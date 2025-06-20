import pygame
from settings import CAMERA_SMOOTHNESS, WORLD_WIDTH, WORLD_HEIGHT

class Camera:
    def __init__(self, width, height):
        # Инициализируем камеру с размерами экрана для задания области обзора
        self.width = width
        self.height = height
        # Начальное смещение камеры, используем для преобразования мировых координат в экранные
        self.offset = pygame.Vector2(0, 0)
        # Определяем пределы игрового мира для ограничения перемещения камеры
        self.world_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    def set_world_size(self, world_width, world_height):
        # Задаем размеры мира, чтобы камера оставалась в рамках игрового поля
        self.world_rect.width = world_width
        self.world_rect.height = world_height

    def apply(self, rect):
        # Преобразуем координаты объекта, учитывая текущее смещение камеры, для корректной отрисовки на экране
        return rect.move(self.offset.x, self.offset.y)

    def update(self, target_rect):
        # Вычисляем идеальное положение камеры: цель должна оказаться по центру экрана
        ideal_x = -target_rect.centerx + self.width // 2
        ideal_y = -target_rect.centery + self.height // 2

        # Ограничиваем смещение, чтобы камера не выходила за границы игрового мира
        ideal_x = min(0, ideal_x)
        ideal_y = min(0, ideal_y)
        ideal_x = max(-(self.world_rect.width - self.width), ideal_x)
        ideal_y = max(-(self.world_rect.height - self.height), ideal_y)

        # Плавно приближаем текущее смещение к рассчитанному идеальному положению
        self.offset.x += (ideal_x - self.offset.x) * CAMERA_SMOOTHNESS
        self.offset.y += (ideal_y - self.offset.y) * CAMERA_SMOOTHNESS

    def is_visible(self, rect, buffer=0):
        # Формируем область видимости с дополнительным запасом (буфер) для оптимизации отрисовки объектов
        view_rect = pygame.Rect(-buffer, -buffer, self.width + 2 * buffer, self.height + 2 * buffer)
        temp_rect = rect.move(self.offset.x, self.offset.y)
        # Проверяем пересечение объекта с областью видимости экрана
        return view_rect.colliderect(temp_rect)
