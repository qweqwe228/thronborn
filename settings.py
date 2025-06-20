import os

# Каталог проекта – базовый путь для ассетов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Пути к ресурсам – ассеты, спрайты, шрифты и звуки
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
FONT_DIR = os.path.join(ASSETS_DIR, "font")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Параметры экрана – режим, размеры, фон и заголовок
FULLSCREEN = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
TITLE = "Papich's Adventure"
FPS = 60

# Габариты игрового мира и плавность перемещения камеры
WORLD_WIDTH = 3200
WORLD_HEIGHT = 2400
CAMERA_SMOOTHNESS = 0.1

# Громкость звуков – настройка аудиоэффектов
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

# Характеристики игрока – базовые параметры силы, скорости и здоровья
PLAYER_BASE_HP = 4
PLAYER_BASE_SPEED = 5
PLAYER_BASE_DAMAGE = 1
PLAYER_ANIMATION_SPEED = 200

# Конфигурация врагов – базовые показатели и визуальные эффекты
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

# Параметры лечения – спавн, скорость движения и величина исцеления
HEALING_ITEM_SPAWN_DISTANCE = 200
HEALING_ITEM_SPEED = 3
HEALING_ITEM_HEAL_AMOUNT = 1
HEALING_ITEM_ANIMATION_SPEED = 200

# Настройки боя – интервалы между атаками для балансировки
ATTACK_INTERVAL = 500
ATTACK_COOLDOWN = 500

# Системные настройки – интервалы очистки и генерация волн противников
CORPSE_CLEANUP_INTERVAL = 1000
CORPSE_DESPAWN_TIME = 5000
WAVE_BASE_ENEMIES = 5
WAVE_ENEMY_INCREMENT = 2  # Дополнительные враги за волну

# Параметры прокачки – коэффициенты улучшений характеристик
SPEED_UPGRADE_MULTIPLIER = 0.1
HEALTH_UPGRADE_BONUS = 2
DAMAGE_UPGRADE_BONUS = 1

# Цветовая палитра для меню – базовые оттенки текста и фона
MENU_TEXT_COLOR = (255, 255, 255)
MENU_SELECTED_COLOR = (0, 255, 0)
MENU_HOVER_COLOR = (200, 255, 200)
PAUSE_BG_COLOR = (0, 0, 0, 180)

# Интерфейс – отступы, расстояния и размеры шрифтов
UI_PADDING = 20  # Общее поле интерфейса
UI_ELEMENT_SPACING = 10
UI_FONT_SIZE_SMALL = 20
UI_FONT_SIZE_MEDIUM = 24
UI_FONT_SIZE_LARGE = 36
UI_FONT_SIZE_TITLE = 48

# Цвета интерфейса – фон, текст и акценты для информационных блоков
UI_BACKGROUND_COLOR = (50, 50, 70)
UI_TEXT_COLOR = (255, 255, 255)
UI_HIGHLIGHT_COLOR = (0, 255, 0)
UI_STAT_COLOR_SPEED = (100, 255, 100)
UI_STAT_COLOR_HEALTH = (255, 100, 100)
UI_STAT_COLOR_DAMAGE = (200, 100, 255)

# Шрифты – выбор между кастомным и системным
CUSTOM_FONT_PATH = os.path.join(FONT_DIR, "OldeTome.ttf")
DEFAULT_FONT = "arial"
