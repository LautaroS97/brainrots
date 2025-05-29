import pygame
from utils import get_responsive_rect

class Character:
    """
    Objeto de juego que representa a un Brainrot.
    """
    def __init__(self, data: dict, position: tuple[float, float], flipped: bool = False):
        self.name        = data["name"]
        self.image_path  = data["image"]
        self.flipped     = flipped
        self.image       = None
        self.position    = position  # Posición en cm (x, y)

        # Atributos de combate
        self.max_health   = 100
        self.health       = 100
        self.max_energy   = 100
        self.energy       = 100
        self.is_defending = False

        # Nombres de movimientos
        self.simple_attack_name  = data.get("simple_attack",  "Simple Attack")
        self.defense_name        = data.get("defense",        "Defensa")
        self.strong_attack_name  = data.get("strong_attack",  "Ataque Fuerte")
        self.special_power_name  = data.get("special_power",  "Poder Especial")

    def draw(self, screen: pygame.Surface):
        # Posición y tamaño en cm → responsivo
        rect = get_responsive_rect(self.position[0], self.position[1], 10, 10, screen)

        # Carga y escalado del sprite
        img = pygame.image.load(self.image_path).convert_alpha()
        img = pygame.transform.scale(img, rect.size)

        if self.flipped:
            img = pygame.transform.flip(img, True, False)

        screen.blit(img, rect.topleft)

    def receive_damage(self, amount: int):
        if self.is_defending:
            amount = int(amount * 0.5)  # Reduce damage if defending
        self.health = max(0, self.health - amount)
        return amount  # ← Esta línea soluciona el "None" en los mensajes

    def consume_energy(self, amount: int):
        self.energy = max(0, self.energy - amount)

    def recover_energy(self, amount: int):
        self.energy = min(self.max_energy, self.energy + amount)

    def restore_health(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def defend(self):
        self.is_defending = True

    def stop_defending(self):
        self.is_defending = False

    def is_alive(self) -> bool:
        return self.health > 0