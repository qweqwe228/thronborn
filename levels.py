import random
from settings import WORLD_WIDTH, WORLD_HEIGHT, ENEMY_SPAWN_MARGIN


def generate_wave(level, player, factory):
    # Определяем число врагов с повышением сложности на каждом уровне
    enemy_count = 5 + 2 * level
    enemies = []

    # Расширяем зону спавна для повышения справедливости игры
    spawn_margin = ENEMY_SPAWN_MARGIN * 2

    for _ in range(enemy_count):
        # Ищем допустимую позицию для появления врага
        while True:
            # Генерируем случайные координаты в пределах мира с учетом отступа
            x = random.randint(spawn_margin, WORLD_WIDTH - spawn_margin)
            y = random.randint(spawn_margin, WORLD_HEIGHT - spawn_margin)

            # Вычисляем расстояние до центра игрока чтобы избежать мгновенного столкновения
            distance_to_player = ((x - player.rect.centerx) ** 2 +
                                  (y - player.rect.centery) ** 2) ** 0.5

            # Принимаем координаты если расстояние превышает 500 пикселей
            if distance_to_player > 500:
                break  # Позиция удовлетворяет условию

        # Создаем врага через фабрику для поддержки модульности спавна
        enemies.append(factory.create_enemy((x, y), player))

    return enemies  # Возвращаем список сгенерированной волны врагов
