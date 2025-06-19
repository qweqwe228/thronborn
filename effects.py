import pygame
import math
from resources import load_sprite_sheet


class SwordSwingEffect(pygame.sprite.Sprite):
    # Карта углов для атаки в разных направлениях (старт, конец, смещение)
    ANGLE_MAP = {
        "right": (-30, 30, (0.5, -0.25)),
        "left": (210, 150, (-0.5, -0.25)),
        "up": (-120, -60, (0, -0.5)),
        "down": (60, 120, (0, 0.5))
    }

    # Преобразования спрайтов для направлений (отражение/поворот)
    ROTATION_MAP = {
        "left": lambda frames: [pygame.transform.flip(f, True, False) for f in frames],
        "up": lambda frames: [pygame.transform.rotate(f, 90) for f in frames],
        "down": lambda frames: [pygame.transform.rotate(f, -90) for f in frames]
    }

    def __init__(self, player, enemy_group, duration=200, scale=(50, 50), arc_radius=60):
        super().__init__()
        # Загрузка кадров анимации удара
        self.frames = load_sprite_sheet("slash_effect", "slash_effect.png", 3, 3, scale)

        # Начальные параметры анимации
        self.frame_index = 0
        self.image = self.frames[0]

        # Ссылки на игрока и врагов
        self.player = player
        self.enemy_group = enemy_group

        # Тайминги анимации
        self.duration = duration
        self.elapsed = 0
        self.last_update = pygame.time.get_ticks()

        # Параметры атаки
        self.arc_radius = arc_radius
        self.damage = player.damage
        self.hit_done = False
        self.damaged_enemies = set()  # Для отслеживания пораженных врагов

        # Настройка траектории атаки
        self.setup_angles()
        self.setup_position()

        # Применение поворота спрайтов для направления атаки
        if player.direction in self.ROTATION_MAP:
            self.frames = self.ROTATION_MAP[player.direction](self.frames)

    def setup_angles(self):
        # Расчет углов атаки на основе направления игрока
        d = self.player.direction
        if d in self.ANGLE_MAP:
            start, end, offset = self.ANGLE_MAP[d]
            # Конвертация градусов в радианы
            self.start_angle = math.radians(start)
            self.end_angle = math.radians(end)
            # Смещение от центра игрока
            self.offset_base = (
                self.player.rect.width * offset[0],
                self.player.rect.height * offset[1]
            )
        # Разница между начальным и конечным углом
        self.delta_angle = self.end_angle - self.start_angle

    def setup_position(self):
        # Расчет стартовой позиции эффекта
        base_x = self.player.rect.centerx + self.offset_base[0]
        base_y = self.player.rect.centery + self.offset_base[1]
        # Позиция на дуге с учетом радиуса и угла
        init_x = base_x + self.arc_radius * math.cos(self.start_angle)
        init_y = base_y + self.arc_radius * math.sin(self.start_angle)
        self.rect = self.image.get_rect(center=(init_x, init_y))

    def update(self):
        # Обновление таймеров
        now = pygame.time.get_ticks()
        dt = now - self.last_update
        self.elapsed += dt

        # Расчет текущего кадра анимации
        frame_duration = self.duration / len(self.frames)
        self.frame_index = min(int(self.elapsed // frame_duration), len(self.frames) - 1)
        self.image = self.frames[self.frame_index]

        # Прогресс анимации от 0 до 1
        t = min(self.elapsed / self.duration, 1)

        # Обновление позиции и проверка попаданий
        self.update_position(t)
        self.check_collisions(t)

        # Завершение анимации
        if t >= 1:
            self.kill()

    def update_position(self, t):
        # Интерполяция позиции по дуге
        base_x = self.player.rect.centerx + self.offset_base[0]
        base_y = self.player.rect.centery + self.offset_base[1]
        # Текущий угол = начальный + % прогресса * разница углов
        current_angle = self.start_angle + self.delta_angle * t
        # Расчет новой позиции
        self.rect.center = (
            base_x + self.arc_radius * math.cos(current_angle),
            base_y + self.arc_radius * math.sin(current_angle)
        )

    def check_collisions(self, t):
        # Проверка попадания только в середине анимации (40-60%)
        if not self.hit_done and 0.4 < t < 0.6:
            # Поиск врагов, пересекающихся с эффектом
            for enemy in pygame.sprite.spritecollide(self, self.enemy_group, False):
                # Нанесение урона только один раз
                if enemy not in self.damaged_enemies:
                    enemy.take_damage(self.damage)
                    self.damaged_enemies.add(enemy)
            self.hit_done = True  # Флаг завершения обработки попадания