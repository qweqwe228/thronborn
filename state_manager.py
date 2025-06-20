from states import MenuState, PlayState, UpgradeState, GameOverState, VictoryState

class StateManager:
    # Словарь для выбора конструктора состояния по его имени
    STATE_MAP = {
        "menu": lambda self: MenuState(self),
        "play": lambda self: PlayState(self),
        "upgrade": lambda self: UpgradeState(self, self.game.game_state.progress),
        "gameover": lambda self: GameOverState(self, self.game.game_state.session.level),
        "victory": lambda self: VictoryState(self, {"Waves": self.game.game_state.session.level})
    }

    def __init__(self, game):
        self.game = game  # Корневой объект игры для доступа к ресурсам
        # Начальное состояние задано как главное меню
        self.current_state = MenuState(self)

    def change_state(self, state_name):
        # Переключение состояния с использованием словаря STATE_MAP
        constructor = self.STATE_MAP.get(state_name)
        if constructor:
            self.current_state = constructor(self)

    def handle_events(self, events):
        # Передача входных событий текущему состоянию
        self.current_state.handle_events(events)

    def update(self, dt):
        # Обновление логики в зависимости от времени
        self.current_state.update(dt)

    def draw(self, screen):
        # Отрисовка активного состояния на экране
        self.current_state.draw(screen)
