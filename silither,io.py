import pygame

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

pygame.quit()
