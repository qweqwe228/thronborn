import pygame
import random
import math
from resources import load_sprite_sheet, load_sprite
from settings import WORLD_WIDTH, WORLD_HEIGHT, PLAYER_BASE_HP, ENEMY_SPAWN_MARGIN

# Конфигурация анимационных диапазонов для игрока по направлениям
PLAYER_ANIMATIONS = {
    "down": slice(0, 4),
    "left": slice(4, 8),
    "right": slice(8, 12),
    "up": slice(12, 16)
}

# Централизованная фабрика игровых объектов для единообразного создания сущностей
class GameObjectFactory:
    def __init__(self, sound_service):
        # Инициализация с передачей сервиса звука для использования аудиоэффектов
        self.sound_service = sound_service

    def create_player(self, pos, game_state):
        # Создает объект игрока, связывая его с текущим игровым состоянием
        return Player(pos, game_state, self.sound_service)

    def create_enemy(self, pos, target):
        # Создает врага, целенаправленно ориентированного на заданную цель
        return Enemy(pos, target, self.sound_service)

    def create_healing_item(self, pos, player):
        # Создает аптечку для восстановления здоровья, привязанную к игроку
        return HealingItem(pos, player)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, game_state, sound_service):
        super().__init__()
        # Связываем объект игрока с игровым состоянием и звуковым сервисом
        self.game_state = game_state
        self.sound_service = sound_service

        # Задаем базовые характеристики игрока, используемые при обновлении статов
        self.base_speed = 5
        self.base_max_hits = PLAYER_BASE_HP
        self.base_damage = 1
        self.hits = 0
        self.update_stats()

        # Загружаем анимационные кадры и устанавливаем начальное состояние
        self.animations = self.load_animations((50, 50))
        self.direction = "down"
        self.current_animation = self.animations[self.direction]
        self.frame_index = 0
        self.image = self.current_animation[0]
        self.rect = self.image.get_rect(center=pos)
        self.animation_speed = 200
        self.last_update = pygame.time.get_ticks()

        # Загружаем изображения для индикатора здоровья и отображаем текущий статус
        self.health_bar_images = load_sprite_sheet("health", "health_bar.png", 5, 1, (256, 64))
        self.update_hp_bar()

    def load_animations(self, scale):
        # Загружает спрайт-лист игрока и распределяет кадры по направлениям движения
        frames = load_sprite_sheet("player", "player.png", 4, 4, scale)
        return {d: frames[s] for d, s in PLAYER_ANIMATIONS.items()}

    def update_hp_bar(self):
        # Пересчитывает изображение индикатора здоровья в зависимости от полученного урона
        total_images = len(self.health_bar_images)
        if total_images == 0:
            return

        progress = min(self.hits / max(self.max_hits, 1), 1.0)
        index = min(int(progress * (total_images - 1)), total_images - 1)
        self.current_hp_image = self.health_bar_images[index]

    @property
    def hp_image(self):
        # Возвращает текущее изображение для индикации здоровья игрока
        return self.current_hp_image

    def take_damage(self, damage=1):
        # Обрабатывает урон игрока и обновляет индикатор здоровья; уничтожает объект при полном исчерпании здоровья
        self.hits = min(self.hits + damage, self.max_hits)
        self.update_hp_bar()
        self.sound_service.play("player_damage")
        if self.hits >= self.max_hits:
            self.kill()

    def heal(self, amount=1):
        # Восстанавливает здоровье, уменьшая накопленный урон
        self.hits = max(0, self.hits - amount)
        self.update_hp_bar()

    def update_stats(self):
        # Пересчитывает параметры игрока с учетом улучшений, накопленных в прогрессе
        self.speed = self.base_speed * (1.0 + 0.1 * self.game_state.progress.speed_upgrades)
        self.max_hits = self.base_max_hits + self.game_state.progress.health_upgrades
        self.damage = self.base_damage + self.game_state.progress.damage_upgrades
        if hasattr(self, 'health_bar_images'):
            self.update_hp_bar()

    def update(self):
        # Обрабатывает ввод и перемещение игрока, обновляя анимацию и обеспечивая цикличность игрового поля
        keys = pygame.key.get_pressed()
        dx = dy = 0
        new_direction = self.direction
        is_moving = False

        if keys[pygame.K_LEFT]:
            dx -= self.speed
            new_direction = "left"
            is_moving = True
        if keys[pygame.K_RIGHT]:
            dx += self.speed
            new_direction = "right"
            is_moving = True
        if keys[pygame.K_UP]:
            dy -= self.speed
            new_direction = "up"
            is_moving = True
        if keys[pygame.K_DOWN]:
            dy += self.speed
            new_direction = "down"
            is_moving = True

        self.rect.x += dx
        self.rect.y += dy

        # Обеспечивает цикличность мира, переводя объект на противоположную сторону при выходе за границы
        if self.rect.right < 0:
            self.rect.left = WORLD_WIDTH
        elif self.rect.left > WORLD_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = WORLD_HEIGHT
        elif self.rect.top > WORLD_HEIGHT:
            self.rect.bottom = 0

        if new_direction != self.direction:
            self.direction = new_direction
            self.current_animation = self.animations[self.direction]
            self.frame_index = 0

        now = pygame.time.get_ticks()
        if not is_moving:
            self.frame_index = 0
        elif now - self.last_update > self.animation_speed:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)

        self.image = self.current_animation[self.frame_index]

    def attack(self, effects_group, enemy_group):
        # Запускает эффект атаки мечом и воспроизводит соответствующий звуковой сигнал
        from effects import SwordSwingEffect
        effects_group.add(SwordSwingEffect(self, enemy_group, 200, (50, 50), 15))
        self.sound_service.play("sword_attack")


class Enemy(pygame.sprite.Sprite):
    STATE_WALK = "walking"
    STATE_ATTACK = "attacking"
    STATE_HIT = "hit"
    STATE_DYING = "dying"

    def __init__(self, pos, target, sound_service):
        super().__init__()
        # Загружает набор анимаций для различных состояний врага
        self.walk_animations = load_sprite_sheet("skeleton_walk", "skeleton_walk.png", 1, 13, (50, 70))
        self.attack_animations = load_sprite_sheet("skeleton_attack", "skeleton_attack.png", 1, 18, (80, 80))
        self.death_animations = load_sprite_sheet("skeleton_dead", "skeleton_dead.png", 1, 15, (50, 70))
        self.hit_animations = load_sprite_sheet("skeleton_hit", "skeleton_hit.png", 1, 8, (50, 70))
        self.state = self.STATE_WALK
        self.frame_index = 0
        self.image = self.walk_animations[0]
        self.rect = self.image.get_rect(center=pos)
        self.last_update = pygame.time.get_ticks()
        self.speed = 3
        self.target = target
        self.health = 3
        self.attack_range = 30
        self.damage_frame = 7
        self.attacked = False
        self.death_animation_completed = False
        self.death_start_time = None
        self.death_completed_time = None
        self.fade_start_time = None
        self.fade_duration = 2000
        self.alpha = 255
        self.hit_start_time = None
        self.sound_service = sound_service

    def update(self):
        # Основной цикл обновления состояния врага, выбирающий поведение в зависимости от дистанции до цели
        now = pygame.time.get_ticks()

        if self.state == self.STATE_DYING:
            self.handle_death_state(now)
            return

        if self.state == self.STATE_HIT:
            self.handle_hit_state(now)
            return

        distance = math.hypot(
            self.target.rect.centerx - self.rect.centerx,
            self.target.rect.centery - self.rect.centery
        )

        self.state = self.STATE_ATTACK if distance < self.attack_range else self.STATE_WALK

        if self.state == self.STATE_WALK:
            self.handle_walk_state(now, distance)
        elif self.state == self.STATE_ATTACK:
            self.handle_attack_state(now)

    def handle_death_state(self, now):
        # Отвечает за анимацию смерти, включая затухание и окончательное исчезновение врага
        elapsed = now - self.death_start_time
        frame_duration = 2000 / len(self.death_animations)
        self.frame_index = min(int(elapsed / frame_duration), len(self.death_animations) - 1)
        self.image = self.death_animations[self.frame_index]

        if self.frame_index == len(self.death_animations) - 1:
            self.death_animation_completed = True
            if self.death_completed_time is None:
                self.death_completed_time = now
                self.fade_start_time = now

        if self.fade_start_time:
            fade_elapsed = now - self.fade_start_time
            self.alpha = max(0, 255 - int(255 * min(1.0, fade_elapsed / self.fade_duration)))
            self.image.set_alpha(self.alpha)

    def handle_hit_state(self, now):
        # Обрабатывает ситуацию, когда враг получает урон, переключая анимацию при кратковременном эффекте попадания
        elapsed = now - self.hit_start_time
        frame_duration = 500 / len(self.hit_animations)
        self.frame_index = min(int(elapsed / frame_duration), len(self.hit_animations))

        if self.frame_index >= len(self.hit_animations):
            self.state = self.STATE_WALK
            self.frame_index = 0
            self.image = self.walk_animations[0]
        else:
            self.image = self.hit_animations[self.frame_index]
            self.mirror_image()

    def handle_walk_state(self, now, distance):
        # Управляет движением врага к цели с регулярной сменой кадров и проверкой границ игрового мира
        if now - self.last_update > 50:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.walk_animations)
            self.image = self.walk_animations[self.frame_index]
            self.mirror_image()

        if distance > 0:
            move_x = int((self.target.rect.centerx - self.rect.centerx) / distance * self.speed)
            move_y = int((self.target.rect.centery - self.rect.centery) / distance * self.speed)

            self.rect.x += move_x
            self.rect.y += move_y

            if self.rect.right < 0:
                self.rect.left = WORLD_WIDTH
            elif self.rect.left > WORLD_WIDTH:
                self.rect.right = 0
            if self.rect.bottom < 0:
                self.rect.top = WORLD_HEIGHT
            elif self.rect.top > WORLD_HEIGHT:
                self.rect.bottom = 0

    def handle_attack_state(self, now):
        # Выполняет анимацию атаки; в момент удара проверяет коллизию с целью и предотвращает повторное срабатывание
        if now - self.last_update > 25:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index == self.damage_frame and not self.attacked:
                if self.rect.colliderect(self.target.rect):
                    self.target.take_damage(1)
                self.attacked = True

            if self.frame_index >= len(self.attack_animations):
                self.frame_index = 0
                self.state = self.STATE_WALK
                self.attacked = False
                self.image = self.walk_animations[0]
            else:
                self.image = self.attack_animations[self.frame_index]
                self.mirror_image()

    def mirror_image(self):
        # Отражает изображение врага для корректного отображения направления движения
        if self.target.rect.centerx < self.rect.centerx:
            self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, amount=1):
        # Обрабатывает получение урона врагом, переходя в соответствующее состояние анимации
        if self.state == self.STATE_DYING:
            return

        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.state = self.STATE_DYING
            self.frame_index = 0
            self.death_start_time = pygame.time.get_ticks()
            self.death_animation_completed = False
            self.death_completed_time = None
            self.fade_start_time = None
            self.alpha = 255
            self.sound_service.play("skeleton_death")
        else:
            self.state = self.STATE_HIT
            self.frame_index = 0
            self.hit_start_time = pygame.time.get_ticks()
            self.sound_service.play("skeleton_damage")


class HealingItem(pygame.sprite.Sprite):
    def __init__(self, pos, player, speed=3):
        super().__init__()
        # Инициализирует аптечку с анимацией и случайной целью движения в пределах мира
        self.animations = load_sprite_sheet("meep_moop", "meep_moop.png", 1, 2, (50, 65))
        self.image = self.animations[0]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.player = player
        self.speed = speed
        self.heal_amount = 1
        self.dest = pygame.Vector2(
            random.randint(50, WORLD_WIDTH - 50),
            random.randint(50, WORLD_HEIGHT - 50)
        )

    def update(self):
        # Меняет направление движения, если достигнута указанная цель, и мигает для привлечения внимания
        if self.pos.distance_to(self.dest) < 5:
            self.dest = pygame.Vector2(
                random.randint(50, WORLD_WIDTH - 50),
                random.randint(50, WORLD_HEIGHT - 50))

        move_vec = (self.dest - self.pos).normalize() * self.speed
        self.pos += move_vec
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.image = self.animations[0] if pygame.time.get_ticks() % 200 < 100 else self.animations[1]


def resolve_collisions(enemies):
    # Корректирует позиционирование врагов, предотвращая их наложение при столкновениях
    enemy_list = list(enemies)

    for i in range(len(enemy_list)):
        for j in range(i + 1, len(enemy_list)):
            e1, e2 = enemy_list[i], enemy_list[j]

            # Пропускает обработку, если враг умирает или прямого столкновения не происходит
            if e1.state == "dying" or e2.state == "dying" or not e1.rect.colliderect(e2.rect):
                continue

            dx = e2.rect.centerx - e1.rect.centerx
            dy = e2.rect.centery - e1.rect.centery

            # Рассчитывает расстояние между центрами для определения степени перекрытия
            dist = max(1, math.hypot(dx, dy))
            overlap = (e1.rect.width / 2 + e2.rect.width / 2) - dist

            if overlap > 0:
                # Вычисляет нормализованный вектор смещения для устранения наложения объектов
                shift_x = (dx / dist) * (overlap / 2)
                shift_y = (dy / dist) * (overlap / 2)

                e1.rect.x -= shift_x  # Смещает первого врага назад от центра столкновения
                e1.rect.y -= shift_y

                e2.rect.x += shift_x  # Смещает второго врага вперед в противоположном направлении
                e2.rect.y += shift_y
