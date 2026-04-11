import pygame
import math
import random
from collections import deque

pygame.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("slither.io")

clock = pygame.time.Clock()

pygame.font.init()
font_big  = pygame.font.SysFont("consolas", 54, bold=True)
font_med  = pygame.font.SysFont("consolas", 22, bold=True)
font_sm   = pygame.font.SysFont("consolas", 14)

# ---------------- INPUT ----------------
def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    return keys, mouse_pos, mouse_click

# ---------------- FONDO DEGRADADO ----------------
def draw_background(surface):
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H

        r = int(10 + (40 - 10) * ratio)
        g = int(15 + (45 - 15) * ratio)
        b = int(20 + (50 - 20) * ratio)

        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

# ---------------- DIBUJO ----------------
def draw_circle(surface, color, pos, radius):
    pygame.draw.circle(surface, color, pos, radius)

def draw_text(surface, text, font, color, pos):
    label = font.render(text, True, color)
    surface.blit(label, pos)

# ---------------- EVENTOS ----------------
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

# ---------------- BOTON ----------------
def draw_button(surface, text, x, y, w, h, mouse_pos, mouse_click):
    rect = pygame.Rect(x, y, w, h)

    if rect.collidepoint(mouse_pos):
        color = (60, 60, 60)
        if mouse_click[0]:
            return True
    else:
        color = (30, 30, 30)

    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, (255,255,255), rect, 2)

    draw_text(surface, text, font_med, (255,255,255), (x + 50, y + 12))

    return False

# ---------------- MENU ----------------
def draw_menu(surface, mouse_pos, mouse_click):
    draw_background(surface)

    draw_text(surface, "SLITHER.IO", font_big, (0,255,0), (SCREEN_W//2 - 170, 200))

    if draw_button(surface, "JUGAR", SCREEN_W//2 - 100, 350, 200, 50, mouse_pos, mouse_click):
        return "play"

    return None

# ---------------- JUEGO ----------------
game_state = "menu"

running = True
while running:
    running = handle_events()
    keys, mouse_pos, mouse_click = handle_input()

    if game_state == "menu":
        action = draw_menu(screen, mouse_pos, mouse_click)

        if action == "play":
            game_state = "game"

    elif game_state == "game":
        draw_background(screen)

        draw_circle(screen, (0, 255, 0), (SCREEN_W//2, SCREEN_H//2), 20)
        draw_text(screen, "puntaje:", font_med, (255,255,255), (20,20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
