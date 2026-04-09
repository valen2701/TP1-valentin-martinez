import pygame
import math
import random
from collections import deque


pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)


SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("slither.io")

clock = pygame.time.Clock()


pygame.font.init()
font_big  = pygame.font.SysFont("consolas", 54, bold=True)
font_med  = pygame.font.SysFont("consolas", 22, bold=True)
font_sm   = pygame.font.SysFont("consolas", 14)

def play_sound(sound):
    try:
        sound.play()
    except:
        pass

def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    return keys, mouse_pos, mouse_click

def draw_background(surface):
    surface.fill((8, 12, 25))

    for x in range(0, SCREEN_W, 80):
        pygame.draw.line(surface, (18,26,45), (x,0), (x,SCREEN_H))
    for y in range(0, SCREEN_H, 80):
        pygame.draw.line(surface, (18,26,45), (0,y), (SCREEN_W,y))

def draw_circle(surface, color, pos, radius):
    pygame.draw.circle(surface, color, pos, radius)

def draw_text(surface, text, font, color, pos):
    label = font.render(text, True, color)
    surface.blit(label, pos)

def draw_particle(surface, x, y, color, size):
    pygame.draw.circle(surface, color, (int(x), int(y)), int(size))

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

running = True
while running:
    running = handle_events()

    keys, mouse_pos, mouse_click = handle_input()

    draw_background(screen)

    draw_circle(screen, (0, 255, 0), (SCREEN_W//2, SCREEN_H//2), 20)
    draw_text(screen, "puntaje:", font_med, (255,255,255), (20,20))

    pygame.display.flip()
    clock.tick(60)

SEGMENT_RADIUS = 8
NORMAL_SPEED   = 2.8
BOOST_SPEED    = 6.0
TURN_SPEED     = 0.065

WORLD_W, WORLD_H = 3000, 3000


def dist2(a, b):
    dx, dy = a[0]-b[0], a[1]-b[1]
    return dx*dx + dy*dy

def dist(a, b):
    return math.sqrt(dist2(a, b))

def angle_diff(a, b):
    d = (b - a) % (2*math.pi)
    if d > math.pi:
        d -= 2*math.pi
    return d

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class Food:
    def __init__(self):
        self.x = random.uniform(50, WORLD_W-50)
        self.y = random.uniform(50, WORLD_H-50)
        self.value = 1

class Snake:
    def __init__(self, x, y):
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = NORMAL_SPEED
        self.boosting = False
        self.alive = True
        self.score = 0

        self.segments = deque()
        for i in range(20):
            self.segments.appendleft((
                x - i * math.cos(self.angle) * SEGMENT_RADIUS,
                y - i * math.sin(self.angle) * SEGMENT_RADIUS
            ))

    @property
    def head(self):
        return self.segments[0]

    def grow(self, n=1):
        tail = self.segments[-1]
        for _ in range(n):
            self.segments.append(tail)

    def update(self, dx, dy, boost):
        if not self.alive:
            return

        if dx != 0 or dy != 0:
            target = math.atan2(dy, dx)
            diff = angle_diff(self.angle, target)
            self.angle += clamp(diff, -TURN_SPEED, TURN_SPEED)

        self.boosting = boost

        speed = BOOST_SPEED if self.boosting else NORMAL_SPEED

        hx, hy = self.head
        nx = (hx + math.cos(self.angle) * speed) % WORLD_W
        ny = (hy + math.sin(self.angle) * speed) % WORLD_H

        self.segments.appendleft((nx, ny))
        self.segments.pop()

        if self.boosting and len(self.segments) > 10:
            self.segments.pop()

    def eat(self, foods):
        hx, hy = self.head
        eaten = []

        for i, f in enumerate(foods):
            if dist2((hx, hy), (f.x, f.y)) < (SEGMENT_RADIUS * 2)**2:
                self.score += f.value
                self.grow(2)
                eaten.append(i)

        return eaten




pygame.quit()
