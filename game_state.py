import json
import os
from dataclasses import dataclass, asdict

# Хранение прогресса игрока между игровыми сессиями
@dataclass
class PlayerProgress:
    upgrade_points: int = 0
    speed_upgrades: int = 0
    health_upgrades: int = 0
    damage_upgrades: int = 0
    highest_level: int = 0
    total_points: int = 0

    # Карта соответствий для выбора метода улучшения по типу
    UPGRADE_METHODS = {
        "speed": "buy_speed",
        "health": "buy_health",
        "damage": "buy_damage"
    }

    def buy_upgrade(self, upgrade_type):
        if self.upgrade_points > 0:
            setattr(self, f"{upgrade_type}_upgrades", getattr(self, f"{upgrade_type}_upgrades") + 1)
            self.upgrade_points -= 1
            return True
        return False

    buy_speed = lambda self: self.buy_upgrade("speed")
    buy_health = lambda self: self.buy_upgrade("health")
    buy_damage = lambda self: self.buy_upgrade("damage")

    def get_speed_multiplier(self) -> float:
        # Вычисляем множитель скорости на основе улучшений
        return 1.0 + 0.1 * self.speed_upgrades

    def get_hp_bonus(self) -> int:
        # Вычисляем бонус к здоровью для учета улучшений
        return self.health_upgrades * 2

    def get_damage_bonus(self) -> int:
        # Определяем бонус к урону на основе количества апгрейдов
        return self.damage_upgrades

# Текущая игровая сессия без постоянного сохранения
@dataclass
class GameSession:
    level: int = 1
    player_hp: int = 4
    current_hp: int = 4
    score: int = 0

# Класс, управляющий состоянием игры и сохранением данных
class GameState:
    SAVE_FILE = "save.json"

    def __init__(self):
        self.progress = PlayerProgress()
        self.session = GameSession()
        self.game = None
        self.load()  # Если есть сохраненные данные, загрузим их

    def load(self):  # Загружаем предыдущий прогресс при наличии файла сохранения
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.progress = PlayerProgress(**data.get("progress", {}))
                    self.session = GameSession(**data.get("session", {}))
            except Exception as e:
                print(f"Failed to load save file: {e}")

    def save(self):
        # Сохраняем текущие данные прогресса и сессии в файл
        with open(self.SAVE_FILE, "w") as f:
            json.dump({
                "progress": asdict(self.progress),
                "session": asdict(self.session)
            }, f)

    def start_new_game(self):
        # Запускаем новую игру с перерасчетом максимального здоровья
        max_hp = 4 + self.progress.health_upgrades * 2
        self.session = GameSession(
            level=1,
            player_hp=max_hp,
            current_hp=max_hp,
            score=0
        )
        self.save()

    def complete_level(self):
        # Обновляем уровень и начисляем новые очки для улучшений
        self.session.level += 1
        self.progress.upgrade_points += 1
        self.progress.total_points += 1
        if self.session.level > self.progress.highest_level:
            self.progress.highest_level = self.session.level
        self.save()

    def buy_upgrade(self, upgrade_type):
        # Если есть доступные очки, вызываем метод покупки улучшения для соответствующего типа
        if self.progress.upgrade_points > 0:
            getattr(self.progress, PlayerProgress.UPGRADE_METHODS[upgrade_type])()  # Применяем улучшение
            self.save()
            return True
        return False
