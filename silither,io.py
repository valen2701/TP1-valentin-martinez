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
font_tiny     = pygame.font.SysFont("consolas", 12)
font_gameover = pygame.font.SysFont("consolas", 72, bold=True)
font_score    = pygame.font.SysFont("consolas", 28, bold=True)

title_text   = "SLITHER.IO"
title_anim_t = 0.0

foods = []
FOOD_RADIUS = 6
FOOD_AMOUNT = 300

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

MINI_W, MINI_H   = 180, 180
MINI_SCALE_X     = MINI_W / WORLD_W
MINI_SCALE_Y     = MINI_H / WORLD_H

SEGMENT_SPACING   = 10
HEAD_RADIUS       = 14
BASE_BODY_RADIUS  = 10

TURBO_SPEED          = 380.0
TURBO_DRAIN_RATE     = 8.0 
TURBO_TRAIL_INTERVAL = 0.08 
TURBO_MIN_SEGS       = 4 

COLOR_PALETTES = {
    "Verde":     {"primary": (0, 220, 60),   "secondary": (0, 160, 40),   "glow": (80, 255, 120)},
    "Rojo":      {"primary": (220, 50, 50),  "secondary": (160, 30, 30),  "glow": (255, 100, 100)},
    "Azul":      {"primary": (40, 120, 255), "secondary": (20, 80, 200),  "glow": (100, 160, 255)},
    "Naranja":   {"primary": (255, 140, 0),  "secondary": (200, 100, 0),  "glow": (255, 190, 80)},
    "Violeta":   {"primary": (160, 50, 220), "secondary": (110, 20, 160), "glow": (200, 120, 255)},
    "Cian":      {"primary": (0, 210, 210),  "secondary": (0, 150, 160),  "glow": (80, 255, 255)},
    "Dorado":    {"primary": (220, 190, 0),  "secondary": (160, 130, 0),  "glow": (255, 230, 80)},
    "Rosa":      {"primary": (240, 80, 160), "secondary": (180, 40, 110), "glow": (255, 150, 200)},
}
PALETTE_NAMES = list(COLOR_PALETTES.keys())

player_color_choice = [0, 2, 0, 5]

game_state       = "menu"
num_players      = 1
game_initialized = False
players          = []

last_num_players = 1
last_color_choices = [0, 2, 0, 5]

viewport_rects   = []
viewport_surfaces = []

def get_viewport_layout(num_humans):
    """Devuelve lista de pygame.Rect para cada viewport según cantidad de humanos."""
    if num_humans == 1:
        return [pygame.Rect(0, 0, SCREEN_W, SCREEN_H)]
    elif num_humans == 2:
        return [
            pygame.Rect(0, 0, SCREEN_W // 2, SCREEN_H),
            pygame.Rect(SCREEN_W // 2, 0, SCREEN_W // 2, SCREEN_H),
        ]
    elif num_humans == 3:
        return [
            pygame.Rect(0, 0, SCREEN_W // 2, SCREEN_H // 2),
            pygame.Rect(SCREEN_W // 2, 0, SCREEN_W // 2, SCREEN_H // 2),
            pygame.Rect(0, SCREEN_H // 2, SCREEN_W, SCREEN_H // 2),
        ]
    else:  
        return [
            pygame.Rect(0, 0, SCREEN_W // 2, SCREEN_H // 2),
            pygame.Rect(SCREEN_W // 2, 0, SCREEN_W // 2, SCREEN_H // 2),
            pygame.Rect(0, SCREEN_H // 2, SCREEN_W // 2, SCREEN_H // 2),
            pygame.Rect(SCREEN_W // 2, SCREEN_H // 2, SCREEN_W // 2, SCREEN_H // 2),
        ]


def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed() 
    mouse_click = False
    events = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return keys, mouse_pos, mouse_buttons, False, False, []
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True
        events.append(event)

    return keys, mouse_pos, mouse_buttons, mouse_click, True, events

def draw_background(surface):
    sw = surface.get_width()
    sh = surface.get_height()
    for y in range(0, sh, 4):
        ratio = y / sh
        r = int(10 + (40 - 10) * ratio)
        g = int(15 + (45 - 15) * ratio)
        b = int(20 + (50 - 20) * ratio)
        pygame.draw.rect(surface, (r, g, b), (0, y, sw, 4))

def bot_ai(player, players, foods, dt):
    px, py = player['pos']

    player.setdefault('target_timer', 0.0)
    player.setdefault('target_food', None)
    player.setdefault('danger_timer', 0.0)
    player.setdefault('wander_noise', random.uniform(-0.5, 0.5))

    player['target_timer'] -= dt
    player['danger_timer'] -= dt

    DANGER_RADIUS = 110

    danger_angle = None
    closest_threat = float('inf')

    for other in players:
        if other is player or not other.get('alive', True):
            continue
        for seg in list(other['history'])[::6]:
            dist = math.hypot(px - seg[0], py - seg[1])
            if dist < closest_threat:
                closest_threat = dist
                if dist < DANGER_RADIUS:
                    danger_angle = math.atan2(py - seg[1], px - seg[0])

    border_margin = 120
    border_angle = None
    if px < border_margin:
        border_angle = 0.0
    elif px > WORLD_W - border_margin:
        border_angle = math.pi
    elif py < border_margin:
        border_angle = math.pi / 2
    elif py > WORLD_H - border_margin:
        border_angle = -math.pi / 2

    ignore_danger = random.random() < 0.20
    if danger_angle is not None and closest_threat < DANGER_RADIUS and not ignore_danger:
        target_angle = danger_angle
    elif border_angle is not None:
        target_angle = border_angle
    else:

        if player['target_food'] is None or player['target_timer'] <= 0:
            best_food = None
            best_score = float('inf')
            sample = random.sample(foods, min(6, len(foods))) if foods else []
            for f in sample:
                dist_to_food = math.hypot(px - f[0], py - f[1])
                if dist_to_food < best_score:
                    best_score = dist_to_food
                    best_food = f
            player['target_food'] = best_food
            player['target_timer'] = random.uniform(0.3, 1.0)

        if player['target_food'] is None:
            return 0
        target = player['target_food']
        dx = target[0] - px
        dy = target[1] - py
        if math.hypot(dx, dy) < 40:
            player['target_food'] = None
            return 0
        target_angle = math.atan2(dy, dx)

    diff = target_angle - player['angle']
    diff = (diff + math.pi) % (2 * math.pi) - math.pi

    if abs(diff) < 0.18:
        return 0

    if random.random() < 0.008:
        player['wander_noise'] = random.uniform(-0.6, 0.6)
    intensity = 0.65 + player['wander_noise'] * 0.15
    return intensity if diff > 0 else -intensity

def draw_snake_on(surface, player, cam_x, cam_y, vw, vh):
    """Dibuja la serpiente en 'surface' usando la cámara dada."""
    hist   = list(player['history'])
    total = int(player['segments'])
    color  = player['color']
    color2 = player['color_sec']
    glow   = player['color_glow']

    for seg_idx in range(total - 1, 0, -1):
        hist_idx = min(seg_idx * 2, len(hist) - 1)
        wx, wy   = hist[hist_idx]
        sx = int(wx - cam_x)
        sy = int(wy - cam_y)

        t = seg_idx / max(total - 1, 1)
        r = max(4, int(HEAD_RADIUS * (1.0 - 0.45 * t)))

        if sx < -r or sx > vw + r or sy < -r or sy > vh + r:
            continue

        even = seg_idx % 2 == 0
        base_col = color if even else color2
        tail_t = seg_idx / max(total - 1, 1)
        fade   = 1.0 - 0.35 * tail_t
        body_col = tuple(max(0, min(255, int(c * fade))) for c in base_col)

        pygame.draw.circle(surface, (0, 0, 0), (sx + 2, sy + 2), r)
        pygame.draw.circle(surface, body_col, (sx, sy), r)
        pygame.draw.circle(surface, (0, 0, 0), (sx, sy), r, 1)
        if r > 5:
            shine_r = max(1, r // 3)
            shine_col = tuple(min(255, c + 80) for c in body_col)
            pygame.draw.circle(surface, shine_col, (sx - r // 3, sy - r // 3), shine_r)
            if even and r > 7:
                pygame.draw.circle(surface, (255, 255, 255), (sx - r // 4, sy - r // 4), max(1, r // 5))

    hx = int(player['pos'][0] - cam_x)
    hy = int(player['pos'][1] - cam_y)
    hr = HEAD_RADIUS
    glow_surf = pygame.Surface((hr * 6, hr * 6), pygame.SRCALPHA)
    glow_alpha = 100 if player.get('turbo', False) else 60
    glow_r = hr * 3 if player.get('turbo', False) else hr * 2
    pygame.draw.circle(glow_surf, (*glow, glow_alpha), (hr * 3, hr * 3), glow_r)
    surface.blit(glow_surf, (hx - hr * 3, hy - hr * 3))

    if player.get('turbo', False):
        angle = player['angle']
        for _ in range(3):
            offset = random.uniform(10, 25)
            spread = random.uniform(-0.5, 0.5)
            px_t = int(hx - math.cos(angle + spread) * offset)
            py_t = int(hy - math.sin(angle + spread) * offset)
            r_p = random.randint(2, 5)
            alpha_c = random.randint(100, 200)
            spark_col = tuple(min(255, c + 60) for c in glow)
            if 0 < px_t < vw and 0 < py_t < vh:
                pygame.draw.circle(surface, spark_col, (px_t, py_t), r_p)

    pygame.draw.circle(surface, (0, 0, 0), (hx + 2, hy + 2), hr)
    pygame.draw.circle(surface, color, (hx, hy), hr)
    highlight = tuple(min(255, c + 100) for c in color)
    pygame.draw.circle(surface, highlight, (hx - 4, hy - 4), hr // 2)
    pygame.draw.circle(surface, (255, 255, 255), (hx - 5, hy - 5), max(2, hr // 4))
    pygame.draw.circle(surface, (0, 0, 0), (hx, hy), hr, 2)

    angle = player['angle']
    perp  = angle + math.pi / 2
    for side in (-1, 1):
        ex = int(hx + math.cos(perp) * 5 * side + math.cos(angle) * 7)
        ey = int(hy + math.sin(perp) * 5 * side + math.sin(angle) * 7)
        pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 4)
        px2 = int(ex + math.cos(angle) * 1.5)
        py2 = int(ey + math.sin(angle) * 1.5)
        pygame.draw.circle(surface, (0, 0, 0), (px2, py2), 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, ey - 1), 1)

    name_lbl = font_tiny.render(player['name'], True, glow)
    surface.blit(name_lbl, (hx - name_lbl.get_width() // 2, hy - hr - 16))

def draw_world_border(surface, cam_x, cam_y):
    t = BORDER_THICKNESS
    pygame.draw.rect(surface, (180, 50, 50), (0 - cam_x, 0 - cam_y, WORLD_W, t))
    pygame.draw.rect(surface, (180, 50, 50), (0 - cam_x, WORLD_H - t - cam_y, WORLD_W, t))
    pygame.draw.rect(surface, (180, 50, 50), (0 - cam_x, 0 - cam_y, t, WORLD_H))
    pygame.draw.rect(surface, (180, 50, 50), (WORLD_W - t - cam_x, 0 - cam_y, t, WORLD_H))
    glow = (220, 80, 80)
    pygame.draw.rect(surface, glow, (0 - cam_x, 0 - cam_y, WORLD_W, t), 3)
    pygame.draw.rect(surface, glow, (0 - cam_x, WORLD_H - t - cam_y, WORLD_W, t), 3)
    pygame.draw.rect(surface, glow, (0 - cam_x, 0 - cam_y, t, WORLD_H), 3)
    pygame.draw.rect(surface, glow, (WORLD_W - t - cam_x, 0 - cam_y, t, WORLD_H), 3)


def draw_grid(surface, cam_x, cam_y):
    grid_size  = 100
    grid_color = (25, 35, 30)
    sw = surface.get_width()
    sh = surface.get_height()
    start_x = int(cam_x // grid_size) * grid_size
    start_y = int(cam_y // grid_size) * grid_size
    for gx in range(start_x, int(cam_x) + sw + grid_size, grid_size):
        pygame.draw.line(surface, grid_color, (gx - int(cam_x), 0),
                         (gx - int(cam_x), sh))
    for gy in range(start_y, int(cam_y) + sh + grid_size, grid_size):
        pygame.draw.line(surface, grid_color, (0, gy - int(cam_y)),
                         (sw, gy - int(cam_y)))


def draw_minimap(surface, players, foods, focus_player, mx, my):
    mini_surf = pygame.Surface((MINI_W, MINI_H), pygame.SRCALPHA)
    mini_surf.fill((0, 0, 0, 160))
    pygame.draw.rect(mini_surf, (80, 200, 80), (0, 0, MINI_W, MINI_H), 2)

    for food in foods:
        fx2 = int(food[0] * MINI_SCALE_X)
        fy2 = int(food[1] * MINI_SCALE_Y)
        mini_surf.set_at(
            (max(0, min(MINI_W - 1, fx2)), max(0, min(MINI_H - 1, fy2))),
            food[2]
        )

    for player in players:
        pmx = int(player['pos'][0] * MINI_SCALE_X)
        pmy = int(player['pos'][1] * MINI_SCALE_Y)
        pygame.draw.circle(mini_surf, player['color'], (pmx, pmy), 4)
        pygame.draw.circle(mini_surf, (255, 255, 255), (pmx, pmy), 4, 1)

    if focus_player:
        vw = surface.get_width()
        vh = surface.get_height()
        cam_x = focus_player['pos'][0] - vw // 2
        cam_y = focus_player['pos'][1] - vh // 2
        vx = int(cam_x * MINI_SCALE_X)
        vy = int(cam_y * MINI_SCALE_Y)
        vw2 = int(vw * MINI_SCALE_X)
        vh2 = int(vh * MINI_SCALE_Y)
        pygame.draw.rect(mini_surf, (255, 255, 100), (vx, vy, vw2, vh2), 1)

    surface.blit(mini_surf, (mx, my))
    label = font_tiny.render("MAPA", True, (0, 220, 0))
    surface.blit(label, (mx + 4, my - 16))


def check_collisions(players):
    """
    Colisión cabeza vs cuerpo de OTRA serpiente.
    Hitbox correcta: distancia entre centros < HEAD_RADIUS + radio_segmento_enemigo
    """
    dead_players = []

    for player in players:
        if player in dead_players:
            continue
        hx, hy = player['pos']

        if (hx < BORDER_THICKNESS + HEAD_RADIUS or
            hx > WORLD_W - BORDER_THICKNESS - HEAD_RADIUS or
            hy < BORDER_THICKNESS + HEAD_RADIUS or
            hy > WORLD_H - BORDER_THICKNESS - HEAD_RADIUS):
            dead_players.append(player)
            continue

        for other in players:
            if other is player or other in dead_players:
                continue

            total_segs = int(other['segments'])
            hist_other = list(other['history'])

            ox, oy = other['pos']
            if math.hypot(hx - ox, hy - oy) < HEAD_RADIUS * 2 - 2:
                dead_players.append(player)
                break

            for seg_idx in range(total_segs - 1, 0, -1):
                hist_idx = min(seg_idx * 2, len(hist_other) - 1)
                sx, sy = hist_other[hist_idx]
                t = seg_idx / max(total_segs - 1, 1)
                seg_r = max(4, int(HEAD_RADIUS * (1.0 - 0.45 * t)))

                if math.hypot(hx - sx, hy - sy) < HEAD_RADIUS + seg_r - 2:
                    dead_players.append(player)
                    break
            if player in dead_players:
                break

    return dead_players

def make_player(index, palette_name, is_bot=True):
    margin = 300
    cx = random.randint(margin, WORLD_W - margin)
    cy = random.randint(margin, WORLD_H - margin)
    history = deque(maxlen=500)
    for _ in range(80):
        history.append((float(cx), float(cy)))
    pal = COLOR_PALETTES[palette_name]
    return {
        'pos':          [float(cx), float(cy)],
        'angle':        random.uniform(0, math.pi * 2),
        'palette':      palette_name,
        'color':        pal["primary"],
        'color_sec':    pal["secondary"],
        'color_glow':   pal["glow"],
        'segments':     6,
        'history':      history,
        'dist_acc':     0.0,
        'speed':        200.0,
        'is_bot':       is_bot,
        'target_food':  None,
        'target_timer': 0.0,
        'danger_timer': 0.0,
        'name':         f"BOT{index+1}" if is_bot else f"J{index+1}",
        'alive':        True,
        'score':        0,
        'respawn_timer': 0.0,
        'turbo':        False,
        'turbo_trail_t': 0.0,
        'seg_drain_acc': 0.0,
        'player_slot':  index,
    }


def respawn_bot(player, index, palette_name):
    """Respawnea un bot en una zona aleatoria."""
    margin = 400
    cx = random.randint(margin, WORLD_W - margin)
    cy = random.randint(margin, WORLD_H - margin)
    history = deque(maxlen=500)
    for _ in range(80):
        history.append((float(cx), float(cy)))
    pal = COLOR_PALETTES[palette_name]
    player['pos']          = [float(cx), float(cy)]
    player['angle']        = random.uniform(0, math.pi * 2)
    player['segments']     = 6
    player['history']      = history
    player['dist_acc']     = 0.0
    player['speed']        = 200.0
    player['target_food']  = None
    player['target_timer'] = 0.0
    player['danger_timer'] = 0.0
    player['alive']        = True
    player['respawn_timer'] = 0.0
    player['turbo']         = False
    player['turbo_trail_t'] = 0.0
    player['seg_drain_acc'] = 0.0


def update_player(player, turn, dt, turbo_active=False):
    turn_speed = 3.2
    player['angle'] += turn * turn_speed * dt


    using_turbo = turbo_active and player['score'] > 0
    player['turbo'] = using_turbo

    speed = TURBO_SPEED if using_turbo else player['speed']
    move  = speed * dt
    new_x = player['pos'][0] + math.cos(player['angle']) * move
    new_y = player['pos'][1] + math.sin(player['angle']) * move
    player['dist_acc'] += math.hypot(new_x - player['pos'][0],
                                     new_y - player['pos'][1])
    player['pos'][0] = new_x
    player['pos'][1] = new_y
    while player['dist_acc'] >= SEGMENT_SPACING:
        player['dist_acc'] -= SEGMENT_SPACING
        player['history'].appendleft((player['pos'][0], player['pos'][1]))

    if using_turbo:
        player['seg_drain_acc'] += TURBO_DRAIN_RATE * dt
        player['turbo_trail_t'] += dt

        if player['turbo_trail_t'] >= TURBO_TRAIL_INTERVAL:
            player['turbo_trail_t'] = 0.0

            angle = player['angle'] + math.pi
            dist = random.uniform(20, 40)
            fx = player['pos'][0] + math.cos(angle) * dist
            fy = player['pos'][1] + math.sin(angle) * dist

            rc, gc, bc = player['color']
            food_color = (min(255, rc+40), min(255, gc+40), min(255, bc+40))

            foods.append([fx, fy, food_color])

        while player['seg_drain_acc'] >= 1.0:
            player['seg_drain_acc'] -= 1.0
            player['score'] = max(0, player['score'] - 1)
            if player['score'] == 0:
                player['turbo'] = False
                break
    else:
        player['seg_drain_acc'] = 0.0
        player['turbo_trail_t'] = 0.0
        player['turbo'] = False

def spawn_food():
    margin = 80
    x = random.randint(margin, WORLD_W - margin)
    y = random.randint(margin, WORLD_H - margin)
    hue = random.random()
    hi = int(hue * 6)
    f  = hue * 6 - hi
    q  = int((1 - f) * 255)
    t2 = int(f * 255)
    v  = 230
    rgb_map = [
        (v, t2, 0), (q, v, 0), (0, v, t2),
        (0, q, v),  (t2, 0, v), (v, 0, q),
    ]
    color = rgb_map[hi % 6]
    foods.append([x, y, color])

def draw_button(surface, text, x, y, w, h, mouse_pos, mouse_click,
                color_idle=(30, 40, 35), color_hover=(55, 75, 60),
                border_color=(0, 200, 80)):
    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse_pos)
    col = color_hover if hovered else color_idle
    pygame.draw.rect(surface, col, rect, border_radius=6)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)
    lbl = font_med.render(text, True, (255, 255, 255))
    lx  = x + (w - lbl.get_width()) // 2
    ly  = y + (h - lbl.get_height()) // 2
    surface.blit(lbl, (lx, ly))
    return hovered and mouse_click


def draw_text(surface, text, font, color, pos):
    label = font.render(text, True, color)
    surface.blit(label, pos)


def update_menu_snake(dt):
    global snake_x, snake_y, wp_idx, TRAIL_TIMER
    tx, ty = WAYPOINTS[wp_idx]
    dx = tx - snake_x; dy = ty - snake_y
    dist = math.hypot(dx, dy)
    move = SNAKE_SPEED * dt
    if dist <= move:
        snake_x = float(tx); snake_y = float(ty)
        wp_idx = (wp_idx + 1) % len(WAYPOINTS)
    else:
        snake_x += (dx / dist) * move
        snake_y += (dy / dist) * move
    TRAIL_TIMER += dt
    if TRAIL_TIMER >= TRAIL_INTERVAL:
        TRAIL_TIMER = 0.0
        SNAKE_TRAIL.appendleft((int(snake_x), int(snake_y)))


def draw_menu_snake(surface):
    """Serpiente del menú con mismo estilo que en el juego."""
    n = len(SNAKE_TRAIL)
    for i, pos in enumerate(SNAKE_TRAIL):
        ratio  = 1.0 - i / max(n, 1)
        t_fade = i / max(n - 1, 1)
        r_seg  = max(4, int(HEAD_RADIUS * (1.0 - 0.45 * t_fade)))

        even = i % 2 == 0
        green_base = int(80 + 175 * ratio)
        green_sec  = int(60 + 100 * ratio)
        base_col = (0, green_base, 0) if even else (0, green_sec, 0)

        pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 2, pos[1] + 2), r_seg)
        pygame.draw.circle(surface, base_col, pos, r_seg)
        pygame.draw.circle(surface, (0, 0, 0), pos, r_seg, 1)
        if r_seg > 5:
            shine = (min(255, green_base + 80), 255, min(255, green_base + 80))
            pygame.draw.circle(surface, shine,
                               (pos[0] - r_seg // 3, pos[1] - r_seg // 3),
                               max(1, r_seg // 3))
            if even and r_seg > 7:
                pygame.draw.circle(surface, (255, 255, 255),
                                   (pos[0] - r_seg // 4, pos[1] - r_seg // 4),
                                   max(1, r_seg // 5))

    hx, hy = int(snake_x), int(snake_y)
    hr = HEAD_RADIUS
    color = (0, 220, 60)
    glow  = (80, 255, 120)

    glow_surf = pygame.Surface((hr * 5, hr * 5), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*glow, 60), (hr * 2 + 2, hr * 2 + 2), hr * 2)
    surface.blit(glow_surf, (hx - hr * 2 - 2, hy - hr * 2 - 2))

    pygame.draw.circle(surface, (0, 0, 0), (hx + 2, hy + 2), hr)
    pygame.draw.circle(surface, color, (hx, hy), hr)
    pygame.draw.circle(surface, (100, 255, 140), (hx - 4, hy - 4), hr // 2)
    pygame.draw.circle(surface, (255, 255, 255), (hx - 5, hy - 5), max(2, hr // 4))
    pygame.draw.circle(surface, (0, 0, 0), (hx, hy), hr, 2)

    tx2, ty2 = WAYPOINTS[wp_idx]
    ddx = tx2 - snake_x; ddy = ty2 - snake_y
    dn  = math.hypot(ddx, ddy) or 1
    angle = math.atan2(ddy, ddx)
    perp  = angle + math.pi / 2
    for side in (-1, 1):
        ex = int(hx + math.cos(perp) * 5 * side + math.cos(angle) * 7)
        ey = int(hy + math.sin(perp) * 5 * side + math.sin(angle) * 7)
        pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 4)
        px2 = int(ex + math.cos(angle) * 1.5)
        py2 = int(ey + math.sin(angle) * 1.5)
        pygame.draw.circle(surface, (0, 0, 0), (px2, py2), 2)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 1, ey - 1), 1)


def draw_animated_title(surface, t):
    base_x = SCREEN_W // 2; base_y = 200
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
        y_off = int(wave * 14)
        green_val = int(180 + 75 * (wave * 0.5 + 0.5))
        red_val   = int(0   + 80 * (wave * 0.5 + 0.5))
        blue_val  = int(0   + 50 * (wave * 0.5 + 0.5))
        color = (red_val, green_val, blue_val)
        scale = 1.0 + 0.08 * (wave * 0.5 + 0.5)
        ch_surf = font_title_lg.render(ch, True, color)
        w, h    = ch_surf.get_width(), ch_surf.get_height()
        new_w   = max(1, int(w * scale)); new_h = max(1, int(h * scale))
        ch_surf_scaled = pygame.transform.smoothscale(ch_surf, (new_w, new_h))
        shadow_surf    = font_title_lg.render(ch, True, (0, 40, 0))
        shadow_scaled  = pygame.transform.smoothscale(shadow_surf, (new_w, new_h))
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
    if draw_button(surface, "JUGAR", SCREEN_W // 2 - 100, 430, 200, 52, mouse_pos, mouse_click):
        return "play"
    return None

def draw_player_select_menu(surface, mouse_pos, mouse_click):
    draw_background(surface)
    draw_text(surface, "CANTIDAD DE JUGADORES", font_big, (0, 255, 80),
              (SCREEN_W // 2 - 310, 160))
    options = [("1 JUGADOR", "1"), ("2 JUGADORES", "2"),
               ("3 JUGADORES", "3"), ("4 JUGADORES", "4")]
    cy = 280
    for label, val in options:
        if draw_button(surface, label, SCREEN_W // 2 - 120, cy, 240, 50,
                       mouse_pos, mouse_click):
            return val
        cy += 70
    return None


def draw_color_select_menu(surface, mouse_pos, mouse_click, events, num_players):
    draw_background(surface)
    draw_text(surface, "ELIGE TU COLOR", font_big, (0, 255, 80),
              (SCREEN_W // 2 - 200, 80))

    player_labels     = ["JUGADOR 1", "JUGADOR 2", "JUGADOR 3", "JUGADOR 4"]
    player_keys_left  = [pygame.K_a, pygame.K_LEFT,  pygame.K_j, pygame.K_KP4]
    player_keys_right = [pygame.K_d, pygame.K_RIGHT, pygame.K_l, pygame.K_KP6]

    key_pressed = set()
    for event in events:
        if event.type == pygame.KEYDOWN:
            key_pressed.add(event.key)

    BOX_W, BOX_H = 80, 80
    COLS = len(PALETTE_NAMES)
    total_palette_w = COLS * (BOX_W + 8) - 8
    start_x = SCREEN_W // 2 - total_palette_w // 2

    for pi in range(num_players):
        row_y = 160 + pi * 130
        draw_text(surface, player_labels[pi], font_med, (200, 255, 200),
                  (start_x, row_y))

        kl = player_keys_left[pi]
        kr = player_keys_right[pi]
        if kl in key_pressed:
            player_color_choice[pi] = (player_color_choice[pi] - 1) % len(PALETTE_NAMES)
        if kr in key_pressed:
            player_color_choice[pi] = (player_color_choice[pi] + 1) % len(PALETTE_NAMES)

        for ci, name in enumerate(PALETTE_NAMES):
            bx = start_x + ci * (BOX_W + 8)
            by = row_y + 28
            pal = COLOR_PALETTES[name]
            rect = pygame.Rect(bx, by, BOX_W, BOX_H)

            pygame.draw.rect(surface, pal["secondary"], rect, border_radius=8)
            inner = pygame.Rect(bx + 6, by + 6, BOX_W - 12, BOX_H - 12)
            pygame.draw.rect(surface, pal["primary"], inner, border_radius=5)

            selected = (player_color_choice[pi] == ci)
            border_col = (255, 255, 255) if selected else (60, 80, 60)
            border_w   = 3 if selected else 1
            pygame.draw.rect(surface, border_col, rect, border_w, border_radius=8)

            lbl = font_tiny.render(name, True, (220, 220, 220))
            surface.blit(lbl, (bx + BOX_W // 2 - lbl.get_width() // 2, by + BOX_H + 2))

            if rect.collidepoint(mouse_pos) and mouse_click:
                player_color_choice[pi] = ci

        sel_pal = COLOR_PALETTES[PALETTE_NAMES[player_color_choice[pi]]]
        px_preview = start_x + total_palette_w + 30
        for si in range(8):
            ratio = 1 - si / 8
            r = max(2, int(10 * ratio))
            shade = 0.7 + 0.3 * ratio
            c = tuple(min(255, int(v * shade)) for v in sel_pal["primary"])
            pygame.draw.circle(surface, c,
                               (px_preview - si * 13, row_y + 68), r)
        pygame.draw.circle(surface, sel_pal["glow"],
                           (px_preview, row_y + 68), 11)

    if draw_button(surface, "JUGAR", SCREEN_W // 2 - 80, SCREEN_H - 90,
                   160, 52, mouse_pos, mouse_click):
        return "start"
    hint = font_sm.render("cambia de color con el mouse", True, (100, 180, 100))
    surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 125))
    return None

def draw_game_over(surface, dead_player, mouse_pos, mouse_click):
    """Dibuja la pantalla de game over semitransparente."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    cx = SCREEN_W // 2
    cy = SCREEN_H // 2 - 100

    go_shadow = font_gameover.render("GAME OVER", True, (80, 0, 0))
    surface.blit(go_shadow, (cx - go_shadow.get_width() // 2 + 4, cy + 4))
    go_text = font_gameover.render("GAME OVER", True, (255, 60, 60))
    surface.blit(go_text, (cx - go_text.get_width() // 2, cy))

    if dead_player:
        score_txt = font_score.render(
            f"{dead_player['name']}  —  {dead_player['segments']} segmentos", True, (255, 200, 100))
        surface.blit(score_txt, (cx - score_txt.get_width() // 2, cy + 90))

    rejugar = draw_button(surface, "VOLVER A JUGAR", cx - 130, cy + 150, 260, 54,
                          mouse_pos, mouse_click,
                          color_idle=(30, 50, 30), color_hover=(50, 90, 50),
                          border_color=(0, 220, 80))

    menu_btn = draw_button(surface, "MENÚ PRINCIPAL", cx - 130, cy + 220, 260, 54,
                           mouse_pos, mouse_click,
                           color_idle=(40, 30, 30), color_hover=(80, 50, 50),
                           border_color=(220, 60, 60))

    if rejugar:
        return "rejugar"
    if menu_btn:
        return "menu"
    return None


def draw_hud_on(surface, player, all_players, mini_x, mini_y):
    """HUD por viewport: puntuación propia + turbo + minimap + leaderboard."""
    pal = COLOR_PALETTES[player['palette']]
    segs = player['segments']
    draw_text(surface, f"{player['name']} | Tamaño: {int(segs)} | Score: {int(player['score'])}",
              font_med, pal["glow"], (10, 10))

    if not player['is_bot']:
        turbo_on = player.get('turbo', False)
        can_turbo = player['score'] > 0
        if turbo_on:
            turbo_col = (255, 220, 50)
            turbo_txt = "TURBO"
        elif not can_turbo:
            turbo_col = (120, 60, 60)
            turbo_txt = "turbo agotado"
        else:
            turbo_col = (80, 120, 80)
            turbo_txt = "Mouse Click = Turbo"
        draw_text(surface, turbo_txt, font_sm, turbo_col, (10, 36))

        bar_w = 120
        bar_h = 8
        ratio = min(1.0, max(0.0, player['score'] / max(1, 60)))
        pygame.draw.rect(surface, (40, 40, 40), (10, 54, bar_w, bar_h), border_radius=4)
        bar_fill = max(2, int(bar_w * ratio))
        bar_color = (255, 200, 40) if turbo_on else (0, 180, 80)
        pygame.draw.rect(surface, bar_color, (10, 54, bar_fill, bar_h), border_radius=4)
        pygame.draw.rect(surface, (80, 80, 80), (10, 54, bar_w, bar_h), 1, border_radius=4)

    draw_minimap(surface, all_players, foods, player, mini_x, mini_y)

    sorted_p = sorted(all_players, key=lambda x: x['segments'], reverse=True)[:5]
    lx = mini_x
    ly = 10
    draw_text(surface, "TOP", font_tiny, (0, 200, 80), (lx, ly))
    for rank, p in enumerate(sorted_p):
        col = p['color_glow'] if not p['is_bot'] else (180, 180, 180)
        draw_text(surface, f"{rank+1}. {p['name']:5s} {p['segments']:.0f}",
                  font_tiny, col, (lx, ly + 14 + rank * 14))

PLAYER_KEY_LEFT  = [pygame.K_UNKNOWN, pygame.K_a,      pygame.K_LEFT, pygame.K_j]
PLAYER_KEY_RIGHT = [pygame.K_UNKNOWN, pygame.K_d,      pygame.K_RIGHT, pygame.K_l]
PLAYER_TURBO_KEYS = [pygame.K_UNKNOWN, pygame.K_w, pygame.K_UP, pygame.K_i]

BOT_RESPAWN_TIME = 3.0 

running = True
dead_human_player = None 

vp_surfaces = []
vp_rects    = []

BOT_TOTAL_SINGLE = 12 

while running:
    dt = clock.tick(60) / 1000.0
    keys, mouse_pos, mouse_buttons, mouse_click, running, events = handle_input()
    mouse_left_held = mouse_buttons[0] 

    if game_state == "menu":
        pygame.mouse.set_visible(True)
        title_anim_t += dt
        update_menu_snake(dt)
        action = draw_menu(screen, mouse_pos, mouse_click)
        if action == "play":
            pygame.event.clear()
            game_state = "player_select"

    elif game_state == "player_select":
        action = draw_player_select_menu(screen, mouse_pos, mouse_click)
        if action in ("1", "2", "3", "4"):
            pygame.event.clear()
            num_players = int(action)
            last_num_players = num_players
            if num_players == 1:
                game_state = "game"
                game_initialized = False
            else:
                game_state = "color_select"

    elif game_state == "color_select":
        action = draw_color_select_menu(screen, mouse_pos, mouse_click,
                                        events, num_players)
        if action == "start":
            pygame.event.clear()
            last_color_choices = player_color_choice[:]
            game_state = "game"
            game_initialized = False

    elif game_state == "game":
        pygame.mouse.set_visible(True)
        if not game_initialized:
            dead_human_player = None
            players = []

            if num_players == 1:
                TOTAL_BOTS = BOT_TOTAL_SINGLE
            else:
                TOTAL_BOTS = max(0, 8 - num_players)

            bot_palette_pool = list(PALETTE_NAMES)
            for i in range(num_players):
                chosen = PALETTE_NAMES[player_color_choice[i]]
                if chosen in bot_palette_pool:
                    bot_palette_pool.remove(chosen)
                p = make_player(i, chosen, is_bot=False)
                p['name'] = f"J{i+1}"
                players.append(p)

            random.shuffle(bot_palette_pool)
            bot_palette_pool_extended = bot_palette_pool * 4 
            for i in range(TOTAL_BOTS):
                pal = bot_palette_pool_extended[i % len(bot_palette_pool_extended)]
                p = make_player(num_players + i, pal, is_bot=True)
                players.append(p)

            foods.clear()
            for _ in range(FOOD_AMOUNT):
                spawn_food()

            human_players_list = [p for p in players if not p['is_bot']]
            vp_rects = get_viewport_layout(len(human_players_list))
            vp_surfaces = []
            for rect in vp_rects:
                vp_surfaces.append(pygame.Surface((rect.width, rect.height)))

            game_initialized = True

        human_players_list = [p for p in players if not p['is_bot']]
        bot_players_list   = [p for p in players if p['is_bot']]

        for bot in bot_players_list:
            if not bot.get('alive', True):
                bot['respawn_timer'] -= dt
                if bot['respawn_timer'] <= 0:
                    respawn_bot(bot, 0, bot['palette'])

        active_players = [p for p in players if p.get('alive', True)]

        for i, player in enumerate(players):
            if not player.get('alive', True):
                continue
            if player['is_bot']:
                turn = bot_ai(player, active_players, foods, dt)
                update_player(player, turn, dt, turbo_active=False)
            else:
                player_slot = player['player_slot']

                if player_slot == 0:
                    vr = vp_rects[0] if vp_rects else pygame.Rect(0, 0, SCREEN_W, SCREEN_H)
                    vw0 = vr.width
                    vh0 = vr.height
                    screen_px = player['pos'][0] - (player['pos'][0] - vw0 // 2)
                    screen_py = vh0 // 2
                    mx_rel = mouse_pos[0] - vr.x
                    my_rel = mouse_pos[1] - vr.y
                    dx_m = mx_rel - vw0 // 2
                    dy_m = my_rel - vh0 // 2
                    if abs(dx_m) > 5 or abs(dy_m) > 5:
                        target_angle = math.atan2(dy_m, dx_m)
                        diff = target_angle - player['angle']
                        diff = (diff + math.pi) % (2 * math.pi) - math.pi
                        turn = max(-1.0, min(1.0, diff * 2.5))
                    else:
                        turn = 0
                    turbo_active = mouse_left_held
                else:
                    turn = 0
                    if keys[PLAYER_KEY_LEFT[player_slot]]:
                        turn -= 1
                    if keys[PLAYER_KEY_RIGHT[player_slot]]:
                        turn += 1
                    turbo_key = PLAYER_TURBO_KEYS[player_slot]
                    turbo_active = keys[turbo_key]

                update_player(player, turn, dt, turbo_active=turbo_active)

        dead = check_collisions(active_players)
        for p in dead:
            seg_count = int(p['segments'])
            for _ in range(min(seg_count, 25)):
                fx = p['pos'][0] + random.randint(-80, 80)
                fy = p['pos'][1] + random.randint(-80, 80)
                fx = max(50, min(WORLD_W - 50, fx))
                fy = max(50, min(WORLD_H - 50, fy))
                foods.append([fx, fy, p['color']])

            if p['is_bot']:
                p['alive'] = False
                p['respawn_timer'] = BOT_RESPAWN_TIME
            else:
                if dead_human_player is None:
                    dead_human_player = p
                p['alive'] = False
                players.remove(p)

        alive_players = [p for p in players if p.get('alive', True)]
        for player in alive_players:
            hx2, hy2 = player['pos']
            eat_radius = HEAD_RADIUS + FOOD_RADIUS - 4
            eaten = []
            for food in foods:
                if math.hypot(hx2 - food[0], hy2 - food[1]) < eat_radius:
                    eaten.append(food)
            for food in eaten:
                foods.remove(food)
                spawn_food()
                player['segments'] += 1
                player['score']    += 1
                new_max = int(player['segments'] * 2 + 20)
                old_list = list(player['history'])
                player['history'] = deque(old_list, maxlen=new_max)
                player['speed'] = max(150, 200 - player['segments'] * 0.25)

        screen.fill((12, 18, 14))

        human_alive = [p for p in players if not p['is_bot']]
        render_players = [p for p in players if p.get('alive', True)]

        if not human_alive and dead_human_player is None:
            game_state = "menu"

        if not vp_surfaces or not vp_rects:
            vp_rects = get_viewport_layout(max(1, len(human_alive)))
            vp_surfaces = [pygame.Surface((r.width, r.height)) for r in vp_rects]

        for vi, (vsurf, vrect) in enumerate(zip(vp_surfaces, vp_rects)):
            vw = vrect.width
            vh = vrect.height

            focus = None
            for p in human_alive:
                if p['player_slot'] == vi:
                    focus = p
                    break

            if focus is None:
                vsurf.fill((12, 18, 14))
                dead_msg = font_med.render(f"J{vi+1}: Sin jugador", True, (180, 80, 80))
                vsurf.blit(dead_msg, (vw // 2 - dead_msg.get_width() // 2, vh // 2 - dead_msg.get_height() // 2))
                screen.blit(vsurf, (vrect.x, vrect.y))
                continue

            cam_x = focus['pos'][0] - vw // 2
            cam_y = focus['pos'][1] - vh // 2

            draw_background(vsurf)
            draw_grid(vsurf, cam_x, cam_y)
            draw_world_border(vsurf, cam_x, cam_y)

            for food in foods:
                sx = int(food[0] - cam_x)
                sy = int(food[1] - cam_y)
                if -FOOD_RADIUS < sx < vw + FOOD_RADIUS and \
                   -FOOD_RADIUS < sy < vh + FOOD_RADIUS:
                    pygame.draw.circle(vsurf, food[2], (sx, sy), FOOD_RADIUS)
                    pygame.draw.circle(vsurf, (255, 255, 255),
                                       (sx - 2, sy - 2), max(1, FOOD_RADIUS // 3))

            for player in render_players:
                draw_snake_on(vsurf, player, cam_x, cam_y, vw, vh)

            mini_x = vw - MINI_W - 10
            mini_y = vh - MINI_H - 10
            draw_hud_on(vsurf, focus, render_players, mini_x, mini_y)

            ctrl_y = vh - 85
            ctrl_texts = [
                "J1: Mouse  |  Click=Turbo",
                "J2: A/D  |  W=Turbo",
                "J3: ⬅ ⮕  |  ↑=Turbo",
                "J4: J/L  |  I=Turbo"
            ]
            if vi < len(ctrl_texts):
                draw_text(vsurf, ctrl_texts[vi], font_tiny, (150, 255, 150), (8, ctrl_y))

            screen.blit(vsurf, (vrect.x, vrect.y))

        if len(vp_rects) > 1:
            for vrect in vp_rects:
                pygame.draw.rect(screen, (0, 80, 0), vrect, 2)

        if dead_human_player is not None and not human_alive:
            action = draw_game_over(screen, dead_human_player, mouse_pos, mouse_click)
            if action == "rejugar":
                pygame.event.clear()
                player_color_choice[:] = last_color_choices
                num_players = last_num_players
                game_initialized = False
                dead_human_player = None
            elif action == "menu":
                pygame.event.clear()
                game_state = "menu"
                game_initialized = False
                dead_human_player = None

    pygame.display.flip()

pygame.quit()