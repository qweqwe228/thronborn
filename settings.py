import os

# Базовые пути к ассетам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
FONT_DIR = os.path.join(ASSETS_DIR, "font")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Настройки экрана
FULLSCREEN = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
TITLE = "Papich's Adventure"
FPS = 60

# Размер мира и плавность камеры
WORLD_WIDTH = 3200
WORLD_HEIGHT = 2400
CAMERA_SMOOTHNESS = 0.1

# Настройки звуков(громкость)
SOUND_VOLUMES = {
    "menu_navigate": 0.2,
    "menu_confirm": 0.2,
    "upgrade_success": 0.2,
    "sword_attack": 0.2,
    "player_damage": 0.2,
    "skeleton_damage": 0.2,
    "skeleton_death": 0.2,
    "health": 0.2
}

# Настройки игрока
PLAYER_BASE_HP = 4
PLAYER_BASE_SPEED = 5
PLAYER_BASE_DAMAGE = 1
PLAYER_ANIMATION_SPEED = 200

# Настройки врагов
ENEMY_SPAWN_MARGIN = 50
ENEMY_BASE_SPEED = 3
ENEMY_BASE_HEALTH = 3
ENEMY_ATTACK_RANGE = 30
ENEMY_DAMAGE_FRAME = 7
ENEMY_FADE_DURATION = 2000
ENEMY_WALK_ANIMATION_SPEED = 50
ENEMY_ATTACK_ANIMATION_SPEED = 25
ENEMY_DEATH_DURATION = 2000
ENEMY_HIT_DURATION = 500

# Настройки предметов
HEALING_ITEM_SPAWN_DISTANCE = 200
HEALING_ITEM_SPEED = 3
HEALING_ITEM_HEAL_AMOUNT = 1
HEALING_ITEM_ANIMATION_SPEED = 200

# Настройки боя
ATTACK_INTERVAL = 500
ATTACK_COOLDOWN = 500

# Настройки системы
CORPSE_CLEANUP_INTERVAL = 1000
CORPSE_DESPAWN_TIME = 5000
WAVE_BASE_ENEMIES = 5
WAVE_ENEMY_INCREMENT = 2 # Доп враги за волну

# Настройки прокачки
SPEED_UPGRADE_MULTIPLIER = 0.1
HEALTH_UPGRADE_BONUS = 2
DAMAGE_UPGRADE_BONUS = 1

# Цвета для меню
MENU_TEXT_COLOR = (255, 255, 255)
MENU_SELECTED_COLOR = (0, 255, 0)
MENU_HOVER_COLOR = (200, 255, 200)
PAUSE_BG_COLOR = (0, 0, 0, 180)

UI_PADDING = 20 # Отступ
UI_ELEMENT_SPACING = 10
UI_FONT_SIZE_SMALL = 20
UI_FONT_SIZE_MEDIUM = 24
UI_FONT_SIZE_LARGE = 36
UI_FONT_SIZE_TITLE = 48

# Цвета интерфейса
UI_BACKGROUND_COLOR = (50, 50, 70)
UI_TEXT_COLOR = (255, 255, 255)
UI_HIGHLIGHT_COLOR = (0, 255, 0)
UI_STAT_COLOR_SPEED = (100, 255, 100)
UI_STAT_COLOR_HEALTH = (255, 100, 100)
UI_STAT_COLOR_DAMAGE = (200, 100, 255)

# Настройки шрифтов
CUSTOM_FONT_PATH = os.path.join(FONT_DIR, "OldeTome.ttf")
DEFAULT_FONT = "arial"