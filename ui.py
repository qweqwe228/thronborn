from resources import get_font


def draw_tiled_background(screen, background, camera_offset):
    bg_width, bg_height = background.get_size()

    # Рассчитываем начальную позицию для тайлинга с учётом смещения камеры
    # Это нужно для того, чтобы фон всегда полностью покрывал экран при движении
    start_x = -int(camera_offset.x) % bg_width - bg_width
    start_y = -int(camera_offset.y) % bg_height - bg_height

    # Определяем количество тайлов, необходимых для полного покрытия экрана с запасом
    # Дополнительные тайлы гарантируют отсутствие пустых областей при динамичном перемещении
    tiles_x = (screen.get_width() // bg_width) + 3
    tiles_y = (screen.get_height() // bg_height) + 3

    # Итеративно отрисовываем тайлы по всей области экрана,
    # обеспечивая плавное и непрерывное повторение фонового изображения
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
    # Определяем название уровня исходя из словаря, а при отсутствии элемента возвращаем значение по умолчанию
    return LEVEL_NAMES.get(level, f"Level {level}")


def draw_hud(screen, player, level):
    # Выбираем позицию для основного блока HUD в левом верхнем углу экрана
    x, y = 20, 20

    # Отрисовка иконки здоровья для наглядного отображения состояния игрока
    screen.blit(player.hp_image, (x, y))

    # Создаем текстовое представление здоровья с использованием выбранного шрифта,
    # что улучшает читаемость и понятность информации для игрока
    font = get_font(20)
    health_text = f"{player.max_hits - player.hits}/{player.max_hits}"
    text_surface = font.render(health_text, True, (255, 255, 255))
    # Размещаем числовой индикатор рядом с иконкой для мгновенной оценки состояния.
    screen.blit(text_surface, (x + player.hp_image.get_width() + 10, y + 10))

    # Отрисовываем название уровня под блоком здоровья,
    # чтобы игрок всегда понимал, на каком этапе находится его прохождение
    font = get_font(24)
    level_text = font.render(get_level_text(level), True, (255, 255, 255))
    screen.blit(level_text, (20, y + player.hp_image.get_height() + 10))
