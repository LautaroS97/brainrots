import pygame, sys
from ui import menu, start_menu, end_menu

# --- Estado global del juego ---
import game.game_state as gs
from game.game_state import (
    init_battle, draw_battle_placeholder, handle_battle_event,
    update_battle_logic,
    VICTORY_DONE_EVENT,
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
START_MENU = "start_menu"
CHARACTER_SELECT = "character_select"
BATTLE = "battle"
END_MENU = "end_menu"
current_state = FRONT

# ---------- Variables globales ----------
selected_character = None          # dict con info del brainrot elegido
winner_name        = None
battle_snapshot    = None           # Surface congelado para el End-Menu

# ---------- Recursos de portada ----------
front_background = pygame.image.load(
    "assets/sprites/backgrounds/front_landscape.png"
).convert()
front_background = pygame.transform.scale(front_background, (1920, 1080))
front_characters = pygame.image.load(
    "assets/sprites/props/front_characters.png"
).convert_alpha()
front_characters_rect = get_responsive_rect(2.96, 1.67, 27.94, 15.72, screen)
front_characters = pygame.transform.scale(front_characters, front_characters_rect.size)

# ---------- Fuente ----------
font_prompt = pygame.font.Font("assets/fonts/upheavtt.ttf", 36)

# ---------- Sonido ----------
sound_manager = SoundManager("assets/sounds")
sound_manager.load_all([
    "tralalero_tralala", "bombardino_crocodilo", "br_br_patapim",
    "lirili_larila", "tung_tung_sahur", "vaca_saturno_saturnita",
    "fx_select", "fx_congratulation", "fx_error", "fx_back",
    "fx_menu_curtain", "fx_combat_curtain"
])

# ---------- Parpadeo portada ----------
blink_timer  = 0
show_text    = True
BLINK_INTERVAL = 500  # ms

def draw_front_screen():
    screen.blit(front_background, (0, 0))
    screen.blit(front_characters, front_characters_rect.topleft)
    if show_text:
        txt = "Presione cualquier tecla o clic para comenzar"
        label  = font_prompt.render(txt, True, (255, 255, 255))
        shadow = font_prompt.render(txt, True, (0, 0, 0))
        r = label.get_rect(center=(screen.get_width() // 2,
                                   int(screen.get_height() * 0.85)))
        screen.blit(shadow, (r.x + 2, r.y + 2))
        screen.blit(label,  r)

# ---------- Bucle principal ----------
def main():
    global current_state, selected_character, winner_name, battle_snapshot
    global blink_timer, show_text

    sound_manager.ensure_loop("fx_menu_curtain")
    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        # ---- Eventos ----
        for event in pygame.event.get():
            # 1) Fin del sonido de victoria → habilitar End-Menu
            if event.type == VICTORY_DONE_EVENT:
                gs.end_menu_ready = True
                continue

            if event.type == pygame.QUIT:
                running = False

            if current_state == FRONT:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    current_state = START_MENU

            elif current_state == CHARACTER_SELECT:
                result = menu.handle_character_select_event(event, sound_manager)
                if result == "back":
                    sound_manager.play("fx_back")
                    sound_manager.ensure_loop("fx_menu_curtain")
                    current_state = START_MENU
                elif result:
                    sound_manager.stop("fx_menu_curtain")
                    sound_manager.play("fx_congratulation")
                    selected_character = result   # ← guarda el dict completo
                    init_battle(selected_character, sound_manager)
                    sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                    current_state = BATTLE

            elif current_state == BATTLE:
                handle_battle_event(event)

        # ---- Render según estado ----
        if current_state == FRONT:
            draw_front_screen()
            sound_manager.ensure_loop("fx_menu_curtain")

        elif current_state == START_MENU:
            sound_manager.ensure_loop("fx_menu_curtain")
            choice = start_menu.run_start_menu(screen, sound_manager, front_background)
            if choice == "CHARACTER_SELECT":
                current_state = CHARACTER_SELECT
            elif choice == "QUIT":
                pygame.quit(); sys.exit()

        elif current_state == CHARACTER_SELECT:
            sound_manager.ensure_loop("fx_menu_curtain")
            menu.draw_character_select(screen, sound_manager, front_background)

        elif current_state == BATTLE:
            draw_battle_placeholder(screen)
            update_battle_logic(dt)

            # Pasar al END_MENU tan pronto gs.end_menu_ready sea True
            if gs.battle and gs.battle.is_game_over() and gs.end_menu_ready:
                winner_name   = gs.battle.winner
                battle_snapshot = screen.copy()          # ← congela la escena
                current_state  = END_MENU

        elif current_state == END_MENU:
            result = end_menu.run_end_menu(
                screen,
                sound_manager,
                winner_name,
                background=battle_snapshot,
                player_name=selected_character["name"]
            )
            if result == "REPLAY":
                init_battle(selected_character, sound_manager)
                sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                current_state = BATTLE
            elif result == "MAIN_MENU":
                sound_manager.ensure_loop("fx_menu_curtain")
                current_state = START_MENU
            elif result == "QUIT":
                pygame.quit(); sys.exit()

        # ---- Parpadeo texto portada ----
        if current_state == FRONT:
            blink_timer += dt
            if blink_timer >= BLINK_INTERVAL:
                show_text = not show_text
                blink_timer = 0

        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()