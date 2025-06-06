import pygame, random, os
from game.character import Character
from game.battle import BattleManager
from game.brainrots import BRAINROTS
from game.scenarios import SCENARIOS
from ui.battle_ui import BattleUI
from utils import get_responsive_rect

# ---------- Constantes para fin de sonido ----------
WIN_LOSE_CHANNEL_ID = 3                       # canal dedicado a fx_win / fx_lose
VICTORY_DONE_EVENT  = pygame.USEREVENT + 1    # se emite cuando el canal termina

# -------------------- VARIABLES GLOBALES --------------------
player1 = player2 = battle = battle_ui = None
background_img = platform_img = interface_img = None
text_animator   = None
sound_manager   = None
battle_has_ended = False
end_menu_ready   = False

_message_queue = []
_message_timer = 0
_current_message = ""
_intro_sequence_pending = False
_intro_sequence_frame_counter = 0

# -------------------- HELPERS / GETTERS --------------------
def get_battle():
    """Devuelve la referencia actual al BattleManager (o None)."""
    return battle

def get_sound_manager():
    """Devuelve el SoundManager activo (o None)."""
    return sound_manager

# -------------------- TEXTO ANIMADO -------------------------
class TextAnimator:
    def __init__(self, full_text: str, speed: int = 10):
        self.full_text = full_text
        self.current_index = 0
        self.timer = 0
        self.speed = speed

    def update(self, dt):
        self.timer += dt
        while self.timer >= self.speed and self.current_index < len(self.full_text):
            self.current_index += 1
            self.timer -= self.speed

    def is_finished(self):
        return self.current_index >= len(self.full_text)

    def get_display_text(self):
        return self.full_text[: self.current_index]

    def set_text(self, new_text):
        self.full_text = new_text
        self.current_index = 0
        self.timer = 0

# -------------------- INICIALIZAR COMBATE --------------------
def init_battle(selected_data, sm=None):
    global player1, player2, battle, battle_ui
    global background_img, platform_img, interface_img
    global text_animator, sound_manager, _message_queue, _current_message
    global _intro_sequence_pending, _intro_sequence_frame_counter
    global battle_has_ended, end_menu_ready

    sound_manager = sm
    screen = pygame.display.get_surface()
    sw, sh = screen.get_size()

    battle_has_ended = False
    end_menu_ready   = False

    # ----- Escenario -----
    scenario = random.choice(SCENARIOS)
    background_img = pygame.transform.scale(
        pygame.image.load(scenario["background"]).convert(), (sw, sh)
    )
    platform_img = pygame.image.load(scenario["platform"]).convert_alpha()
    platform_img = pygame.transform.scale(
        platform_img, get_responsive_rect(0, 0, 10.92, 6, screen).size
    )

    map_key = os.path.basename(scenario["background"]).replace("_landscape.png", "")
    interface_img = pygame.image.load(
        f"assets/sprites/menu/{map_key}_menu.png"
    ).convert_alpha()
    interface_img = pygame.transform.scale(
        interface_img, get_responsive_rect(0, 0, 33.85, 5.97, screen).size
    )

    # ------ Personajes ------
    left_pos  = (6.61, 1.63)
    right_pos = (17.58, 1.63)
    player1 = Character(selected_data, left_pos)
    cpu_data = random.choice([b for b in BRAINROTS if b["name"] != selected_data["name"]])
    player2 = Character(cpu_data, right_pos, flipped=True)

    battle = BattleManager(player1, player2, sound_manager)
    battle.scenario = scenario
    battle_ui = BattleUI(screen, player1, player2)

    # ------ Mensajes iniciales ------
    _message_queue.clear()
    _message_queue.extend(battle.get_status_messages())
    _current_message = _message_queue.pop(0)
    text_animator = TextAnimator(_current_message)

    _intro_sequence_pending = True
    _intro_sequence_frame_counter = 0

    # ------ Canal dedicado a win/lose ------
    pygame.mixer.set_num_channels(
        max(WIN_LOSE_CHANNEL_ID + 1, pygame.mixer.get_num_channels())
    )
    victory_channel = pygame.mixer.Channel(WIN_LOSE_CHANNEL_ID)
    victory_channel.set_endevent(VICTORY_DONE_EVENT)

# -------------------- DIBUJO POR FRAME ----------------------
def draw_battle_placeholder(screen):
    screen.blit(background_img, (0, 0))
    screen.blit(platform_img, get_responsive_rect(6.15, 6.95, 0, 0, screen).topleft)
    screen.blit(platform_img, get_responsive_rect(16.79, 6.95, 0, 0, screen).topleft)

    player1.draw(screen)
    player2.draw(screen)

    screen.blit(interface_img, get_responsive_rect(0.02, 13.05, 0, 0, screen).topleft)

    if battle_ui:
        battle_ui.draw(text_animator)

# -------------------- EVENTOS DE COMBATE --------------------
def handle_battle_event(event):
    global _message_queue, _current_message

    if text_animator and not text_animator.is_finished():
        return

    if event.type == pygame.KEYDOWN:
        keymap = {
            pygame.K_a: "simple_attack",
            pygame.K_s: "strong_attack",
            pygame.K_d: "defense",
            pygame.K_f: "special_power",
        }
        if event.key in keymap and battle.get_active_player() == player1:
            battle_ui.buttons_enabled = False
            battle.apply_action(keymap[event.key])
            _message_queue = battle.get_status_messages()
            _current_message = _message_queue.pop(0)
            text_animator.set_text(_current_message)

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and battle_ui:
        if battle.get_active_player() == player1:
            action = battle_ui.handle_click(event.pos)
            if action:
                battle_ui.buttons_enabled = False
                battle.apply_action(action)
                _message_queue = battle.get_status_messages()
                _current_message = _message_queue.pop(0)
                text_animator.set_text(_current_message)

# -------------------- UPDATE LÓGICO -------------------------
def update_battle_logic(dt):
    global _message_timer, _message_queue, _current_message
    global _intro_sequence_pending, _intro_sequence_frame_counter

    # ---- Intro de voces ----
    if _intro_sequence_pending:
        _intro_sequence_frame_counter += 1
        if _intro_sequence_frame_counter >= 2:
            _intro_sequence_pending = False
            if sound_manager:
                sound_manager.play_intro_sequence(player1.name, player2.name)

    # ---- Animación de texto y lógica de turnos ----
    if text_animator:
        text_animator.update(dt)

        if text_animator.is_finished():
            if _message_queue:
                _message_timer += dt
                if _message_timer >= 800:
                    _message_timer = 0
                    _current_message = _message_queue.pop(0)
                    text_animator.set_text(_current_message)
            else:
                _handle_end_of_battle()

                if not battle.is_game_over():
                    if battle.get_active_player() == player1:
                        battle_ui.buttons_enabled = True
                    else:
                        _handle_cpu_turn()

# -------------------- FIN DEL COMBATE ----------------------
def _handle_end_of_battle():
    global battle_has_ended
    if not battle or not battle.is_game_over():
        return

    if not battle_has_ended:
        battle_has_ended = True
        if sound_manager:
            sound_manager.stop("fx_combat_curtain")
            battle.play_victory_sound()  # bloquea hasta terminar voces

            # reproducir win/lose en canal dedicado
            snd_key = "fx_win" if battle.winner == player1.name else "fx_lose"
            snd = sound_manager._get(snd_key)
            pygame.mixer.Channel(WIN_LOSE_CHANNEL_ID).play(snd)

# -------------------- TURNO DEL CPU ------------------------
def _handle_cpu_turn():
    global _message_queue, _current_message
    if battle.get_active_player() != player2 or battle.is_game_over():
        return

    pygame.time.delay(400)

    action = random.choice(
        ["simple_attack", "defense", "strong_attack", "special_power"]
    )
    battle.apply_action(action)
    _message_queue = battle.get_status_messages()
    if _message_queue:
        _current_message = _message_queue.pop(0)
        text_animator.set_text(_current_message)