from pygame import gfxdraw
import pygame as pg
import random as rand

BIRDS_COUNT = 6

TARGET_FPS = 75
TARGET_TICKS = round(1000 / TARGET_FPS, 2)
# TARGET_TICKS = 1000 // TARGET_FPS

print(TARGET_FPS, TARGET_TICKS)

FULLSCREEN = False

FONT_ANTIALIASING = True

BIRD_COLOR = (128, 0, 0)

WINDOW_WIDTH = 520
# Horizontal
# WINDOW_HEIGHT = WINDOW_WIDTH // 16 * 9

# Vertical
WINDOW_HEIGHT = WINDOW_WIDTH // 3 * 5