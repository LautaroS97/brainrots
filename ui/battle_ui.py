import pygame
from utils import get_responsive_rect

class BattleUI:
    LIFE_COLOR   = (235, 16, 33)
    ENERGY_COLOR = (20, 198, 9)

    def __init__(self, screen, player1, player2):
        self.screen   = screen
        self.player1  = player1
        self.player2  = player2

        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 32)
        self.font_labels = pygame.font.Font("assets/fonts/upheavtt.ttf", 32)
        self.font_status = pygame.font.Font("assets/fonts/upheavtt.ttf", 36)

        self.frame_life  = pygame.image.load("assets/sprites/props/life_bar.png").convert_alpha()
        self.frame_power = pygame.image.load("assets/sprites/props/power_bar.png").convert_alpha()

        self.buttons = [
            {
                "action": "simple_attack",
                "rect": get_responsive_rect(11.55, 14.14, 5.13, 3.6, screen),
                "text_rect": get_responsive_rect(11.55, 14.14, 5.13, 3.6, screen)
            },
            {
                "action": "defense",
                "rect": get_responsive_rect(16.68, 14.14, 5.13, 3.6, screen),
                "text_rect": get_responsive_rect(16.68, 14.14, 5.13, 3.6, screen)
            },
            {
                "action": "strong_attack",
                "rect": get_responsive_rect(21.84, 14.14, 5.13, 3.6, screen),
                "text_rect": get_responsive_rect(21.84, 14.14, 5.13, 3.6, screen)
            },
            {
                "action": "special_power",
                "rect": get_responsive_rect(26.95, 14.14, 5.13, 3.6, screen),
                "text_rect": get_responsive_rect(26.95, 14.14, 5.13, 3.6, screen)
            }
        ]

        self.button_imgs = {
            "simple_attack": pygame.image.load("assets/sprites/props/button_simple_attack.png").convert_alpha(),
            "defense"       : pygame.image.load("assets/sprites/props/button_defense.png").convert_alpha(),
            "strong_attack" : pygame.image.load("assets/sprites/props/button_growth_attack.png").convert_alpha(),
            "special_power" : pygame.image.load("assets/sprites/props/button_special_power.png").convert_alpha()
        }

        self.button_inactive = pygame.image.load("assets/sprites/props/button_inactive.png").convert_alpha()

        self.disp_hp1 = self.player1.health
        self.disp_en1 = self.player1.energy
        self.disp_hp2 = self.player2.health
        self.disp_en2 = self.player2.energy

        self.buttons_enabled = True

    def _draw_static_bar(self, cm_x, cm_y, cm_w, cm_h, value, max_value, color):
        s = self.screen
        full_rect = get_responsive_rect(cm_x, cm_y, cm_w, cm_h, s)
        filled_width = int(full_rect.width * (value / max_value))
        filled_rect = pygame.Rect(full_rect.x, full_rect.y, filled_width, full_rect.height)
        pygame.draw.rect(s, color, filled_rect, border_radius=5)

    def _draw_bars(self):
        s = self.screen
        s.blit(pygame.transform.scale(self.frame_life, get_responsive_rect(0.39, 0.56, 6.85, 1.2, s).size), get_responsive_rect(0.39, 0.56, 0, 0, s).topleft)
        s.blit(pygame.transform.scale(self.frame_power, get_responsive_rect(0.39, 2.00, 6.85, 1.2, s).size), get_responsive_rect(0.39, 2.00, 0, 0, s).topleft)
        s.blit(pygame.transform.scale(self.frame_life, get_responsive_rect(26.63, 0.56, 6.85, 1.2, s).size), get_responsive_rect(26.63, 0.56, 0, 0, s).topleft)
        s.blit(pygame.transform.scale(self.frame_power, get_responsive_rect(26.63, 2.00, 6.85, 1.2, s).size), get_responsive_rect(26.63, 2.00, 0, 0, s).topleft)

        self._draw_static_bar(0.67, 0.8, 5.14, 0.7, self.disp_hp1, self.player1.max_health, self.LIFE_COLOR)
        self._draw_static_bar(26.9, 0.8, 5.14, 0.7, self.disp_hp2, self.player2.max_health, self.LIFE_COLOR)
        self._draw_static_bar(0.67, 2.24, 5.14, 0.7, self.disp_en1, self.player1.max_energy, self.ENERGY_COLOR)
        self._draw_static_bar(26.9, 2.24, 5.14, 0.7, self.disp_en2, self.player2.max_energy, self.ENERGY_COLOR)

    def _draw_status(self, text_animator):
        if not text_animator:
            return

        s = self.screen
        text = text_animator.get_display_text()
        area = get_responsive_rect(1.82, 14.24, 9.24, 3.4, s)
        x, y = area.topleft

        color = (0, 0, 0)
        scenario = getattr(getattr(self.player1, "battle", None), "scenario", None)
        if scenario and "color_text_resume" in scenario:
            hex_color = scenario["color_text_resume"]
            color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

        words = text.split(" ")
        line = ""
        lines = []
        for word in words:
            test_line = line + word + " "
            if self.font_status.size(test_line)[0] < area.width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        for i, line in enumerate(lines):
            surface = self.font_status.render(line.strip(), True, color)
            s.blit(surface, (x, y + i * self.font_status.get_height()))

    def _draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            action = btn["action"]
            w, h = btn["rect"].size
            rect = btn["rect"]

            # Selección de imagen según estado del botón
            img = (
                pygame.transform.scale(self.button_imgs[action], (w, h))
                if self.buttons_enabled
                else pygame.transform.scale(self.button_inactive, (w, h))
            )
            self.screen.blit(img, rect.topleft)

            # Mostrar nombre del movimiento en ambos estados
            label_text = getattr(self.player1, f"{action}_name", action.upper())
            text_rect = btn["text_rect"]

            words = label_text.split(" ")
            lines = []
            current = ""
            for word in words:
                test = current + word + " "
                if self.font_labels.size(test)[0] < text_rect.width:
                    current = test
                else:
                    lines.append(current.strip())
                    current = word + " "
            lines.append(current.strip())

            total_height = len(lines) * self.font_labels.get_height()
            y_start = text_rect.y + (text_rect.height - total_height) // 2

            for i, line in enumerate(lines):
                surf = self.font_labels.render(line, True, (255, 255, 255))
                shadow = self.font_labels.render(line, True, (0, 0, 0))
                x_center = text_rect.centerx - surf.get_width() // 2
                y = y_start + i * self.font_labels.get_height()
                self.screen.blit(shadow, (x_center + 2, y + 2))
                self.screen.blit(surf, (x_center, y))

            if self.buttons_enabled and rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)

    def _smooth_values(self, speed=0.18):
        self.disp_hp1 += (self.player1.health  - self.disp_hp1) * speed
        self.disp_en1 += (self.player1.energy  - self.disp_en1) * speed
        self.disp_hp2 += (self.player2.health  - self.disp_hp2) * speed
        self.disp_en2 += (self.player2.energy  - self.disp_en2) * speed

    def draw(self, text_animator=None):
        self._smooth_values()
        self._draw_bars()
        self._draw_status(text_animator)
        self._draw_buttons()

    def handle_click(self, pos):
        if not self.buttons_enabled:
            return None
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                return btn["action"]
        return None