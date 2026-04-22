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

foods = []
FOOD_RADIUS = 6
FOOD_AMOUNT = 200

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

WORLD_W, WORLD_H = 5000, 5000
BORDER_THICKNESS = 30

MINI_W, MINI_H   = 200, 200
MINI_X, MINI_Y   = SCREEN_W - MINI_W - 15, SCREEN_H - MINI_H - 15
MINI_SCALE_X     = MINI_W / WORLD_W
MINI_SCALE_Y     = MINI_H / WORLD_H

SEGMENT_SPACING   = 10
HEAD_RADIUS       = 14
BASE_BODY_RADIUS  = 10

def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return keys, mouse_pos, False, False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True

    return keys, mouse_pos, mouse_click, True

def draw_background(surface):
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H
        r = int(10 + (40 - 10) * ratio)
        g = int(15 + (45 - 15) * ratio)
        b = int(20 + (50 - 20) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

def bot_ai(player, players, foods):
    px, py = player['pos']

    target = None
    min_dist = float("inf")

    for food in foods:
        dist = (px - food[0])**2 + (py - food[1])**2
        if dist < min_dist:
            min_dist = dist
            target = food

    dx, dy = 0, 0

    if target:
        dx = target[0] - px
        dy = target[1] - py

    margin = 200

    if px < margin:
        dx += 1
    if px > WORLD_W - margin:
        dx -= 1
    if py < margin:
        dy += 1
    if py > WORLD_H - margin:
        dy -= 1

    for other in players:
        if other == player:
            continue

        for seg in list(other['history'])[::4]:  
            dist = math.hypot(px - seg[0], py - seg[1])
            if dist < 80:
                dx += (px - seg[0])
                dy += (py - seg[1])

    return dx, dy
def draw_circle(surface, color, pos, radius):
    pygame.draw.circle(surface, color, pos, radius)

def check_collisions(players):
    dead_players = []

    for player in players:
        hx, hy = player['pos']

        for other in players:
            if other == player:
                continue

            for seg in list(other['history'])[::2]:
                dist = math.hypot(hx - seg[0], hy - seg[1])

                if dist < HEAD_RADIUS:
                    dead_players.append(player)
                    break

            if player in dead_players:
                break

    return dead_players

def draw_text(surface, text, font, color, pos):
    label = font.render(text, True, color)
    surface.blit(label, pos)

def spawn_food():
    margin = 80
    x = random.randint(margin, WORLD_W - margin)
    y = random.randint(margin, WORLD_H - margin)
    color = (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )
    foods.append([x, y, color])

def draw_button(surface, text, x, y, w, h, mouse_pos, mouse_click):
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse_pos):
        color = (60, 60, 60)
        if mouse_click:
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



def make_player(index, color):
    """Create a player dict with segment history."""
    cx = WORLD_W // 2 + index * 150
    cy = WORLD_H // 2
    history = deque()
    for _ in range(80):
        history.append((float(cx), float(cy)))
    return {
        'pos':      [float(cx), float(cy)],
        'angle':    0.0,
        'color':    color,
        'segments': 6,
        'history':  history,
        'dist_acc': 0.0,
        'speed':    200.0,
    }


def player_body_radius(player, seg_idx):
    """Radius tapers from head toward tail."""
    total = player['segments']
    t = seg_idx / max(total - 1, 1)
    return max(4, int(HEAD_RADIUS * (1.0 - 0.45 * t)))


def update_player(player, dx, dy, dt):
    """Move player, record history, clamp to world bounds."""
    speed = player['speed']

    if abs(dx) > 0 or abs(dy) > 0:
        length = math.hypot(dx, dy)
        nx, ny = dx / length, dy / length

        target_angle = math.atan2(ny, nx)

        diff = target_angle - player['angle']

        diff = (diff + math.pi) % (2 * math.pi) - math.pi

        turn_speed = 4.0 

        player['angle'] += diff * min(1, turn_speed * dt)

        move = speed * dt
        new_x = player['pos'][0] + math.cos(player['angle']) * move
        new_y = player['pos'][1] + math.sin(player['angle']) * move


        new_x = max(BORDER_THICKNESS + HEAD_RADIUS,
                    min(WORLD_W - BORDER_THICKNESS - HEAD_RADIUS, new_x))
        new_y = max(BORDER_THICKNESS + HEAD_RADIUS,
                    min(WORLD_H - BORDER_THICKNESS - HEAD_RADIUS, new_y))

        player['dist_acc'] += math.hypot(new_x - player['pos'][0],
        new_y - player['pos'][1])
        player['pos'][0] = new_x
        player['pos'][1] = new_y

        while player['dist_acc'] >= SEGMENT_SPACING:
            player['dist_acc'] -= SEGMENT_SPACING
            player['history'].appendleft((player['pos'][0], player['pos'][1]))


def draw_snake(surface, player, cam_x, cam_y):
    """Draw body segments then head."""
    hist    = list(player['history'])
    total   = player['segments']
    color   = player['color']

    for seg_idx in range(total - 1, 0, -1):
        hist_idx = min(seg_idx * 2, len(hist) - 1)
        wx, wy   = hist[hist_idx]
        sx       = int(wx - cam_x)
        sy       = int(wy - cam_y)
        r        = player_body_radius(player, seg_idx)

        shade = 0.75 if seg_idx % 2 == 0 else 0.9
        body_color = (
            min(255, int(color[0] * shade)),
            min(255, int(color[1] * shade)),
            min(255, int(color[2] * shade)),
        )
        pygame.draw.circle(surface, body_color, (sx, sy), r)
        pygame.draw.circle(surface, (0, 0, 0), (sx, sy), r, 1)

    hx = int(player['pos'][0] - cam_x)
    hy = int(player['pos'][1] - cam_y)
    hr = HEAD_RADIUS

    highlight = (
        min(255, color[0] + 80),
        min(255, color[1] + 80),
        min(255, color[2] + 80),
    )
    pygame.draw.circle(surface, highlight, (hx, hy), hr)
    pygame.draw.circle(surface, (0, 0, 0), (hx, hy), hr, 2)

    angle = player['angle']
    eye_offset = 5
    perp = angle + math.pi / 2
    for side in (-1, 1):
        ex = int(hx + math.cos(perp) * eye_offset * side + math.cos(angle) * 6)
        ey = int(hy + math.sin(perp) * eye_offset * side + math.sin(angle) * 6)
        pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 3)
        pygame.draw.circle(surface, (0, 0, 0), (ex, ey), 1)


def draw_world_border(surface, cam_x, cam_y):
    """Draw the world boundary walls."""
    pygame.draw.rect(surface, (180, 50, 50),
    (0 - cam_x, 0 - cam_y, WORLD_W, BORDER_THICKNESS))
    pygame.draw.rect(surface, (180, 50, 50),
    (0 - cam_x, WORLD_H - BORDER_THICKNESS - cam_y, WORLD_W, BORDER_THICKNESS))
    pygame.draw.rect(surface, (180, 50, 50),
    (0 - cam_x, 0 - cam_y, BORDER_THICKNESS, WORLD_H))
    pygame.draw.rect(surface, (180, 50, 50),
    (WORLD_W - BORDER_THICKNESS - cam_x, 0 - cam_y, BORDER_THICKNESS, WORLD_H))

    glow = (220, 80, 80)
    t = BORDER_THICKNESS
    pygame.draw.rect(surface, glow,
                     (0 - cam_x, 0 - cam_y, WORLD_W, t), 3)
    pygame.draw.rect(surface, glow,
                     (0 - cam_x, WORLD_H - t - cam_y, WORLD_W, t), 3)
    pygame.draw.rect(surface, glow,
                     (0 - cam_x, 0 - cam_y, t, WORLD_H), 3)
    pygame.draw.rect(surface, glow,
                     (WORLD_W - t - cam_x, 0 - cam_y, t, WORLD_H), 3)


def draw_grid(surface, cam_x, cam_y):
    """Faint grid lines to give sense of movement."""
    grid_size = 100
    grid_color = (25, 35, 30)
    start_x = int(cam_x // grid_size) * grid_size
    start_y = int(cam_y // grid_size) * grid_size
    for gx in range(start_x, int(cam_x) + SCREEN_W + grid_size, grid_size):
        sx = gx - int(cam_x)
        pygame.draw.line(surface, grid_color, (sx, 0), (sx, SCREEN_H))
    for gy in range(start_y, int(cam_y) + SCREEN_H + grid_size, grid_size):
        sy = gy - int(cam_y)
        pygame.draw.line(surface, grid_color, (0, sy), (SCREEN_W, sy))


def draw_minimap(surface, players, foods):
    """Draw a small overview minimap in the corner."""
    mini_surf = pygame.Surface((MINI_W, MINI_H), pygame.SRCALPHA)
    mini_surf.fill((0, 0, 0, 160))

    pygame.draw.rect(mini_surf, (80, 200, 80), (0, 0, MINI_W, MINI_H), 2)

    for food in foods:
        mx = int(food[0] * MINI_SCALE_X)
        my = int(food[1] * MINI_SCALE_Y)
        mini_surf.set_at((max(0, min(MINI_W-1, mx)), max(0, min(MINI_H-1, my))),
                          food[2])

    for player in players:
        mx = int(player['pos'][0] * MINI_SCALE_X)
        my = int(player['pos'][1] * MINI_SCALE_Y)
        pygame.draw.circle(mini_surf, player['color'], (mx, my), 4)
        pygame.draw.circle(mini_surf, (255, 255, 255), (mx, my), 4, 1)

    cam_x = players[0]['pos'][0] - SCREEN_W // 2
    cam_y = players[0]['pos'][1] - SCREEN_H // 2
    vx = int(cam_x * MINI_SCALE_X)
    vy = int(cam_y * MINI_SCALE_Y)
    vw = int(SCREEN_W * MINI_SCALE_X)
    vh = int(SCREEN_H * MINI_SCALE_Y)
    pygame.draw.rect(mini_surf, (255, 255, 100),
                     (vx, vy, vw, vh), 1)

    surface.blit(mini_surf, (MINI_X, MINI_Y))

    label = font_sm.render("MAPA", True, (0, 220, 0))
    surface.blit(label, (MINI_X + 4, MINI_Y - 18))

game_state       = "menu"
num_players      = 1
game_initialized = False
players          = []

running = True
while running:
    dt = clock.tick(60) / 1000.0
    keys, mouse_pos, mouse_click, running = handle_input()
    if game_state == "menu":
        title_anim_t += dt
        update_menu_snake(dt)
        action = draw_menu(screen, mouse_pos, mouse_click)
        if action == "play":
            pygame.event.clear()
            game_state = "player_select"
    elif game_state == "player_select":
        action = draw_player_select_menu(screen, mouse_pos, mouse_click)
        if action == "1":
            pygame.event.clear()
            num_players = 1
            game_state = "game"
        elif action == "2":
            pygame.event.clear()
            num_players = 2
            game_state = "game"
    elif game_state == "game":
        if not game_initialized:
            players = []
            colors = [(0, 220, 0), (220, 0, 0), (0, 80, 220)]
            TOTAL_PLAYERS = 6  
            for i in range(TOTAL_PLAYERS):
                p = make_player(i, colors[i % len(colors)])
                if i < num_players:
                    p['is_bot'] = False
                else:
                    p['is_bot'] = True

                players.append(p)

            foods.clear()
            for _ in range(FOOD_AMOUNT):
                spawn_food()

            game_initialized = True
        for i, player in enumerate(players):

            if player.get('is_bot'):
                dx, dy = bot_ai(player, players, foods)

            else:
                dx, dy = 0, 0

                if i == 0:
                    if keys[pygame.K_a]: dx -= 1
                    if keys[pygame.K_d]: dx += 1
                    if keys[pygame.K_w]: dy -= 1
                    if keys[pygame.K_s]: dy += 1

                elif i == 1:
                    if keys[pygame.K_LEFT]:  dx -= 1
                    if keys[pygame.K_RIGHT]: dx += 1
                    if keys[pygame.K_UP]:    dy -= 1
                    if keys[pygame.K_DOWN]:  dy += 1

            update_player(player, dx, dy, dt)
        dead = check_collisions(players)
        for p in dead:
            if p in players:
                players.remove(p)
        for player in players:
            head_x, head_y = player['pos']
            eat_radius = HEAD_RADIUS + FOOD_RADIUS
            for food in foods[:]:
                dist = math.hypot(head_x - food[0], head_y - food[1])
                if dist < eat_radius:
                    foods.remove(food)
                    spawn_food()
                    player['segments'] += 1
                    new_max = player['segments'] * 2 + 20
                    old_list = list(player['history'])
                    player['history'] = deque(old_list, maxlen=new_max)

        cam_x = players[0]['pos'][0] - SCREEN_W // 2
        cam_y = players[0]['pos'][1] - SCREEN_H // 2

        screen.fill((12, 18, 14))
        draw_grid(screen, cam_x, cam_y)
        draw_world_border(screen, cam_x, cam_y)

        for food in foods:
            sx = int(food[0] - cam_x)
            sy = int(food[1] - cam_y)
            if -FOOD_RADIUS < sx < SCREEN_W + FOOD_RADIUS and \
               -FOOD_RADIUS < sy < SCREEN_H + FOOD_RADIUS:
                pygame.draw.circle(screen, food[2], (sx, sy), FOOD_RADIUS)
                pygame.draw.circle(screen, (255, 255, 255),
                                   (sx - 2, sy - 2), max(1, FOOD_RADIUS // 3))

        for player in players:
            draw_snake(screen, player, cam_x, cam_y)

        draw_text(screen, f"Segmentos: {players[0]['segments']}", font_med,
            (200, 255, 200), (20, 20))
        if num_players == 2:
            draw_text(screen, f"J2 segs: {players[1]['segments']}", font_med,
            (255, 180, 180), (20, 50))

        draw_minimap(screen, players, foods)

    pygame.display.flip()

pygame.quit()