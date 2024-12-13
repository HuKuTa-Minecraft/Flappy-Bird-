from settings import *

from resources import Images
from animation import Animation

class Object:
    def __init__(self, x: int, y: int, width: int, height: int, level_data):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (0, 255, 0)
        self.level_data = level_data

    def draw(self, screen):
        pass

    def update(self):
        pass

class Tube(Object):
    def __init__(self, x: int, y: int, width: int, height: int, level_data, tube_index: int):
        super().__init__(x, y, width, height, level_data)
        self.level_constants = level_data.constants
        self.color = self.level_constants.tube_color
        self.tube_index = tube_index
        self.head_width = self.width + 10
        self.head_height = 16

    def relocate(self):
        self.y = rand.randint(
            min(self.level_constants.limit_tube_y, WINDOW_HEIGHT // 2),
            max(WINDOW_HEIGHT - self.level_constants.limit_tube_y - self.level_constants.tube_vgap, WINDOW_HEIGHT // 2)
        )

    def draw(self, screen):
        self.color = (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255)) if self.level_constants.tube_random_color else self.color
        pg.draw.rect(screen, self.color, (self.x, 0, self.width, self.y))
        pg.draw.rect(screen, self.level_constants.tube_head_color, (
            (self.x + (self.width - self.head_width) // 2),
            self.y - self.head_height,
            self.head_width,
            self.head_height
        ))
        pg.draw.rect(screen, self.color, (
            self.x,
            self.y + self.level_constants.tube_vgap,
            self.width,
            WINDOW_HEIGHT - (self.y + self.level_constants.tube_vgap)
        ))
        pg.draw.rect(screen, self.level_constants.tube_head_color, (
            (self.x + (self.width - self.head_width) // 2),
            self.y + self.level_constants.tube_vgap,
            self.head_width,
            self.head_height
        ))

    def update(self):
        self.x = self.x - self.level_constants.tube_speed
        if self.x + self.width < 0:
            self.relocate()

class Bird(Object):
    MAX_VEL_Y = 10.0
    def __init__(self, x: int, y: int, width: int, height: int, level_data):
        super().__init__(x, y, width, height, level_data)
        bird_file_index = (
            "0"+str(level_data.scopes.bird_index + 1) if level_data.scopes.bird_index + 1 < 10 else
           level_data.scopes.bird_index + 1
        )
        self.animation = Animation((
            Images.get_images(
                width, height,
                f'bird{bird_file_index}_0',
                f'bird{bird_file_index}_1',
                f'bird{bird_file_index}_2'
            )
        ))
        # self.accel_y = 10
        self.vel_x = 0.0
        self.vel_y = 0.0

    def jump(self):
        self.vel_y = -8
        self.animation.play()

    def draw(self, screen: pg.Surface):
        # pg.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        self.color = (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255)) if self.level_data.constants.bird_random_color else self.color
        x_int = int(self.x)
        y_int = int(self.y)
        # pg.draw.rect(screen, (0, 0, 0), (x_int, y_int, self.width, self.height))
        # half_width = int(self.width // 2)
        # half_height = int(self.height // 2)
        # gfxdraw.aacircle(screen, x_int + half_width, y_int + half_height, half_width, self.color)
        # gfxdraw.filled_ellipse(screen, x_int + half_width, y_int + half_height, half_width, half_height, self.color)
        self.animation.draw(x_int, y_int, screen, -self.vel_y)

    def update(self):
        # self.accel_y = min(max(self.vel_y * self.level_constants.gravity, -Bird.MAX_VEL_Y), Bird.MAX_VEL_Y)
        # self.vel_y = min(max(self.vel_y + self.accel_y, -Bird.MAX_VEL_Y), Bird.MAX_VEL_Y)
        # self.vel_y = self.vel_y * self.level_constants.gravity
        # self.vel_y = self.vel_y + 0.005
        self.animation.update()
        self.vel_y = min(max(self.vel_y + self.level_data.constants.gravity, -Bird.MAX_VEL_Y), Bird.MAX_VEL_Y)
        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        # print(self.vel_y)

import enum

class Cloud(Object):
    class CloudType(enum.Enum):
        def __init__(self, speed: int, width: int, height: int):
            self.speed = speed
            self.width = width
            self.height = height
        parallax_1 = 1.1, 16, 9
        parallax_2 = 1.2, 32, 19
        parallax_3 = 1.3, 46, 27
        parallax_4 = 1.4, 72, 43

    def __init__(self, x: int, y: int, cloud_type: CloudType, level_data):
        super().__init__(x, y, cloud_type.width, cloud_type.height, level_data)
        self.cloud_type = Cloud.CloudType.parallax_1
        self.color = self.level_data.constants.cloud_color

    def random_type(self):
        self.set_type(rand.choice(list(Cloud.CloudType)))

    def relocate_y(self):
        self.y = rand.randint(0, self.level_data.constants.cloud_y_max - self.height)

    def relocate(self):
        self.relocate_y()
        # self.x = rand.randint(WINDOW_WIDTH, WINDOW_WIDTH * 2 - self.width)
        self.x = WINDOW_WIDTH
        self.random_type()

    def set_type(self, cloud_type: CloudType):
        self.cloud_type = cloud_type
        self.width = self.cloud_type.width
        self.height = self.cloud_type.height

    def draw(self, screen):
        self.color = (rand.randint(0,255), rand.randint(0,255), rand.randint(0,255)) if self.level_data.constants.cloud_random_color else self.color
        pg.draw.rect(screen, self.color, (
            self.x, self.y,
            self.width, self.height
        ))

    def update(self):
        self.x = self.x - self.cloud_type.speed
        if self.x + self.width < 0:
            self.relocate()