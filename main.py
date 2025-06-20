import sys
import pygame
from settings import FPS, BACKGROUND_COLOR, TITLE, FULLSCREEN
from game_state import GameState
from state_manager import StateManager
from resources import preload_resources


class SoundService:
    def __init__(self, volumes_dict):
        self.sounds = {}
        for name, volume in volumes_dict.items():
            # Используем запасной звук для ситуаций, когда файл не найден,
            # чтобы игра продолжала работать даже при ошибке загрузки
            sound = pygame.mixer.Sound(buffer=bytes(8000))
            try:
                sound = pygame.mixer.Sound(f"assets/sounds/{name}.wav")
                sound.set_volume(volume)
            except:
                print(f"Warning: Sound {name} not found")
            self.sounds[name] = sound

    def play(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        if FULLSCREEN:
            # Переходим в полноэкранный режим для использования нативного разрешения устройства,
            # что обеспечивает оптимальное отображение интерфейса
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = self.screen.get_size()
        else:
            # Выбираем оконный режим с фиксированными размерами, что удобно для отладки и тестирования
            self.screen_width, self.screen_height = 800, 600
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        try:
            preload_resources()
        except Exception as e:
            print(f"Resource preloading error: {e}")

        self.game_state = GameState()
        self.state_manager = StateManager(self)

        self.sound_service = SoundService({
            "menu_navigate": 0.2,
            "menu_confirm": 0.2,
            "upgrade_success": 0.2,
            "sword_attack": 0.2,
            "player_damage": 0.2,
            "skeleton_damage": 0.2,
            "skeleton_death": 0.2,
            "health": 0.2
        })

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    # Завершаем выполнение игры, так как пользователь закрыл окно
                    pygame.quit()
                    sys.exit()

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.screen.fill(BACKGROUND_COLOR)
            self.state_manager.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
