from dataclasses import dataclass


@dataclass
class ProgressSystem:
    upgrade_points: int = 0  # Счётчик очков апгрейда — отражает накопленный потенциал для улучшений
    speed_upgrades: int = 0  # Количество улучшений скорости — влияет на быстроту и динамику движения
    health_upgrades: int = 0  # Количество улучшений здоровья — повышает устойчивость и выживаемость
    damage_upgrades: int = 0  # Количество улучшений атаки — усиливает урон и эффективность в бою

    def add_points(self, points: int = 1) -> None:
        # Функция аккумулирует очки для будущих улучшений, что позволяет динамично масштабировать возможности игрока
        self.upgrade_points += points
        print("Added points, now:", self.upgrade_points)

    def buy_speed(self) -> bool:
        # При наличии очков происходит покупка улучшения скорости, что меняет темп геймплея
        if self.upgrade_points > 0:
            self.upgrade_points -= 1
            self.speed_upgrades += 1
            print("Bought speed upgrade. Speed upgrades:", self.speed_upgrades,
                  "Remaining points:", self.upgrade_points)
            return True
        return False

    def buy_health(self) -> bool:
        # Улучшение здоровья применяется, если доступны очки — это увеличивает шансы выжить в сложных ситуациях
        if self.upgrade_points > 0:
            self.upgrade_points -= 1
            self.health_upgrades += 1
            print("Bought health upgrade. Health upgrades:", self.health_upgrades,
                  "Remaining points:", self.upgrade_points)
            return True
        return False

    def buy_damage(self) -> bool:
        # Улучшение атаки активируется при наличии очков, что повышает способность наносить критический урон
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
