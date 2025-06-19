import random
from settings import WORLD_WIDTH, WORLD_HEIGHT, ENEMY_SPAWN_MARGIN


def generate_wave(level, player, factory):
    # Расчет количества врагов: база + 2 за каждый уровень
    enemy_count = 5 + 2 * level
    enemies = []

    # Увеличенная зона спавна
    spawn_margin = ENEMY_SPAWN_MARGIN * 2

    for _ in range(enemy_count):
        # Поиск валидной позиции для спавна
        while True:
            # Случайные координаты в пределах игрового мира (с отступом)
            x = random.randint(spawn_margin, WORLD_WIDTH - spawn_margin)
            y = random.randint(spawn_margin, WORLD_HEIGHT - spawn_margin)

            # Расчет расстояния до игрока
            distance_to_player = ((x - player.rect.centerx) ** 2 +
                                  (y - player.rect.centery) ** 2) ** 0.5

            # Проверка минимальной дистанции (500 пикселей)
            if distance_to_player > 500:
                break  # Позиция подходит

        # Создание врага через фабрику и добавление в список
        enemies.append(factory.create_enemy((x, y), player))

    return enemies  # Возврат сгенерированной волны