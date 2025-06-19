import pygame
import random
from settings import (
    TITLE, BACKGROUND_COLOR,
    WORLD_WIDTH, WORLD_HEIGHT, HEALING_ITEM_SPAWN_DISTANCE,
    ATTACK_COOLDOWN, PAUSE_BG_COLOR, MENU_TEXT_COLOR,
    MENU_SELECTED_COLOR, MENU_HOVER_COLOR
)
from resources import load_sprite, get_font
from camera import Camera
from levels import generate_wave
from ui import draw_hud, draw_tiled_background
from entities import resolve_collisions, GameObjectFactory
from game_state import PlayerProgress


# Базовый класс для всех игровых состояний
class BaseState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.game = state_manager.game
        self.screen_width = self.game.screen.get_width()
        self.screen_height = self.game.screen.get_height()

    # Пустые методы для переопределения в дочерних классах
    def handle_events(self, events):
        pass

    def update(self, dt: int):
        pass

    def draw(self, screen: pygame.Surface):
        pass

    # Вспомогательный метод для звуков
    def play_sound(self, sound_name):
        self.game.sound_service.play(sound_name)


# Состояние главного меню
class MenuState(BaseState):
    OPTIONS = ["New Game", "Upgrade", "Quit"]

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.selected = 0  # Выбранный пункт меню
        # Шрифты для текста
        self.title_font = get_font(48)
        self.option_font = get_font(36)
        self.option_rects = []  # Для кликабельных зон

        # Позиции пунктов меню
        self.OPTION_POSITIONS = {
            "New Game": (self.screen_width // 2, self.screen_height // 2 - 30),
            "Upgrade": (self.screen_width // 2, self.screen_height // 2),
            "Quit": (self.screen_width // 2, self.screen_height // 2 + 35)
        }

    def handle_events(self, events):
        for event in events:
            # Клавиатура
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.OPTIONS)
                    self.play_sound("menu_navigate")
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.OPTIONS)
                    self.play_sound("menu_navigate")
                elif event.key == pygame.K_RETURN:
                    self.play_sound("menu_confirm")
                    self.handle_option_select()
            # Мышь
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.play_sound("menu_confirm")
                self.handle_mouse_click()

    def handle_mouse_motion(self, mouse_pos):
        # Подсветка при наведении
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break

    def handle_option_select(self):
        # Обработка выбора пункта
        option = self.OPTIONS[self.selected]
        if option == "New Game":
            self.start_new_game()
        elif option == "Upgrade":
            self.state_manager.change_state("upgrade")
        elif option == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_mouse_click(self):
        # Клик по пункту меню
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                self.handle_option_select()
                break

    def start_new_game(self):
        # Запуск новой игры
        self.game.game_state.start_new_game()
        self.state_manager.change_state("play")

    def update(self, dt):
        pass  # Нет логики обновления

    def draw(self, screen):
        # Отрисовка меню
        screen.fill(BACKGROUND_COLOR)

        # Заголовок
        title_text = self.title_font.render(TITLE, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text, title_rect)

        # Очистка старых прямоугольников
        self.option_rects = []

        # Пункты меню
        for idx, option in enumerate(self.OPTIONS):
            color = MENU_SELECTED_COLOR if idx == self.selected else MENU_TEXT_COLOR
            text = self.option_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + idx * 50))
            screen.blit(text, text_rect)
            self.option_rects.append(text_rect)


# Управление игровым миром
class GameWorld:
    def __init__(self, player, factory, level):
        self.player = player
        self.factory = factory
        self.level = level

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group(player)
        self.enemies = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.healing_items = pygame.sprite.Group()

        # Инициализация уровня
        self.initialize_level()
        self.removed_corpses = 0
        self.last_corpse_cleanup = pygame.time.get_ticks()
        self.corpse_cleanup_interval = 1000
        self.healing_item_spawned = False
        self.last_attack_time = 0

    def initialize_level(self):
        # Создание начальных врагов
        initial_enemies = generate_wave(self.level, self.player, self.factory)
        for enemy in initial_enemies:
            self.enemies.add(enemy)
        self.all_sprites.add(self.enemies)
        self.player.update_stats()  # Обновление статов игрока

    def update(self, current_time):
        # Обновление всех объектов
        self.all_sprites.update()
        self.effects.update()
        self.healing_items.update()

        # Спавн аптечки после 1 уровня
        if self.level > 1 and not self.healing_item_spawned:
            self.spawn_healing_item()

        # Коллизии с аптечками
        for _ in pygame.sprite.spritecollide(self.player, self.healing_items, True):
            self.player.heal(1)
            self.player.sound_service.play("health")

        # Уборка трупов
        if current_time - self.last_corpse_cleanup > self.corpse_cleanup_interval:
            self.last_corpse_cleanup = current_time
            for enemy in list(self.enemies):
                if enemy.state == "dying" and enemy.death_animation_completed:
                    if enemy.death_completed_time and current_time - enemy.death_completed_time > 5000:
                        enemy.kill()
                        self.removed_corpses += 1

        # Разрешение коллизий врагов
        resolve_collisions(self.enemies)

        # Проверка завершения уровня
        if all(enemy.state == "dying" for enemy in self.enemies):
            self.player.game_state.complete_level()
            self.level = self.player.game_state.session.level

            # Проверка победы
            if self.level > 10:
                return "victory"

            # Генерация новой волны
            self.healing_item_spawned = False
            new_enemies = generate_wave(self.level, self.player, self.factory)
            for enemy in new_enemies:
                self.enemies.add(enemy)
            self.all_sprites.add(new_enemies)
            self.player.update_stats()

        # Проверка смерти игрока
        if self.player.hits >= self.player.max_hits:
            return "gameover"

        return None

    def spawn_healing_item(self):
        # Спавн аптечки вдали от игрока
        while True:
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)
            distance_to_player = ((x - self.player.rect.centerx) ** 2 +
                                  (y - self.player.rect.centery) ** 2) ** 0.5
            if distance_to_player > HEALING_ITEM_SPAWN_DISTANCE * 2:
                break

        # Создание и добавление аптечки
        healing_item = self.factory.create_healing_item((x, y), self.player)
        self.healing_items.add(healing_item)
        self.all_sprites.add(healing_item)
        self.healing_item_spawned = True


# Система отрисовки
class RenderSystem:
    def __init__(self, camera, background_tile):
        self.camera = camera
        self.background_tile = background_tile

    def render(self, screen, all_sprites, effects, player, level):
        # Отрисовка фона
        draw_tiled_background(screen, self.background_tile, self.camera.offset)

        # Отрисовка спрайтов с сортировкой по Y
        for sprite in sorted(all_sprites.sprites(), key=lambda s: s.rect.bottom):
            if self.camera.is_visible(sprite.rect, 100):
                # Особый рендеринг для умирающих врагов
                if hasattr(sprite, 'state') and sprite.state == "dying" and hasattr(sprite, 'alpha'):
                    temp_surface = sprite.image.copy()
                    temp_surface.fill((255, 255, 255, sprite.alpha), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(temp_surface, self.camera.apply(sprite.rect))
                else:
                    screen.blit(sprite.image, self.camera.apply(sprite.rect))

        # Отрисовка эффектов
        for effect in effects:
            if self.camera.is_visible(effect.rect, 100):
                screen.blit(effect.image, self.camera.apply(effect.rect))

        # Отрисовка HUD
        draw_hud(screen, player, level)


# Игровое состояние
class PlayState(BaseState):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.game_state = self.game.game_state
        factory = GameObjectFactory(self.game.sound_service)

        # Создание игрока
        self.player = factory.create_player(
            (self.screen_width // 2, self.screen_height // 2),
            self.game_state
        )

        # Создание игрового мира
        self.game_world = GameWorld(
            self.player,
            factory,
            self.game_state.session.level
        )

        # Система рендеринга
        self.render_system = RenderSystem(
            Camera(self.screen_width, self.screen_height),
            load_sprite("background", "background.png")
        )

        # Настройка камеры
        self.render_system.camera.set_world_size(WORLD_WIDTH, WORLD_HEIGHT)

        # Переменные паузы
        self.paused = False
        self.pause_options = ["Continue", "Exit to Menu"]
        self.pause_selected = 0
        self.mouse_pos = (0, 0)
        self.last_attack_time = 0
        self.attack_cooldown = ATTACK_COOLDOWN
        self.pause_option_rects = []

    def handle_events(self, events):
        self.mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Пауза
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if self.paused:
                        self.pause_selected = 0
                    self.play_sound("menu_navigate")
                # Атака
                elif event.key == pygame.K_SPACE and not self.paused:
                    self.handle_attack()
                # Навигация в меню паузы
                if self.paused:
                    if event.key == pygame.K_UP:
                        self.pause_selected = (self.pause_selected - 1) % len(self.pause_options)
                        self.play_sound("menu_navigate")
                    elif event.key == pygame.K_DOWN:
                        self.pause_selected = (self.pause_selected + 1) % len(self.pause_options)
                        self.play_sound("menu_navigate")
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("menu_confirm")
                        self.handle_pause_selection()
            # Мышь в паузе
            elif event.type == pygame.MOUSEMOTION and self.paused:
                self.handle_pause_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.paused:
                self.handle_pause_mouse_click(event.pos)

    def handle_pause_mouse_motion(self, mouse_pos):
        # Выбор пунктов в паузе мышью
        for i, rect in enumerate(self.pause_option_rects):
            if rect.collidepoint(mouse_pos):
                self.pause_selected = i
                break

    def handle_attack(self):
        # Обработка атаки игрока
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.player.attack(self.game_world.effects, self.game_world.enemies)
            self.last_attack_time = current_time

    def handle_pause_selection(self):
        # Выбор в меню паузы
        if self.pause_selected == 0:
            self.paused = False  # Продолжить игру
        elif self.pause_selected == 1:
            self.state_manager.change_state("menu")  # Выход в меню

    def handle_pause_mouse_click(self, mouse_pos):
        # Клик по пунктам в паузе
        for i, rect in enumerate(self.pause_option_rects):
            if rect.collidepoint(mouse_pos):
                self.pause_selected = i
                self.play_sound("menu_confirm")
                self.handle_pause_selection()
                break

    def update(self, dt):
        if self.paused:
            return  # Не обновлять игру на паузе

        current_time = pygame.time.get_ticks()
        # Обновление камеры
        self.render_system.camera.update(self.player.rect)
        # Обновление мира и проверка состояния
        result = self.game_world.update(current_time)

        # Обработка результатов обновления
        if result == "victory":
            # Очистка перед победой
            self.game_world.all_sprites.empty()
            self.game_world.enemies.empty()
            self.game_world.effects.empty()
            self.game_world.healing_items.empty()
            self.state_manager.change_state("victory")
        elif result == "gameover":
            self.state_manager.change_state("gameover")

    def draw(self, screen):
        # Отрисовка игрового мира
        self.render_system.render(
            screen,
            self.game_world.all_sprites,
            self.game_world.effects,
            self.player,
            self.game_world.level
        )

        # Отрисовка экрана паузы
        if self.paused:
            self.draw_pause_screen(screen)

    def draw_pause_screen(self, screen):
        # Затемнение экрана
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(PAUSE_BG_COLOR)
        screen.blit(overlay, (0, 0))

        # Заголовок паузы
        title_font = get_font(64)
        title = title_font.render("PAUSED", True, MENU_TEXT_COLOR)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title, title_rect)

        # Пункты меню паузы
        option_font = get_font(36)
        self.pause_option_rects = []

        for i, option in enumerate(self.pause_options):
            color = MENU_SELECTED_COLOR if i == self.pause_selected else MENU_TEXT_COLOR
            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + i * 50))
            screen.blit(text, text_rect)
            self.pause_option_rects.append(text_rect)

        # Информация в углах
        info_font = get_font(24)
        info_text = info_font.render(
            f"Level: {self.game_world.level} | Corpses: {self.game_world.removed_corpses}",
            True, (200, 200, 200)
        )
        screen.blit(info_text, (10, 10))

        fps_text = info_font.render(f"FPS: {self.game.clock.get_fps():.1f}", True, (200, 200, 200))
        screen.blit(fps_text, (self.screen_width - fps_text.get_width() - 10, 10))


# Состояние улучшений
class UpgradeState(BaseState):
    OPTIONS = ["Increase Speed", "Increase Health", "Increase Damage", "Done"]
    STAT_COLORS = {
        "Speed": (100, 255, 100),
        "Health": (255, 100, 100),
        "Damage": (200, 100, 255)
    }

    def __init__(self, state_manager, progress):
        super().__init__(state_manager)
        self.progress = progress
        self.title_font = get_font(48)
        self.info_font = get_font(28)
        self.selected = 0
        self.last_purchase = 0
        self.purchase_effect = None
        self.option_rects = []

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Навигация
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.OPTIONS)
                    self.play_sound("menu_navigate")
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.OPTIONS)
                    self.play_sound("menu_navigate")
                elif event.key == pygame.K_RETURN:
                    self.play_sound("menu_confirm")
                    self.handle_option_select()
            # Мышь
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.play_sound("menu_confirm")
                self.handle_option_select()

    def handle_mouse_motion(self, mouse_pos):
        # Выбор мышью
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break

    def handle_option_select(self):
        now = pygame.time.get_ticks()
        # Защита от спама
        if now - self.last_purchase < 500:
            return

        option = self.OPTIONS[self.selected]
        success = False

        # Покупка улучшений
        if option == "Increase Speed":
            success = self.progress.buy_speed()
            self.purchase_effect = "speed" if success else None
        elif option == "Increase Health":
            success = self.progress.buy_health()
            self.purchase_effect = "health" if success else None
        elif option == "Increase Damage":
            success = self.progress.buy_damage()
            self.purchase_effect = "damage" if success else None
        elif option == "Done":
            self.state_manager.change_state("menu")  # Выход

        if success:
            self.last_purchase = now
            self.play_sound("upgrade_success")

    def update(self, dt):
        pass  # Нет логики обновления

    def draw(self, screen):
        screen.fill((50, 50, 70))  # Фон

        # Заголовок
        title = self.title_font.render("Upgrade Menu", True, (220, 180, 40))
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        # Очки улучшений
        points_text = self.info_font.render(
            f"Available Upgrade Points: {self.progress.upgrade_points}",
            True, (255, 215, 0)
        )
        points_rect = points_text.get_rect(center=(self.screen_width // 2, 140))
        screen.blit(points_text, points_rect)

        # Отрисовка опций
        self.option_rects = []
        start_y = 200
        gap = 40

        for idx, option in enumerate(self.OPTIONS):
            color = MENU_SELECTED_COLOR if idx == self.selected else MENU_TEXT_COLOR
            option_text = self.info_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + idx * gap))
            screen.blit(option_text, option_rect)
            self.option_rects.append(option_rect)

            # Уровни улучшений
            self.draw_option_level(screen, option, start_y + idx * gap, idx)

        # Статистика
        self.draw_stats(screen)
        self.draw_purchase_effect(screen)

    def draw_option_level(self, screen, option, y, idx):
        # Отображение уровня улучшения
        level_info = {
            "Increase Speed": ("Level", self.progress.speed_upgrades, f"+{self.progress.speed_upgrades * 20}%"),
            "Increase Health": ("Level", self.progress.health_upgrades, f"+{self.progress.health_upgrades * 2} HP"),
            "Increase Damage": ("Level", self.progress.damage_upgrades, f"+{self.progress.damage_upgrades} DMG")
        }

        if option in level_info:
            prefix, level, bonus = level_info[option]
            color = (150, 255, 150) if idx == self.selected else (100, 200, 100)
            level_text = self.info_font.render(f"{prefix}: {level} ({bonus})", True, color)
            level_x = self.screen_width // 2 + 150
            level_rect = level_text.get_rect(midleft=(level_x, y))
            screen.blit(level_text, level_rect)

    def draw_stats(self, screen):
        # Панель статистики внизу
        stats_y = self.screen_height - 120
        pygame.draw.rect(screen, (40, 40, 60), (0, stats_y, self.screen_width, 120))

        # Данные статистики
        stats = [
            ("Speed", self.progress.speed_upgrades, f"+{self.progress.speed_upgrades * 20}%"),
            ("Health", self.progress.health_upgrades, f"+{self.progress.health_upgrades * 2} HP"),
            ("Damage", self.progress.damage_upgrades, f"+{self.progress.damage_upgrades} DMG")
        ]

        start_x = self.screen_width // 4
        for i, (stat, level, bonus) in enumerate(stats):
            text = self.info_font.render(
                f"{stat}: Level {level} ({bonus})",
                True, self.STAT_COLORS[stat]
            )
            text_y = stats_y + 40 + i * 30
            screen.blit(text, (start_x, text_y))

    def draw_purchase_effect(self, screen):
        # Анимация покупки
        if self.purchase_effect and pygame.time.get_ticks() - self.last_purchase < 1000:
            effect_color = self.STAT_COLORS.get(self.purchase_effect.capitalize(), (255, 255, 255))
            effect_text = self.info_font.render("UPGRADE APPLIED!", True, effect_color)
            effect_rect = effect_text.get_rect(center=(self.screen_width // 2, 350))
            screen.blit(effect_text, effect_rect)


# Состояние проигрыша
class GameOverState(BaseState):
    def __init__(self, state_manager, level):
        super().__init__(state_manager)
        self.level = level
        self.title_font = get_font(72)
        self.stats_font = get_font(36)
        self.instruction_font = get_font(28)
        self.timer = 0
        self.button_rect = None

    def handle_events(self, events):
        for event in events:
            # Выход по Enter
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.play_sound("menu_confirm")
                self.state_manager.change_state("menu")
            # Клик для выхода
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect and self.button_rect.collidepoint(event.pos):
                    self.play_sound("menu_confirm")
                    self.state_manager.change_state("menu")

    def update(self, dt):
        self.timer += dt  # Таймер для анимаций

    def draw(self, screen):
        # Затемнение
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Текст Game Over
        game_over_text = self.title_font.render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(game_over_text, game_over_rect)

        # Достигнутый уровень
        level_text = self.stats_font.render(f"Reached Level {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(level_text, level_rect)

        # Инструкция
        instruction_text = self.instruction_font.render(
            "Press ENTER or click to return to Main Menu",
            True, (255, 255, 255)
        )
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height * 3 // 4))
        screen.blit(instruction_text, instruction_rect)
        self.button_rect = instruction_rect  # Для клика


# Состояние победы
class VictoryState(BaseState):
    def __init__(self, state_manager, stats=None):
        super().__init__(state_manager)
        self.title_font = get_font(72)
        self.stats_font = get_font(36)
        self.instruction_font = get_font(28)
        self.stats = stats or {}
        self.timer = 0
        self.button_rect = None

    def handle_events(self, events):
        for event in events:
            # Выход по Enter
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.play_sound("menu_confirm")
                self.state_manager.game.game_state.progress = PlayerProgress()  # Сброс прогресса
                self.state_manager.game.game_state.save()
                self.state_manager.change_state("menu")
            # Клик для выхода
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect and self.button_rect.collidepoint(event.pos):
                    self.play_sound("menu_confirm")
                    self.state_manager.game.game_state.progress = PlayerProgress()  # Сброс прогресса
                    self.state_manager.game.game_state.save()
                    self.state_manager.change_state("menu")

    def update(self, dt):
        self.timer += dt  # Таймер для анимаций

    def draw(self, screen):
        # Затемнение
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Текст победы
        victory_text = self.title_font.render("You Win!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(victory_text, victory_rect)

        # Статистика
        y_pos = self.screen_height // 3
        for key, value in self.stats.items():
            stat_text = self.stats_font.render(f"{key}: {value}", True, (255, 255, 255))
            stat_rect = stat_text.get_rect(center=(self.screen_width // 2, y_pos))
            screen.blit(stat_text, stat_rect)
            y_pos += 50

        # Инструкция
        done_text = self.instruction_font.render(
            "Press ENTER or click to return to Main Menu",
            True, (255, 255, 255))
        done_rect = done_text.get_rect(center=(self.screen_width // 2, self.screen_height * 3 // 4))
        screen.blit(done_text, done_rect)
        self.button_rect = done_rect  # Для клика