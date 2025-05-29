from game import move
from game.sound_manager import SoundManager
import pygame

class BattleManager:
    def __init__(self, player1, player2, sound_manager=None):
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.status_messages = [f"¡{self.get_active_player().name} comienza el combate!"]
        self.game_over = False
        self.winner = None
        self.sound_manager = sound_manager
        self.pending_victory_type = None  # "energy" o "health"

    def get_active_player(self):
        return self.player1 if self.turn == 1 else self.player2

    def get_enemy_player(self):
        return self.player2 if self.turn == 1 else self.player1

    def apply_action(self, action_name):
        if self.game_over:
            self.status_messages = ["El combate ya ha terminado."]
            return

        attacker = self.get_active_player()
        defender = self.get_enemy_player()

        messages = []

        # Forzar acción aunque no tenga suficiente energía
        energy_costs = {
            "simple_attack": 10,
            "defense": 5,
            "strong_attack": 25,
            "special_power": 40
        }
        required_energy = energy_costs.get(action_name, 0)

        if attacker.energy < required_energy:
            attacker.energy = 0
            messages.append(f"{attacker.name} intentó usar {action_name}, pero quedó sin energía.")
        else:
            if action_name == "simple_attack":
                result = move.simple_attack(attacker, defender)
            elif action_name == "defense":
                result = move.defense(attacker)
            elif action_name == "strong_attack":
                result = move.strong_attack(attacker, defender)
            elif action_name == "special_power":
                result = move.special_power(attacker)
            else:
                result = "Acción desconocida."

            if isinstance(result, list):
                messages.extend(result)
            else:
                messages.append(result)

        # Verificar condición de victoria, pero no ejecutar aún efectos (solo marcamos)
        if not defender.is_alive():
            self.game_over = True
            self.winner = attacker.name
            self.pending_victory_type = "health"
            messages.append(f"{defender.name} fue derrotado. {attacker.name} gana el combate.")

        elif defender.energy <= 0:
            self.game_over = True
            self.winner = attacker.name
            self.pending_victory_type = "energy"
            messages.append(f"{defender.name} se quedó sin energía. {attacker.name} gana el combate.")

        # Si no terminó, cambia turno
        if not self.game_over:
            self.turn = 2 if self.turn == 1 else 1
            messages.append(f"Turno de {self.get_active_player().name}.")

        self.status_messages = messages

    def play_victory_sound(self):
        if not self.game_over or not self.sound_manager:
            return

        loser = self.get_enemy_player().name
        winner = self.get_active_player().name

        if self.pending_victory_type == "health":
            self.sound_manager.play_victory_health(loser, winner)
        elif self.pending_victory_type == "energy":
            self.sound_manager.play_victory_energy(loser, winner)

        self.pending_victory_type = None

    def is_game_over(self):
        return self.game_over

    def get_status_messages(self):
        return self.status_messages

    def start_intro_sequence(self):
        if self.sound_manager:
            self.sound_manager.play_intro_sequence(self.player1.name, self.player2.name)