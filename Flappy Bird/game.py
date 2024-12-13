from settings import *
from resources import Fonts, Saves, Images

from level import LevelManager

class Game:
    @staticmethod
    def quit_pygame():
        pg.quit()

    def __init__(self):
        self.clock = None
        self.screen = None
        self.running = False

    def init_pygame(self):
        pg.init()
        self.clock = pg.time.Clock()
        flags = pg.FULLSCREEN if FULLSCREEN else 0
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=flags | pg.DOUBLEBUF)
        pg.font.init()
        Fonts.init()
        Images.load_sync()
        pg.display.set_caption(f"PyBird")

    def start(self):
        self.init_pygame()
        self.running = True

        LevelManager.set_best_score(Saves.read_scores())
        LevelManager.change_level(LevelManager.menu_level(self.screen))

        #ticks_for_stats = pg.time.get_ticks()
        #updates: int = 0

        unprocessed_ticks = 0
        old_ticks = pg.time.get_ticks()
        import math
        while self.running:
            now_ticks = pg.time.get_ticks()
            delta = (now_ticks - old_ticks)
            unprocessed_ticks = round(unprocessed_ticks + delta, 2)
            old_ticks = now_ticks
            #print(unprocessed_ticks, TARGET_TICKS)
            if math.isclose(unprocessed_ticks, TARGET_TICKS) or unprocessed_ticks > TARGET_TICKS:
            # if unprocessed_ticks >= TARGET_TICKS:
                self.update()
                #updates += 1
                unprocessed_ticks = round(unprocessed_ticks - TARGET_TICKS, 2)
            self.on_draw()

            # if pg.time.get_ticks() - ticks_for_stats > 1000:
            #     print(updates, unprocessed_ticks, TARGET_TICKS)
            #     pg.display.set_caption(f"PyBird UPS: {updates}")
            #     ticks_for_stats += 1000
            #     updates = 0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.running = False
                    break
                self.event(event)
        Game.quit_pygame()

    def on_draw(self):
        self.screen.fill((0, 0, 0))
        self.draw()
        pg.display.flip()

    def update(self):
        #self.clock.tick()
        LevelManager.get_current_level().update()

    def draw(self):
        LevelManager.get_current_level().draw()

    def event(self, event):
        LevelManager.get_current_level().event(event)