import pygame


class Camera:
    def __init__(self, screen_width, screen_height):
        # Инициализация камеры с размером экрана
        self.offset = pygame.Vector2(0, 0)  # Смещение камеры
        self.screen_width = screen_width    # Ширина игрового экрана
        self.screen_height = screen_height  # Высота игрового экрана
        self.world_width = 0                # Ширина игрового мира (устанавливается позже)
        self.world_height = 0               # Высота игрового мира

    def set_world_size(self, width, height):
        # Установка размеров игрового мира
        self.world_width = width
        self.world_height = height

    def update(self, target_rect):
        # Обновление позиции камеры с плавным слежением за целью
        # Расчет желаемой позиции камеры (центрированной на цели)
        desired_x = max(0, min(target_rect.centerx - self.screen_width // 2,
                               self.world_width - self.screen_width))
        desired_y = max(0, min(target_rect.centery - self.screen_height // 2,
                               self.world_height - self.screen_height))

        # Плавное перемещение камеры (10% от расстояния до цели)
        self.offset.x += (desired_x - self.offset.x) * 0.1
        self.offset.y += (desired_y - self.offset.y) * 0.1

    def apply(self, rect):
        # Преобразование мировых координат в экранные
        return rect.move(-self.offset.x, -self.offset.y)

    def is_visible(self, rect, buffer=0):
        # Проверка видимости объекта на экране
        # Создаем область видимости камеры с буфером
        visible_rect = pygame.Rect(
            self.offset.x - buffer,
            self.offset.y - buffer,
            self.screen_width + 2 * buffer,
            self.screen_height + 2 * buffer
        )
        # Проверка пересечения объекта с видимой областью
        return rect.colliderect(visible_rect)