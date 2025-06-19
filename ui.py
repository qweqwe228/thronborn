from resources import get_font


def draw_tiled_background(screen, background, camera_offset):
    bg_width, bg_height = background.get_size()

    # Расчет стартовой позиции для тайлинга
    start_x = -int(camera_offset.x) % bg_width - bg_width
    start_y = -int(camera_offset.y) % bg_height - bg_height

    # Количество тайлов для покрытия экрана + запас
    tiles_x = (screen.get_width() // bg_width) + 3
    tiles_y = (screen.get_height() // bg_height) + 3

    # Отрисовка сетки тайлов
    for x in range(start_x, start_x + tiles_x * bg_width, bg_width):
        for y in range(start_y, start_y + tiles_y * bg_height, bg_height):
            screen.blit(background, (x, y))


LEVEL_NAMES = {
    1: "The First Level",
    2: "The Second Level",
    3: "The Third Level",
    4: "The Fourth Level",
    5: "The Fifth Level",
    6: "The Sixth Level",
    7: "The Seventh Level",
    8: "The Eighth Level",
    9: "The Ninth Level",
    10: "The Final Level"
}


def get_level_text(level):
    return LEVEL_NAMES.get(level, f"Level {level}")  # Дефолт для уровней >10


def draw_hud(screen, player, level):
    # Позиция основного блока HUD
    x, y = 20, 20

    # Иконка здоровья
    screen.blit(player.hp_image, (x, y))

    # Цифровое отображение здоровья
    font = get_font(20)
    health_text = f"{player.max_hits - player.hits}/{player.max_hits}"
    text_surface = font.render(health_text, True, (255, 255, 255))
    # Позиция справа от иконки
    screen.blit(text_surface, (x + player.hp_image.get_width() + 10, y + 10))

    # Название уровня под блоком здоровья
    font = get_font(24)
    level_text = font.render(get_level_text(level), True, (255, 255, 255))
    screen.blit(level_text, (20, y + player.hp_image.get_height() + 10))