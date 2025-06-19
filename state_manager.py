from states import MenuState, PlayState, UpgradeState, GameOverState, VictoryState

class StateManager:
    # Словарь для создания состояний по имени
    STATE_MAP = {
        "menu": lambda self: MenuState(self),
        "play": lambda self: PlayState(self),
        "upgrade": lambda self: UpgradeState(
            self,
            self.game.game_state.progress  # Прогресс игрока
        ),
        "gameover": lambda self: GameOverState(
            self,
            self.game.game_state.session.level  # Текущий уровень
        ),
        "victory": lambda self: VictoryState(
            self,
            {"Waves": self.game.game_state.session.level}  # Статистика побед
        )
    }

    def __init__(self, game):
        self.game = game  # Ссылка на главный объект игры
        # Начальное состояние - меню
        self.current_state = MenuState(self)

    def change_state(self, state_name):
        # Получаем конструктор состояния из словаря
        constructor = self.STATE_MAP.get(state_name)
        if constructor:
            # Создаем новое состояние
            self.current_state = constructor(self)

    # Методы для передачи событий текущему состоянию
    def handle_events(self, events):
        self.current_state.handle_events(events)

    def update(self, dt):
        self.current_state.update(dt)

    def draw(self, screen):
        self.current_state.draw(screen)