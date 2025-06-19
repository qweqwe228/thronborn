# progress.py
from dataclasses import dataclass


@dataclass
class ProgressSystem:
    upgrade_points: int = 0  # Очки, заработанные для прокачки
    speed_upgrades: int = 0  # Количество купленных улучшений скорости
    health_upgrades: int = 0  # Количество купленных улучшений здоровья
    damage_upgrades: int = 0  # Новый параметр

    def add_points(self, points: int = 1) -> None:
        self.upgrade_points += points
        print("Added points, now:", self.upgrade_points)

    def buy_speed(self) -> bool:
        if self.upgrade_points > 0:
            self.upgrade_points -= 1
            self.speed_upgrades += 1
            print("Bought speed upgrade. Speed upgrades:", self.speed_upgrades,
                  "Remaining points:", self.upgrade_points)
            return True
        return False

    def buy_health(self) -> bool:
        if self.upgrade_points > 0:
            self.upgrade_points -= 1
            self.health_upgrades += 1
            print("Bought health upgrade. Health upgrades:", self.health_upgrades,
                  "Remaining points:", self.upgrade_points)
            return True
        return False

    def buy_damage(self) -> bool:
        if self.upgrade_points > 0:
            self.upgrade_points -= 1
            self.damage_upgrades += 1
            print("Bought damage upgrade. Damage upgrades:", self.damage_upgrades,
                  "Remaining points:", self.upgrade_points)
            return True
        return False

    def get_speed_multiplier(self) -> float:
        return 1.0 + 0.1 * self.speed_upgrades

    def get_hp_bonus(self) -> int:
        return self.health_upgrades * 1

    def get_damage_bonus(self) -> int:
        return self.damage_upgrades * 1