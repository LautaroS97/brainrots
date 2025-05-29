import pygame
from game.brainrots import BRAINROTS
from game.game_state import TextAnimator
from utils import get_responsive_rect

# Inicializar fuentes
pygame.font.init()
title_font  = pygame.font.Font("assets/fonts/upheavtt.ttf", 48)
button_font = pygame.font.Font("assets/fonts/retro_gaming.ttf", 48)

# Configuración de botones
button_width_cm, button_height_cm = 9.24, 3.4
button_margin_cm = 1.5
button_color     = (255, 255, 255)
hover_color      = (255, 255, 100)
options          = ["Revancha", "Volver al menú"]
selected_index   = 0

# Estado
text_animator  = None
winner_thumb   = None
background_img = None

def reset_summary(winner, background_path):
    global text_animator, winner_thumb, background_img

    message = f"¡Ganó {winner}!"
    text_animator = TextAnimator(message, speed=40)

    winner_data = next((c for c in BRAINROTS if c["name"] == winner), None)
    if winner_data:
        winner_thumb = pygame.image.load(winner_data["thumb"]).convert_alpha()
        winner_thumb = pygame.transform.scale(winner_thumb, (240, 240))

    background_img = pygame.image.load(background_path).convert()
    background_img = pygame.transform.scale(background_img, (1920, 1080))

def draw_summary_screen(screen, winner_name, sound_manager=None):
    screen_w, screen_h = screen.get_size()

    # Fondo + overlay
    if background_img:
        bg = pygame.transform.scale(background_img, (screen_w, screen_h))
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((0, 0, 0))

    # Título animado
    if text_animator:
        text = text_animator.get_display_text()
        shadow = title_font.render(text, True, (0, 0, 0))
        label  = title_font.render(text, True, (255, 255, 255))

        # Posición en cm desde el top
        title_pos = get_responsive_rect(0, 3.5, 33.867, 3, screen)
        x_center = title_pos.centerx
        y = title_pos.y

        screen.blit(shadow, (x_center - shadow.get_width() // 2 + 2, y + 2))
        screen.blit(label,  (x_center - label.get_width() // 2, y))
        text_animator.update(pygame.time.get_ticks() // 20)

    # Imagen del ganador
    if winner_thumb:
        thumb_rect = get_responsive_rect(12, 7, 9, 9, screen)  # imagen centrada en pantalla
        screen.blit(winner_thumb, thumb_rect.topleft)

    # Botones
    for i, text in enumerate(options):
        rect = get_responsive_rect(
            11.0, 14.0 + i * (button_height_cm + button_margin_cm),
            button_width_cm, button_height_cm,
            screen
        )
        color = hover_color if i == selected_index else button_color
        pygame.draw.rect(screen, color, rect, border_radius=8)

        label = button_font.render(text, True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=rect.center))

    pygame.display.flip()

def handle_summary_event(event, sound_manager=None):
    global selected_index
    screen = pygame.display.get_surface()

    for i in range(len(options)):
        rect = get_responsive_rect(
            11.0, 14.0 + i * (button_height_cm + button_margin_cm),
            button_width_cm, button_height_cm,
            screen
        )

        if event.type == pygame.MOUSEMOTION:
            if rect.collidepoint(event.pos) and selected_index != i:
                selected_index = i
                if sound_manager: sound_manager.play("fx_select")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                selected_index = i
                if sound_manager: sound_manager.play("fx_congratulation")
                return options[i]

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_index = (selected_index - 1) % len(options)
            if sound_manager: sound_manager.play("fx_select")
        elif event.key == pygame.K_DOWN:
            selected_index = (selected_index + 1) % len(options)
            if sound_manager: sound_manager.play("fx_select")
        elif event.key == pygame.K_RETURN:
            if sound_manager: sound_manager.play("fx_congratulation")
            return options[selected_index]
        elif event.key == pygame.K_ESCAPE:
            if sound_manager: sound_manager.play("fx_back")
            return "Volver al menú"

    return None