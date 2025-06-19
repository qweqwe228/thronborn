import json
import os
from dataclasses import dataclass, asdict

# Прогресс игрока между сессиями
@dataclass
class PlayerProgress:
    upgrade_points: int = 0
    speed_upgrades: int = 0
    health_upgrades: int = 0
    damage_upgrades: int = 0
    highest_level: int = 0
    total_points: int = 0

    # Соответствие типов улучшений и методов
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
        return 1.0 + 0.1 * self.speed_upgrades

    def get_hp_bonus(self) -> int:
        return self.health_upgrades * 2

    def get_damage_bonus(self) -> int:
        return self.damage_upgrades

# Текущая игровая сессия(не сохраняется)
@dataclass
class GameSession:
    level: int = 1
    player_hp: int = 4
    current_hp: int = 4
    score: int = 0

# Главный класс управления состоянием игры
class GameState:
    SAVE_FILE = "save.json"

    def __init__(self):
        self.progress = PlayerProgress()
        self.session = GameSession()
        self.game = None
        self.load()

    def load(self): # Загружает прогресс из файла если он существует
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.progress = PlayerProgress(**data.get("progress", {}))
                    self.session = GameSession(**data.get("session", {}))
            except Exception as e:
                print(f"Failed to load save file: {e}")

    def save(self):
        with open(self.SAVE_FILE, "w") as f:
            json.dump({
                "progress": asdict(self.progress),
                "session": asdict(self.session)
            }, f)

    def start_new_game(self):
        max_hp = 4 + self.progress.health_upgrades * 2
        self.session = GameSession(
            level=1,
            player_hp=max_hp,
            current_hp=max_hp,
            score=0
        )
        self.save()

    def complete_level(self):
        self.session.level += 1
        self.progress.upgrade_points += 1
        self.progress.total_points += 1
        if self.session.level > self.progress.highest_level:
            self.progress.highest_level = self.session.level
        self.save()

    def buy_upgrade(self, upgrade_type):
        if self.progress.upgrade_points > 0:
            getattr(self.progress, PlayerProgress.UPGRADE_METHODS[upgrade_type])() # Вызываем соответствующий метод покупки
            self.save()
            return True
        return False