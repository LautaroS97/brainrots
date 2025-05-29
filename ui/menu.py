import pygame
from game.brainrots import BRAINROTS
from utils import get_responsive_rect

pygame.font.init()

# Fuentes personalizadas
title_font  = pygame.font.Font("assets/fonts/retro_gaming.ttf", 72)
button_font = pygame.font.Font("assets/fonts/retro_gaming.ttf", 42)
name_font   = pygame.font.Font("assets/fonts/upheavtt.ttf",     22)

# Selector global
selected_index = 0
last_index     = -1
character_thumbs = []   # [(rect, character_dict)]

# Valores de referencia (en cm)
THUMB_W_CM, THUMB_H_CM = 5.3, 5.3
GRID_COLS = 3
GRID_SPACING_X_CM = 2.5
GRID_SPACING_Y_CM = 2.4
GRID_TOP_CM       = 5.3

BTN_W_CM, BTN_H_CM = 9.5, 2.5
BTN_Y_CM           = 20.0
BTN_X_CM           = 12.2
BTN_COLOR, BTN_HOVER = (255,255,255), (200,200,200)

# ---------- MENÚ PRINCIPAL ----------
def draw_menu(screen, background_img):
    screen.blit(pygame.transform.scale(background_img, screen.get_size()), (0, 0))
    screen_w, _ = screen.get_size()

    # Título centrado (posición en cm)
    x, y = get_responsive_rect(0, 3.5, 0, 0, screen).topleft
    title_surf = title_font.render("ITALIAN BRAINROTS ARENA", True, (0, 0, 0))
    screen.blit(title_surf, title_surf.get_rect(midtop=(screen_w // 2, y)))

    # Botón "COMENZAR"
    btn_rect = get_responsive_rect(BTN_X_CM, BTN_Y_CM, BTN_W_CM, BTN_H_CM, screen)
    mouse = pygame.mouse.get_pos()
    color = BTN_HOVER if btn_rect.collidepoint(mouse) else BTN_COLOR
    pygame.draw.rect(screen, color, btn_rect, border_radius=10)

    txt = button_font.render("COMENZAR", True, (0, 0, 0))
    screen.blit(txt, txt.get_rect(center=btn_rect.center))

def handle_menu_event(event):
    screen = pygame.display.get_surface()
    btn_rect = get_responsive_rect(BTN_X_CM, BTN_Y_CM, BTN_W_CM, BTN_H_CM, screen)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if btn_rect.collidepoint(event.pos):
            return True
    return False

# ---------- SELECTOR DE PERSONAJES ----------
def draw_character_select(screen, sound_manager=None, background_img=None):
    global character_thumbs
    screen_w, screen_h = screen.get_size()

    if background_img:
        screen.blit(pygame.transform.scale(background_img, screen.get_size()), (0, 0))
    else:
        screen.fill((30, 30, 30))

    # Título con posicionamiento responsivo (subido a 1.5 cm)
    x, y = get_responsive_rect(0, 1.5, 0, 0, screen).topleft
    title_shadow = title_font.render("ELIGE TU PERSONAJE", True, (0, 0, 0))
    title_text   = title_font.render("ELIGE TU PERSONAJE", True, (255, 255, 255))
    screen.blit(title_shadow, title_shadow.get_rect(midtop=(screen_w // 2 + 2, y + 2)))
    screen.blit(title_text, title_text.get_rect(midtop=(screen_w // 2, y)))

    # Cálculos de layout
    thumb_w   = get_responsive_rect(0, 0, THUMB_W_CM, THUMB_H_CM, screen).width
    thumb_h   = get_responsive_rect(0, 0, THUMB_W_CM, THUMB_H_CM, screen).height
    spacing_x = get_responsive_rect(0, 0, GRID_SPACING_X_CM, 0, screen).width
    spacing_y = get_responsive_rect(0, 0, 0, GRID_SPACING_Y_CM, screen).height
    grid_top_y = get_responsive_rect(0, GRID_TOP_CM, 0, 0, screen).y

    total_width = GRID_COLS * thumb_w + (GRID_COLS - 1) * spacing_x
    start_x = (screen_w - total_width) // 2

    character_thumbs.clear()
    mouse = pygame.mouse.get_pos()

    for i, char in enumerate(BRAINROTS):
        col = i % GRID_COLS
        row = i // GRID_COLS
        x = start_x + col * (thumb_w + spacing_x)
        y = grid_top_y + row * (thumb_h + spacing_y)

        img = pygame.image.load(char["image"]).convert_alpha()
        img = pygame.transform.scale(img, (thumb_w, thumb_h))
        rect = pygame.Rect(x, y, thumb_w, thumb_h)

        screen.blit(img, rect.topleft)

        hover  = rect.collidepoint(mouse)
        select = (i == selected_index)
        if hover:
            overlay = pygame.Surface((thumb_w, thumb_h), pygame.SRCALPHA)
            overlay.fill((255,255,255,50))
            screen.blit(overlay, rect.topleft)
            pygame.draw.rect(screen, (255,255,100), rect, 4)
        elif select:
            pygame.draw.rect(screen, (255,0,0), rect, 4)
        else:
            pygame.draw.rect(screen, (255,255,255), rect, 3)

        # Nombre con sombra
        name = char["name"]
        name_surf   = name_font.render(name, True, (255,255,255))
        shadow_surf = name_font.render(name, True, (0,0,0))
        name_rect = name_surf.get_rect(center=(x + thumb_w // 2, y + thumb_h + 28))
        screen.blit(shadow_surf, name_rect.move(2, 2))
        screen.blit(name_surf, name_rect)

        character_thumbs.append((rect, char))

def handle_character_select_event(event, sound_manager=None):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, char in character_thumbs:
            if rect.collidepoint(event.pos):
                if sound_manager: sound_manager.play("fx_congratulation")
                return char
    elif event.type == pygame.KEYDOWN:
        return _handle_keyboard(event, sound_manager)
    return None

def _handle_keyboard(event, sound_manager=None):
    global selected_index, last_index
    total = len(BRAINROTS)

    move = 0
    if event.key in (pygame.K_LEFT, pygame.K_a):  move = -1
    if event.key in (pygame.K_RIGHT, pygame.K_d): move = +1
    if event.key in (pygame.K_UP, pygame.K_w):    move = -GRID_COLS
    if event.key in (pygame.K_DOWN, pygame.K_s):  move = +GRID_COLS

    if move:
        new_i = selected_index + move
        if 0 <= new_i < total:
            selected_index = new_i
            if sound_manager and new_i != last_index:
                sound_manager.play("fx_select")
            last_index = new_i
        return None

    if event.key == pygame.K_RETURN:
        if sound_manager: sound_manager.play("fx_congratulation")
        return BRAINROTS[selected_index]

    if event.key == pygame.K_ESCAPE:
        if sound_manager: sound_manager.play("fx_back")
        return "back"

    return None