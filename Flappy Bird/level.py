from settings import *
from animation import Animation
from resources import Fonts, Saves, Images

from typing import List

# Data that will transport between levels
class LevelScopes:
    def __init__(self):
        # Global scope...
        self.bird_index = 0
        # Local scopes...
        self.__scopes = dict()
    def set(self, name: str, value):
        self.__scopes[name] = value
    def get(self, name: str):
        return self.__scopes[name] if (name in self.__scopes) else False

class BaseLevel:
    def __init__(self, screen: pg.Surface, level_name: str, level_scopes: LevelScopes = LevelScopes()):
        self.screen = screen
        self.level_name = level_name
        self.level_scopes = level_scopes

    def init(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass

    def event(self, event):
        pass

class LevelData:
    class Constants:
        def __init__(self):
            self.gravity = 0.35

            self.counter_random_color = False
            self.counter_color = (0, 0, 0)

            self.bg_random_color = False
            self.bg_color = (78, 192, 202)

            self.tube_random_color = False
            self.tube_color = (60, 128, 0)
            self.tube_head_color = (60, 126, 0)
            self.tube_hgap = 180
            self.tube_vgap = 160
            self.tube_width = 96
            self.tube_counts = 3
            self.tube_speed = 2
            self.limit_tube_y = 120

            self.has_clouds = True
            self.cloud_random_color = False
            self.cloud_counts = 8
            self.cloud_y_max = WINDOW_HEIGHT // 4
            self.cloud_color = (232, 252, 223)

            self.ground_random_color = False
            self.ground_color = (0, 255, 0)
            self.ground_height = WINDOW_HEIGHT // 8

            self.bird_random_color = False
            self.bird_height = 36
            self.bird_width = int(round(self.bird_height / 0.75))
    def __init__(self):
        self.scopes = LevelScopes()
        self.constants = LevelData.Constants()

from gameobjects import Object, Bird, Tube, Cloud

class Level(BaseLevel):
    def __init__(self, screen: pg.Surface, level_name: str, level_data = LevelData()):
        super().__init__(screen, level_name, level_data.scopes)
        self.paused = False

        self.scores = 0
        self.adding_score = False
        self.objects: List[Object] = []
        self.level_data = level_data
        self.level_constants = self.level_data.constants

        if self.level_constants.has_clouds:
            self.clouds = []
            for i in range(self.level_constants.cloud_counts):
                cloud = Cloud(0, 0, Cloud.CloudType.parallax_1, self.level_data)
                cloud.random_type()
                cloud.x = rand.randint(0, (WINDOW_WIDTH * 2 - cloud.width))
                cloud.relocate_y()
                self.clouds.append(cloud)
            self.objects.extend(self.clouds)

        self.tubes = []
        for i in range(self.level_constants.tube_counts):
            tube = Tube(
                self.screen.get_width() + (i * (self.level_constants.tube_width + self.level_constants.tube_hgap)),
                0,
                self.level_constants.tube_width,
                0,
                self.level_data,
                i
            )
            tube.relocate()
            self.tubes.append(tube)
        self.objects.extend(self.tubes)

        self.bird = Bird(
            96,
            (WINDOW_HEIGHT - self.level_constants.bird_height) // 2,
            self.level_constants.bird_width,
            self.level_constants.bird_height,
            self.level_data
        )
        self.bird.color = BIRD_COLOR
        self.objects.append(self.bird)

    def init(self):
        # self.bird.color = tuple(rand.randint(60, 255) for _ in range(3))
        self.bird.color = (rand.randint(BIRD_COLOR[0] - 10, BIRD_COLOR[0] + 10), 0, 0)

    def draw(self):
        self.screen.fill(
            (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255))
            if self.level_constants.bg_random_color else self.level_constants.bg_color,
             (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
         )

        pg.draw.rect(self.screen,
            (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255))
            if self.level_constants.ground_random_color else self.level_constants.ground_color, (
            0,
            WINDOW_HEIGHT - self.level_constants.ground_height,
            WINDOW_WIDTH,
            self.level_constants.ground_height
        ))

        for object in self.objects:
            object.draw(self.screen)

        scores_text_surface = Fonts.font64.render(f"{self.scores}", FONT_ANTIALIASING,
            (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255))
            if self.level_constants.counter_random_color else self.level_constants.counter_color
        )
        self.screen.blit(scores_text_surface, (
            (WINDOW_WIDTH - scores_text_surface.get_width()) // 2,
            scores_text_surface.get_height() + 12
        ))

        if self.paused:
            gray_fx_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pg.SRCALPHA)
            gray_fx_surface.fill((120, 120, 120, 200))
            self.screen.blit(gray_fx_surface, (0, 0))
            # pg.draw.rect(self.screen, (120, 120, 120, 90), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    def update(self):
        if self.paused: return
        for object in self.objects:
            object.update()
        at_once_one_x_level_tube = False
        for tube in self.tubes:
            tube_x = tube.x
            if tube_x > WINDOW_WIDTH: continue
            tube_w = tube.width
            if tube_x + tube_w < 0:
                tube.x = (
                    self.tubes[(tube.tube_index - 1) % self.level_constants.tube_counts].x +
                    (self.level_constants.tube_width + self.level_constants.tube_hgap)
                )
            else:
                #Bird collision check
                bird_x = self.bird.x
                bird_y = self.bird.y
                bird_w = self.level_constants.bird_width
                bird_h = self.level_constants.bird_height
                tube_limit_y = tube.y
                one_x_level_tube = bird_x + bird_w >= tube_x and bird_x < tube_x + tube_w

                if one_x_level_tube and not at_once_one_x_level_tube: at_once_one_x_level_tube = True

                top_column_collied = one_x_level_tube and bird_y < tube_limit_y
                bottom_column_collied = one_x_level_tube and bird_y + bird_h > tube_limit_y + self.level_constants.tube_vgap
                if top_column_collied or bottom_column_collied:
                    self.lose()
                    break

        if at_once_one_x_level_tube:
            if not self.adding_score:
                self.adding_score = True
                self.scores = self.scores + 1
        else:
            if self.adding_score:
                self.adding_score = False

        if (self.bird.y + self.level_constants.bird_height < 0 or
            self.bird.y + self.level_constants.bird_height > WINDOW_HEIGHT - self.level_constants.ground_height):
            self.lose()

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                self.bird.jump()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.bird.jump()
            if event.key == pg.K_PAUSE:
                self.paused = not self.paused

    def lose(self):
        best_score = max(self.scores, LevelManager.get_best_score())
        new_best_score = best_score > LevelManager.prev_best_score
        if new_best_score:
            Saves.save_scores(self.scores)
            LevelManager.set_best_score(best_score)
        level_scopes = LevelScopes()
        level_scopes.set('new_best_score', new_best_score)
        level_scopes.bird_index = self.level_data.scopes.bird_index
        LevelManager.change_level(LevelManager.menu_level(self.screen, level_scopes))


class MenuLevel(BaseLevel):
    def __init__(self, screen: pg.Surface, level_scopes: LevelScopes, level_name: str):
        super().__init__(screen, level_name, level_scopes)

        y_buttons_offset = 150
        self.start_game_button = {
            'x': (WINDOW_WIDTH - 140) // 2,
            'y': (WINDOW_HEIGHT - 96) // 2 - y_buttons_offset,
            'w': 140,
            'h': 96,
            'text': 'Start game',
            'hover_cursor': True,
            'is_hover': False
        }
        self.start_ghost_game_button = {
            'x': (WINDOW_WIDTH - 140) // 2,
            'y': (WINDOW_HEIGHT - 96) // 2 - y_buttons_offset + 96 + 12,
            'w': 140,
            'h': 96,
            'text': 'Start ghost game',
            'hover_cursor': True,
            'is_hover': False
        }
        self.start_space_game_button = {
            'x': (WINDOW_WIDTH - 140) // 2,
            'y': (WINDOW_HEIGHT - 96) // 2 - y_buttons_offset + (96 + 12) * 2,
            'w': 140,
            'h': 96,
            'text': 'Start moon game',
            'hover_cursor': True,
            'is_hover': False
        }
        self.formula_game_button = {
            'x': (WINDOW_WIDTH - 140) // 2,
            'y': (WINDOW_HEIGHT - 96) // 2 - y_buttons_offset + (96 + 12) * 3,
            'w': 140,
            'h': 96,
            'text': 'Start F1 game',
            'hover_cursor': True,
            'is_hover': False
        }
        self.start_lsd_game_button = {
            'x': (WINDOW_WIDTH - 140) // 2 + 140 + 12,
            'y': (WINDOW_HEIGHT - 96) // 2 - y_buttons_offset,
            'w': 140,
            'h': 96,
            'text': '0_0',
            'hover_cursor': True,
            'is_hover': False
        }
        self.prev_bird_button = {
            'x': self.formula_game_button['x'],
            'y': self.formula_game_button['y'] + self.formula_game_button['h'] + (WINDOW_HEIGHT - (self.formula_game_button['y'] + self.formula_game_button['h']) - 96) // 2,
            'w': 20,
            'h': 96,
            'text': '<',
            'hover_cursor': True,
            'is_hover': False
        }
        self.next_bird_button = {
            'x': self.formula_game_button['x'] + self.formula_game_button['w'] - 20,
            'y': self.formula_game_button['y'] + self.formula_game_button['h'] + (WINDOW_HEIGHT - (self.formula_game_button['y'] + self.formula_game_button['h']) - 96) // 2,
            'w': 20,
            'h': 96,
            'text': '>',
            'hover_cursor': True,
            'is_hover': False
        }
        self.buttons: List[dict] = [
            self.start_game_button, self.start_ghost_game_button, self.start_space_game_button, self.formula_game_button,
            self.next_bird_button, self.prev_bird_button
        ]

        self.bird_height = 64
        self.bird_width = int(round(self.bird_height / 0.75))
        self.bird_x = (WINDOW_WIDTH - self.bird_width) // 2
        self.bird_y = self.next_bird_button['y'] + (self.next_bird_button['h'] - self.bird_height) // 2
        self.bird_index = self.level_scopes.bird_index
        self.bird_anims = [
            Animation((
                Images.get_images(
                    self.bird_width,
                    self.bird_height,
                    f'bird{"0"+str(i) if i < 10 else i}_0',
                    f'bird{"0"+str(i) if i < 10 else i}_1',
                    f'bird{"0"+str(i) if i < 10 else i}_2'
                )
            ), loop=True, ticks_per_frame=40) for i in range(1, BIRDS_COUNT + 1)
        ]

        self.last_keys = []
        self.last_keys_length = 3
        self.new_best_scores = level_scopes.get('new_best_score')

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            at_once_one_button_hovered, hovered_button = self.over_start_button(event.pos[0], event.pos[1])
            if at_once_one_button_hovered:
                if hovered_button == self.start_game_button:
                    self.enter_game_level()
                elif hovered_button == self.start_ghost_game_button:
                    self.enter_ghost_game_level()
                elif hovered_button == self.start_space_game_button:
                    self.enter_space_game_level()
                elif hovered_button == self.formula_game_button:
                    self.enter_formula_game_level()
                elif hovered_button == self.start_lsd_game_button:
                    self.enter_lsd_game_level()

                if hovered_button == self.next_bird_button:
                    self.next_bird()
                if hovered_button == self.prev_bird_button:
                    self.prev_bird()
        if event.type == pg.MOUSEMOTION:
            at_once_one_button_hovered, hovered_button = self.over_start_button(event.pos[0], event.pos[1])
            pg.mouse.set_cursor(
                pg.SYSTEM_CURSOR_HAND
                if at_once_one_button_hovered and hovered_button['hover_cursor'] else
                pg.SYSTEM_CURSOR_ARROW
            )
        if event.type == pg.KEYDOWN:
            if event.unicode:
                self.last_keys.append(event.unicode)
                if len(self.last_keys) > self.last_keys_length:
                    self.last_keys.pop(0)
                if "".join(self.last_keys).lower() == 'lsd':
                    self.buttons.append(self.start_lsd_game_button)
            if event.key == pg.K_1:
                self.enter_game_level()
            if event.key == pg.K_2:
                self.enter_ghost_game_level()
            if event.key == pg.K_3:
                self.enter_space_game_level()
            if event.key == pg.K_4:
                self.enter_formula_game_level()

    def draw(self):
        for button in self.buttons:
            btn_text_surface = (Fonts.font20 if button['is_hover'] else Fonts.font22).render(
                button['text'], FONT_ANTIALIASING, (0, 0, 0)
            )
            pg.draw.rect(
                self.screen,
                (255, 255, 255),
                (button['x'], button['y'], button['w'], button['h'])
            )
            self.screen.blit(btn_text_surface, (
                (button['x'] + (button['w'] - btn_text_surface.get_width()) // 2),
                (button['y'] + (button['h'] - btn_text_surface.get_height()) // 2)
            ))

        title_text_srf = Fonts.font64.render('PyBird', FONT_ANTIALIASING, (255, 255, 255))
        self.screen.blit(title_text_srf, (
            ((WINDOW_WIDTH - title_text_srf.get_width()) // 2),
            (title_text_srf.get_height() + WINDOW_HEIGHT // 8)
        ))

        score_text_surface = (Fonts.font22.render(
            f"Best score: {LevelManager.get_best_score()}",
            FONT_ANTIALIASING,
            (255, 255, 255) if not self.new_best_scores else (0, 255, 0)
        ))
        self.screen.blit(score_text_surface, (
            ((WINDOW_WIDTH - score_text_surface.get_width()) // 2),
            (score_text_surface.get_height() + 10)
        ))

        text_bird_index_srf = Fonts.font32.render(
            f'{self.bird_index + 1}/{len(self.bird_anims)}',
            FONT_ANTIALIASING,
            (255, 255, 255)
        )
        self.screen.blit(text_bird_index_srf, (
            ((WINDOW_WIDTH - text_bird_index_srf.get_width()) // 2),
            self.next_bird_button['y'] + self.next_bird_button['h'] + text_bird_index_srf.get_height()
        ))
        self.bird_anims[self.bird_index].draw(self.bird_x, self.bird_y, self.screen)

    def update(self):
        for bird_anim in self.bird_anims:
            bird_anim.update()
        # self.bird_anims[self.bird_index].update()

    def over_start_button(self, x: int, y: int) -> (bool, dict):
        for button in self.buttons: button['is_hover'] = False
        for button in self.buttons:
            if ((button['x'] <= x < button['x'] + button['w']) and
                (button['y'] <= y < button['y'] + button['h'])):
                button['is_hover'] = True
                return True, button
        return False, None

    @staticmethod
    def __change_level(level: BaseLevel):
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        LevelManager.change_level(level)

    def next_bird(self):
        if self.bird_index + 1 == len(self.bird_anims):
            self.bird_index = 0
        else:
            self.bird_index += 1

    def prev_bird(self):
        if self.bird_index - 1 < 0:
            self.bird_index = len(self.bird_anims) - 1
        else:
            self.bird_index -= 1

    def enter_game_level(self):
        level_data = LevelData()
        level_data.scopes.bird_index = self.bird_index
        self.__change_level(LevelManager.game_level(self.screen, level_data))

    def enter_ghost_game_level(self):
        level_data = LevelData()
        level_data.scopes.bird_index = self.bird_index
        level_data.constants.tube_counts = 2
        level_data.constants.tube_hgap = max(level_data.constants.tube_hgap - 20, 128)
        level_data.constants.tube_color = (200, 200, 200)
        level_data.constants.tube_head_color = (198, 198, 198)
        # game_level_constans.gravity = 0.2
        game_level = LevelManager.game_level(self.screen, level_data)
        self.__change_level(game_level)

    def enter_space_game_level(self):
        level_data = LevelData()
        level_data.scopes.bird_index = self.bird_index
        level_data.constants.gravity = 0.2
        level_data.constants.tube_vgap = level_data.constants.tube_vgap + 64
        # game_level_constans.has_clouds = False
        level_data.constants.bg_color = (5, 69, 105)
        # game_level_constans.bg_color = (85, 145, 169)
        level_data.constants.cloud_color = (255, 255, 0)
        level_data.constants.counter_color = (255, 255, 255)
        level_data.constants.ground_color = (206, 215, 224)
        game_level = LevelManager.game_level(self.screen, level_data)
        self.__change_level(game_level)

    def enter_formula_game_level(self):
        level_data = LevelData()
        level_data.scopes.bird_index = self.bird_index
        level_data.constants.tube_speed = 8
        level_data.constants.tube_vgap = 250
        level_data.constants.tube_hgap += 60
        game_level = LevelManager.game_level(self.screen, level_data)
        self.__change_level(game_level)

    def enter_lsd_game_level(self):
        level_data = LevelData()
        level_data.scopes.bird_index = self.bird_index
        level_data.constants.cloud_y_max = WINDOW_HEIGHT
        level_data.constants.bg_random_color = True
        level_data.constants.bird_random_color = True
        level_data.constants.tube_random_color = True
        level_data.constants.cloud_random_color = True
        level_data.constants.ground_random_color = True
        level_data.constants.counter_random_color = True
        game_level = LevelManager.game_level(self.screen, level_data)
        self.__change_level(game_level)


class LevelManager:
    menu_level_name = "menuLevel"
    game_level_name = "gameLevel"

    __best_score = 0
    prev_best_score = __best_score

    __current_level: BaseLevel = None

    @staticmethod
    def set_best_score(value: int):
        LevelManager.__best_score = value
        LevelManager.prev_best_score = value
    @staticmethod
    def get_best_score() -> int:
        return LevelManager.__best_score

    @staticmethod
    def menu_level(screen: pg.Surface, level_scopes: LevelScopes = LevelScopes()) -> MenuLevel:
        return MenuLevel(screen, level_scopes, LevelManager.menu_level_name)

    @staticmethod
    def game_level(screen: pg.Surface, level_data = LevelData()) -> Level:
        return Level(screen, LevelManager.game_level_name, level_data)

    @staticmethod
    def get_current_level() -> BaseLevel:
        return LevelManager.__current_level

    @staticmethod
    def change_level(level: BaseLevel):
        del LevelManager.__current_level
        LevelManager.__current_level = level
        LevelManager.__current_level.init()