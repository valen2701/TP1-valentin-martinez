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
font_big      = pygame.font.SysFont("consolas", 54, bold=True)
font_med      = pygame.font.SysFont("consolas", 22, bold=True)
font_sm       = pygame.font.SysFont("consolas", 14)
font_title_lg = pygame.font.SysFont("consolas", 90, bold=True)

title_text   = "SLITHER.IO"
title_anim_t = 0.0

WAYPOINTS = [
    (80,   155),
    (1200, 155),
    (1200, 370),
    (80,   370),
]
wp_idx      = 0
snake_x     = float(WAYPOINTS[0][0])
snake_y     = float(WAYPOINTS[0][1])
SNAKE_SPEED = 220.0  


SNAKE_TRAIL    = deque(maxlen=70)
TRAIL_TIMER    = 0.0
TRAIL_INTERVAL = 0.03  

def handle_input():
    keys        = pygame.key.get_pressed()
    mouse_pos   = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    return keys, mouse_pos, mouse_click

def draw_background(surface):
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H
        r = int(10 + (40 - 10) * ratio)
        g = int(15 + (45 - 15) * ratio)
        b = int(20 + (50 - 20) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

def draw_circle(surface, color, pos, radius):
    pygame.draw.circle(surface, color, pos, radius)

def draw_text(surface, text, font, color, pos):
    label = font.render(text, True, color)
    surface.blit(label, pos)

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

def draw_button(surface, text, x, y, w, h, mouse_pos, mouse_click):
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse_pos):
        color = (60, 60, 60)
        if mouse_click[0]:
            return True
    else:
        color = (30, 30, 30)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, (255, 255, 255), rect, 2)
    draw_text(surface, text, font_med, (255, 255, 255), (x + 50, y + 12))
    return False

def update_menu_snake(dt):
    global snake_x, snake_y, wp_idx, TRAIL_TIMER

    tx, ty = WAYPOINTS[wp_idx]
    dx     = tx - snake_x
    dy     = ty - snake_y
    dist   = math.hypot(dx, dy)
    move   = SNAKE_SPEED * dt

    if dist <= move:
        snake_x = float(tx)
        snake_y = float(ty)
        wp_idx  = (wp_idx + 1) % len(WAYPOINTS)
    else:
        snake_x += (dx / dist) * move
        snake_y += (dy / dist) * move

    TRAIL_TIMER += dt
    if TRAIL_TIMER >= TRAIL_INTERVAL:
        TRAIL_TIMER = 0.0
        SNAKE_TRAIL.appendleft((int(snake_x), int(snake_y)))

def draw_menu_snake(surface):
    n = len(SNAKE_TRAIL)
    for i, pos in enumerate(SNAKE_TRAIL):
        ratio  = 1.0 - i / max(n, 1)
        radius = max(2, int(11 * ratio))
        green  = int(80 + 175 * ratio)
        pygame.draw.circle(surface, (0, green, 0), pos, radius)

    hx, hy = int(snake_x), int(snake_y)
    pygame.draw.circle(surface, (180, 255, 180), (hx, hy), 14)


    tx, ty = WAYPOINTS[wp_idx]
    ddx = tx - snake_x
    ddy = ty - snake_y
    dn  = math.hypot(ddx, ddy) or 1
    ex  = int(ddy / dn * 5)
    ey  = int(-ddx / dn * 5)
    fx  = int(ddx / dn * 5)
    fy  = int(ddy / dn * 5)
    pygame.draw.circle(surface, (0, 0, 0), (hx + fx + ex, hy + fy + ey), 3)
    pygame.draw.circle(surface, (0, 0, 0), (hx + fx - ex, hy + fy - ey), 3)

def draw_animated_title(surface, t):
    base_x = SCREEN_W // 2
    base_y = 230

    char_surfaces = []
    total_w = 0
    for ch in title_text:
        surf = font_title_lg.render(ch, True, (255, 255, 255))
        char_surfaces.append(surf)
        total_w += surf.get_width() + 2
    total_w -= 2

    x_cursor = base_x - total_w // 2

    for idx, (ch, surf_ref) in enumerate(zip(title_text, char_surfaces)):
        phase = idx * 0.45
        wave  = math.sin(t * 2.8 + phase)

        y_off     = int(wave * 14)
        green_val = int(180 + 75 * (wave * 0.5 + 0.5))
        red_val   = int(0   + 80 * (wave * 0.5 + 0.5))
        blue_val  = int(0   + 50 * (wave * 0.5 + 0.5))
        color     = (red_val, green_val, blue_val)

        scale  = 1.0 + 0.08 * (wave * 0.5 + 0.5)
        ch_surf = font_title_lg.render(ch, True, color)
        w, h    = ch_surf.get_width(), ch_surf.get_height()
        new_w   = max(1, int(w * scale))
        new_h   = max(1, int(h * scale))
        ch_surf_scaled = pygame.transform.smoothscale(ch_surf, (new_w, new_h))

        shadow_surf   = font_title_lg.render(ch, True, (0, 40, 0))
        shadow_scaled = pygame.transform.smoothscale(shadow_surf, (new_w, new_h))
        cy = base_y + y_off
        surface.blit(shadow_scaled, (x_cursor + 4, cy + 6))
        surface.blit(ch_surf_scaled, (x_cursor, cy))

        x_cursor += surf_ref.get_width() + 2

    if int(t * 1.8) % 2 == 0:
        sub = font_sm.render("by pollini", True, (0, 180, 0))
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, base_y + 100))

def draw_menu(surface, mouse_pos, mouse_click):
    draw_background(surface)
    draw_menu_snake(surface)
    draw_animated_title(surface, title_anim_t)
    if draw_button(surface, "JUGAR", SCREEN_W // 2 - 100, 420, 170, 50, mouse_pos, mouse_click):
        return "play"
    return None

def draw_player_select_menu(surface, mouse_pos, mouse_click):
    draw_background(surface)
    draw_text(surface, "SELECCIONA JUGADORES", font_big, (0, 255, 0), (SCREEN_W // 2 - 250, 200))
    if draw_button(surface, "1 JUGADOR", SCREEN_W // 2 - 100, 350, 200, 50, mouse_pos, mouse_click):
        return "1"
    if draw_button(surface, "2 JUGADORES", SCREEN_W // 2 - 100, 420, 200, 50, mouse_pos, mouse_click):
        return "2"
    return None

game_state       = "menu"
num_players      = 1
game_initialized = False
players          = []

running = True
while running:
    dt      = clock.tick(60) / 1000.0
    running = handle_events()
    keys, mouse_pos, mouse_click = handle_input()

    if game_state == "menu":
        title_anim_t += dt
        update_menu_snake(dt)
        action = draw_menu(screen, mouse_pos, mouse_click)
        if action == "play":
            game_state = "player_select"

    elif game_state == "player_select":
        action = draw_player_select_menu(screen, mouse_pos, mouse_click)
        if action == "1":
            num_players = 1
            game_state  = "game"
        elif action == "2":
            num_players = 2
            game_state  = "game"

    elif game_state == "game":
        if not game_initialized:
            players = []
            for i in range(num_players):
                color = [(0, 255, 0), (255, 0, 0)][i] if i < 2 else (0, 0, 255)
                players.append({'pos': [SCREEN_W // 2 + i * 100, SCREEN_H // 2],
                                'color': color, 'radius': 20})
            game_initialized = True

        for i, player in enumerate(players):
            if i == 0:
                if keys[pygame.K_a]: player['pos'][0] -= 5
                if keys[pygame.K_d]: player['pos'][0] += 5
                if keys[pygame.K_w]: player['pos'][1] -= 5
                if keys[pygame.K_s]: player['pos'][1] += 5
            elif i == 1:
                if keys[pygame.K_LEFT]:  player['pos'][0] -= 5
                if keys[pygame.K_RIGHT]: player['pos'][0] += 5
                if keys[pygame.K_UP]:    player['pos'][1] -= 5
                if keys[pygame.K_DOWN]:  player['pos'][1] += 5

        draw_background(screen)
        for player in players:
            draw_circle(screen, player['color'], player['pos'], player['radius'])
        draw_text(screen, f"jugadores: {num_players}", font_med, (255, 255, 255), (20, 20))

    pygame.display.flip()



pygame.quit()