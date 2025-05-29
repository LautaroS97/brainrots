import pygame
import sys
from ui import menu, summary
from game.game_state import (
    init_battle,
    draw_battle_placeholder,
    handle_battle_event,
    update_battle_logic,
    battle,
    player1,
    sound_manager
)
from game.sound_manager import SoundManager
from utils import get_responsive_rect

# ---------- Inicialización ----------
pygame.init()
pygame.mixer.init()
SCREEN_W, SCREEN_H = 1920, 1080
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Italian Brainrots Arena")
clock = pygame.time.Clock()
FPS = 60

# ---------- Estados ----------
FRONT = "front"
MENU = "menu"
CHARACTER_SELECT = "character_select"
BATTLE = "battle"
SUMMARY = "summary"
current_state = FRONT

# ---------- Variables globales ----------
selected_character = None
winner_name = None

# ---------- Recursos de portada ----------
front_background = pygame.image.load("assets/sprites/backgrounds/front_landscape.png").convert()
front_background = pygame.transform.scale(front_background, (1920, 1080))

front_characters = pygame.image.load("assets/sprites/props/front_characters.png").convert_alpha()
front_characters_rect = get_responsive_rect(2.96, 1.67, 27.94, 15.72, screen)
front_characters = pygame.transform.scale(front_characters, front_characters_rect.size)

# ---------- Fuentes personalizadas ----------
font_title = pygame.font.Font("assets/fonts/retro_gaming.ttf", 60)
font_prompt = pygame.font.Font("assets/fonts/upheavtt.ttf", 36)  # tamaño agrandado

# ---------- Sistema de sonido ----------
sound_manager = SoundManager("assets/sounds")
sound_manager.load_all([
    "tralalero_tralala",
    "bombardino_crocodilo",
    "br_br_patapim",
    "lirili_larila",
    "tung_tung_sahur",
    "vaca_saturno_saturnita"
])

# ---------- Parpadeo del texto ----------
blink_timer = 0
show_text = True
BLINK_INTERVAL = 500  # ms

# ---------- Pantalla de portada ----------
def draw_front_screen():
    screen.blit(front_background, (0, 0))
    screen.blit(front_characters, front_characters_rect.topleft)

    if show_text:
        prompt_text = "Presione cualquier tecla o clic para comenzar"
        text_surface = font_prompt.render(prompt_text, True, (255, 255, 255))
        shadow_surface = font_prompt.render(prompt_text, True, (0, 0, 0))

        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, int(screen.get_height() * 0.85)))
        shadow_rect = shadow_surface.get_rect(center=(screen.get_width() // 2 + 2, int(screen.get_height() * 0.85) + 2))

        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

# ---------- Bucle principal ----------
def main():
    global current_state, selected_character, winner_name
    global blink_timer, show_text
    sound_manager.play_loop("fx_menu_curtain")

    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == FRONT:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    current_state = CHARACTER_SELECT

            elif current_state == CHARACTER_SELECT:
                result = menu.handle_character_select_event(event, sound_manager)
                if result == "back":
                    sound_manager.play("fx_back")
                    sound_manager.play_loop("fx_menu_curtain")
                    current_state = MENU
                elif result:
                    sound_manager.stop("fx_menu_curtain")
                    sound_manager.play("fx_congratulation")
                    selected_character = result
                    init_battle(selected_character, sound_manager)
                    sound_manager.play_loop("fx_combat_curtain", volume=0.5)
                    current_state = BATTLE

            elif current_state == BATTLE:
                handle_battle_event(event)

            elif current_state == SUMMARY:
                action = summary.handle_summary_event(event, sound_manager)
                if action == "Revancha":
                    init_battle(selected_character, sound_manager)
                    sound_manager.play_loop("fx_combat_curtain", volume=0.5)
                    current_state = BATTLE
                elif action == "Volver al menú":
                    sound_manager.play_loop("fx_menu_curtain")
                    current_state = MENU

        if current_state == FRONT:
            draw_front_screen()

        elif current_state == CHARACTER_SELECT:
            menu.draw_character_select(screen, sound_manager, front_background)

        elif current_state == BATTLE:
            draw_battle_placeholder(screen)
            update_battle_logic(dt)

            if battle and battle.is_game_over():
                pygame.time.wait(1000)
                winner_name = battle.winner
                bg_path = getattr(battle.scenario, "background", "assets/sprites/backgrounds/default.png")
                summary.reset_summary(winner_name, bg_path)
                current_state = SUMMARY

        elif current_state == SUMMARY:
            summary.draw_summary_screen(screen, winner_name, sound_manager)

        elif current_state == MENU:
            menu.draw_menu(screen, front_background)

        # ---------- Actualizar parpadeo ----------
        if current_state == FRONT:
            blink_timer += dt
            if blink_timer >= BLINK_INTERVAL:
                show_text = not show_text
                blink_timer = 0

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()