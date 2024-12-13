from typing import Tuple

from settings import *

class Animation:
    def __init__(self, frames: Tuple[pg.image] = tuple(), ticks_per_frame: int = 10, loop: bool = False):
        self.ticks = 0
        self.__loop = loop
        self.frame_index = 0
        self.ticks_per_frame = ticks_per_frame
        self.__frames: Tuple[pg.image] = frames
        self.duration_ticks = (self.get_frame_count() - (0 if self.__loop else 1)) * self.ticks_per_frame

    def draw(self, x: int, y: int, screen: pg.Surface, angle: float = 0):
        image = pg.transform.rotate(self.current_frame(), angle)
        rect = image.get_rect()
        rect = rect.move((x, y))
        screen.blit(image, rect)

    def play(self):
        if not self.__loop:
            self.ticks = self.duration_ticks

    def current_frame(self):
        return self.get_frame(self.frame_index)

    def next_frame(self):
        if self.frame_index + 1 == len(self.__frames):
            self.frame_index = 0
        else:
            self.frame_index += 1

    def prev_frame(self):
        if self.frame_index - 1 < 0:
            self.frame_index = len(self.__frames) - 1
        else:
            self.frame_index -= 1

    def get_frame(self, index: int):
        return self.__frames[min(max(index, 0), len(self.__frames) - 1)]

    def get_frame_count(self):
        return len(self.__frames)

    def update(self):
        if self.__loop:
            self.frame_index = self.ticks // self.ticks_per_frame
            self.ticks += 1
            if self.ticks >= self.duration_ticks:
                self.ticks -= self.duration_ticks
        else:
            if self.ticks > 0:
                self.ticks -= 1
                # print(((self.duration_ticks - self.ticks) % self.ticks_per_frame), (self.duration_ticks - self.ticks), self.ticks, self.duration_ticks)
                self.frame_index = (self.duration_ticks - self.ticks) // self.ticks_per_frame + 1
                if self.ticks == 0:
                    self.frame_index = 0