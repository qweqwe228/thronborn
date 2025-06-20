import pygame
import math
from resources import load_sprite_sheet

class SwordSwingEffect(pygame.sprite.Sprite):
    # Карта параметров дуговой атаки для различных направлений
    # Задает начальный и конечный углы, а также смещение эффекта относительно игрока
    ANGLE_MAP = {
        "right": (-30, 30, (0.5, -0.25)),
        "left": (210, 150, (-0.5, -0.25)),
        "up": (-120, -60, (0, -0.5)),
        "down": (60, 120, (0, 0.5))
    }

    # Определяет преобразования кадров для корректного визуального отображения направления атаки
    ROTATION_MAP = {
        "left": lambda frames: [pygame.transform.flip(f, True, False) for f in frames],
        "up": lambda frames: [pygame.transform.rotate(f, 90) for f in frames],
        "down": lambda frames: [pygame.transform.rotate(f, -90) for f in frames]
    }

    def __init__(self, player, enemy_group, duration=200, scale=(50, 50), arc_radius=60):
        super().__init__()
        # Загружаем спрайт-лист удара мечом с нужным масштабом для создания эффекта атаки
        self.frames = load_sprite_sheet("slash_effect", "slash_effect.png", 3, 3, scale)

        # Устанавливаем начальное состояние анимации
        self.frame_index = 0
        self.image = self.frames[0]

        # Сохраняем ссылки на игрока и группу врагов для контроля попадания эффекта
        self.player = player
        self.enemy_group = enemy_group

        # Инициализируем параметры временного контроля эффекта
        self.duration = duration
        self.elapsed = 0
        self.last_update = pygame.time.get_ticks()

        # Настраиваем параметры атаки: радиус дуги и урон берутся из состояния игрока
        self.arc_radius = arc_radius
        self.damage = player.damage
        self.hit_done = False  # Флаг для предотвращения повторного нанесения урона
        self.damaged_enemies = set()  # Сохраняем врагов, уже получивших урон, чтобы не повторять обработку

        # Вычисляем углы дуговой атаки и позицию эффекта относительно игрока
        self.setup_angles()
        self.setup_position()

        # Корректируем кадры анимации, если направление игрока требует поворота
        if player.direction in self.ROTATION_MAP:
            self.frames = self.ROTATION_MAP[player.direction](self.frames)

    def setup_angles(self):
        # Определяем диапазон углов для движения эффекта, чтобы он соответствовал направлению удара
        d = self.player.direction
        if d in self.ANGLE_MAP:
            start, end, offset = self.ANGLE_MAP[d]
            # Переводим градусы в радианы для точности математических расчетов
            self.start_angle = math.radians(start)
            self.end_angle = math.radians(end)
            # Рассчитываем базовое смещение относительно размеров игрока для корректного старта анимации
            self.offset_base = (
                self.player.rect.width * offset[0],
                self.player.rect.height * offset[1]
            )
        # Вычисляем изменение угла, используемое для интерполяции в процессе анимации
        self.delta_angle = self.end_angle - self.start_angle

    def setup_position(self):
        # Вычисляем исходную позицию эффекта на дуге, исходя из центра игрока и базового смещения
        base_x = self.player.rect.centerx + self.offset_base[0]
        base_y = self.player.rect.centery + self.offset_base[1]
        init_x = base_x + self.arc_radius * math.cos(self.start_angle)
        init_y = base_y + self.arc_radius * math.sin(self.start_angle)
        self.rect = self.image.get_rect(center=(init_x, init_y))

    def update(self):
        # Обновляем анимацию эффекта на основе прошедшего времени для достижения плавности движения
        now = pygame.time.get_ticks()
        dt = now - self.last_update
        self.elapsed += dt

        # Рассчитываем текущий кадр в зависимости от прогресса анимации
        frame_duration = self.duration / len(self.frames)
        self.frame_index = min(int(self.elapsed // frame_duration), len(self.frames) - 1)
        self.image = self.frames[self.frame_index]

        # Определяем прогресс анимации от 0 до 1
        t = min(self.elapsed / self.duration, 1)

        # Обновляем позицию эффекта вдоль дуги и проверяем столкновения с врагами
        self.update_position(t)
        self.check_collisions(t)

        # Удаляем объект эффекта, когда анимация полностью завершена
        if t >= 1:
            self.kill()

    def update_position(self, t):
        # Плавно интерполируем положение эффекта по дуге с учетом текущего угла
        base_x = self.player.rect.centerx + self.offset_base[0]
        base_y = self.player.rect.centery + self.offset_base[1]
        current_angle = self.start_angle + self.delta_angle * t
        self.rect.center = (
            base_x + self.arc_radius * math.cos(current_angle),
            base_y + self.arc_radius * math.sin(current_angle)
        )

    def check_collisions(self, t):
        # Наносим урон врагам в промежуточный момент анимации (примерно 40-60%), синхронизируя визуальный эффект и логическую обработку
        if not self.hit_done and 0.4 < t < 0.6:
            for enemy in pygame.sprite.spritecollide(self, self.enemy_group, False):
                if enemy not in self.damaged_enemies:
                    enemy.take_damage(self.damage)
                    self.damaged_enemies.add(enemy)
            self.hit_done = True
