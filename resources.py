import os
import pygame
from typing import Optional, Tuple, List, Dict

# Глобальные кэши для избежания повторной загрузки ресурсов
SPRITE_CACHE: Dict[str, pygame.Surface] = {}
FONT_CACHE: Dict[int, pygame.font.Font] = {}
SOUND_CACHE: Dict[str, pygame.mixer.Sound] = {}

def load_sprite(name: str, filename: str, scale: Optional[Tuple[int, int]] = None,
                colorkey: Optional[Tuple[int, int, int]] = None) -> pygame.Surface:
    if name in SPRITE_CACHE:
        return SPRITE_CACHE[name]

    from settings import SPRITES_DIR
    path = os.path.join(SPRITES_DIR, filename)

    try:
        image = pygame.image.load(path).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        if colorkey:
            image.set_colorkey(colorkey)
        SPRITE_CACHE[name] = image
        return image
    except pygame.error as e:
        print(f"Error loading sprite {path}: {e}")
        fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(fallback, (255, 0, 255), (0, 0, 32, 32))
        SPRITE_CACHE[name] = fallback
        return fallback

def load_sprite_sheet(name: str, filename: str, rows: int, cols: int,
                      scale: Optional[Tuple[int, int]] = None) -> List[pygame.Surface]:
    cache_key = f"{name}_{rows}x{cols}"
    if cache_key in SPRITE_CACHE:
        return SPRITE_CACHE[cache_key]

    from settings import SPRITES_DIR
    path = os.path.join(SPRITES_DIR, filename)

    try:
        sheet = pygame.image.load(path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // cols
        frame_height = sheet_height // rows
        frames = []

        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect)
                if scale:
                    frame = pygame.transform.scale(frame, scale)
                frames.append(frame)

        SPRITE_CACHE[cache_key] = frames
        return frames
    except pygame.error as e:
        print(f"Error loading spritesheet {path}: {e}")
        fallback = [pygame.Surface((32, 32), pygame.SRCALPHA) for _ in range(rows * cols)]
        for i, surf in enumerate(fallback):
            pygame.draw.rect(surf, (255, 0, 255), (0, 0, 32, 32))
            pygame.draw.line(surf, (0, 0, 0), (0, 0), (32, 32), 2)
        SPRITE_CACHE[cache_key] = fallback
        return fallback

def get_sprite(name: str) -> Optional[pygame.Surface]:
    return SPRITE_CACHE.get(name)

def load_font(size: int) -> pygame.font.Font:
    if size in FONT_CACHE:
        return FONT_CACHE[size]

    try:
        from settings import CUSTOM_FONT_PATH, DEFAULT_FONT
        if CUSTOM_FONT_PATH and os.path.exists(CUSTOM_FONT_PATH):
            font = pygame.font.Font(CUSTOM_FONT_PATH, size)
        else:
            font = pygame.font.SysFont(DEFAULT_FONT, size)
    except Exception as e:
        print(f"Error loading font: {e}")
        font = pygame.font.SysFont("arial", size)

    FONT_CACHE[size] = font
    return font

def get_font(size: int) -> pygame.font.Font:
    return FONT_CACHE.get(size) or load_font(size)

def load_sound(name: str, filename: str, volume: float = 1.0) -> pygame.mixer.Sound:
    if name in SOUND_CACHE:
        return SOUND_CACHE[name]

    from settings import SOUNDS_DIR
    path = os.path.join(SOUNDS_DIR, filename)

    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        SOUND_CACHE[name] = sound
        return sound
    except pygame.error as e:
        print(f"Error loading sound {path}: {e}")
        fallback = pygame.mixer.Sound(buffer=bytes(8000))
        SOUND_CACHE[name] = fallback
        return fallback

def get_sound(name: str) -> Optional[pygame.mixer.Sound]:
    return SOUND_CACHE.get(name)

def preload_resources():
    try:
        # Предзагружаем шрифты для стабильного отображения интерфейса
        get_font(20)  # HUD
        get_font(24)  # Информационные элементы
        get_font(28)  # Меню улучшений
        get_font(36)  # Основное меню
        get_font(48)  # Заголовки
        get_font(64)  # Акцентный текст
        get_font(72)  # Главный заголовок

        # Загружаем звуки для быстрого отклика на действие
        load_sound("menu_navigate", "menu_navigate.wav", 0.5)
        load_sound("menu_confirm", "menu_confirm.wav", 0.7)
        load_sound("upgrade_success", "upgrade_success.wav", 0.7)
        load_sound("player_damage", "player_damage.wav", 0.7)
        load_sound("skeleton_damage", "skeleton_damage.wav", 0.7)
        load_sound("skeleton_death", "skeleton_death.wav", 0.7)
        load_sound("health", "health.wav", 0.7)
        load_sound("sword_attack", "sword_swing.wav", 0.6)

        # Загружаем спрайты и спрайт-листы для динамики игры
        load_sprite("background", "background.png")
        load_sprite_sheet("player", "player.png", 4, 4, (50, 50))
        load_sprite_sheet("skeleton_walk", "skeleton_walk.png", 1, 13, (50, 70))
        load_sprite_sheet("skeleton_attack", "skeleton_attack.png", 1, 18, (80, 80))
        load_sprite_sheet("skeleton_dead", "skeleton_dead.png", 1, 15, (50, 70))
        load_sprite_sheet("skeleton_hit", "skeleton_hit.png", 1, 8, (50, 70))
        load_sprite_sheet("health", "health_bar.png", 5, 1, (256, 64))
        load_sprite_sheet("slash_effect", "slash_effect.png", 3, 3, (50, 50))
        load_sprite_sheet("meep_moop", "meep_moop.png", 1, 2, (50, 65))
    except Exception as e:
        print(f"Error during resource preloading: {e}")
