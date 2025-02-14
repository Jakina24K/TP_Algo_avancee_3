# gui.py
import pygame
import threading
import queue
import math
from game import GameState
from ai import alphabeta

class FanoronaTeloPygame:
    def __init__(self):
        pygame.init()
        # Agrandissement de l'interface : 600x600 pixels
        self.width = 600
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fanorona Telo - Pygame")
        self.clock = pygame.time.Clock()
        # Pour un plateau 3x3, chaque cellule est de 200x200 pixels
        self.cell_size = 200
        # Positions initiales fixes :
        # Joueur 1 (Rouge) : (111,000,000) → indices 0,1,2
        # Joueur 2 (Bleu) : (000,000,111) → indices 6,7,8
        self.initial_board1 = (1 << 0) | (1 << 1) | (1 << 2)
        self.initial_board2 = (1 << 6) | (1 << 7) | (1 << 8)
        self.reset_game()  # Initialise l'état du jeu
        self.selected = None  # Pour la sélection d'un pion (joueur humain)
        self.animating_move = None  # Dictionnaire contenant les infos d'animation en cours
        self.ai_queue = queue.Queue()  # File pour recevoir le coup de l'IA
        self.ai_thinking = False
        # Utilisation d'une police plus grande pour une meilleure lisibilité
        self.font = pygame.font.SysFont(None, 48)
        self.running = True

    def reset_game(self):
        """Réinitialise le plateau aux positions initiales et redémarre la partie."""
        self.state = GameState(
            board1=self.initial_board1,
            board2=self.initial_board2,
            turn=1,
            phase="movement",
            placements=(3, 3)
        )
        self.selected = None
        self.animating_move = None

    def show_notification(self, message):
        """Affiche une notification temporaire sur l'écran."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        self.screen.blit(overlay, (0, 0))
        text_surf = self.font.render(message, True, (0, 0, 0))
        rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surf, rect)
        pygame.display.flip()
        pygame.time.delay(2000)

    def get_cell_center(self, index):
        row = index // 3
        col = index % 3
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        return (x, y)

    def get_valid_moves(self, pos):
        valid = []
        row = pos // 3
        col = pos % 3
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r = row + dr
                c = col + dc
                if 0 <= r < 3 and 0 <= c < 3:
                    new_index = r * 3 + c
                    if not ((self.state.board1 | self.state.board2) & (1 << new_index)):
                        valid.append(new_index)
        return valid

    def animate_move(self, color, start_index, end_index, callback):
        self.animating_move = {
            "color": color,
            "start_index": start_index,
            "end_index": end_index,
            "start_time": pygame.time.get_ticks(),
            "duration": 500,  # Durée de l'animation en millisecondes
            "callback": callback
        }

    def update_animation(self):
        if self.animating_move:
            now = pygame.time.get_ticks()
            elapsed = now - self.animating_move["start_time"]
            progress = elapsed / self.animating_move["duration"]
            if progress >= 1.0:
                self.animating_move["callback"]()
                self.animating_move = None

    def draw_board(self):
        self.screen.fill((255, 255, 255))
        # Dessiner les intersections
        for i in range(9):
            center = self.get_cell_center(i)
            pygame.draw.circle(self.screen, (0, 0, 0), center, 8)
        # Dessiner les lignes reliant les intersections
        drawn = set()
        for i in range(9):
            row = i // 3
            col = i % 3
            center = self.get_cell_center(i)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r = row + dr
                    c = col + dc
                    if 0 <= r < 3 and 0 <= c < 3:
                        j = r * 3 + c
                        if (i, j) not in drawn and (j, i) not in drawn:
                            neighbor_center = self.get_cell_center(j)
                            pygame.draw.line(self.screen, (0, 0, 0), center, neighbor_center, 2)
                            drawn.add((i, j))
        # Dessiner les pions (en omettant celui en animation)
        for i in range(9):
            center = self.get_cell_center(i)
            if self.animating_move and i == self.animating_move["start_index"]:
                continue
            if self.state.board1 & (1 << i):
                pygame.draw.circle(self.screen, (255, 0, 0), center, 30)
            elif self.state.board2 & (1 << i):
                pygame.draw.circle(self.screen, (0, 0, 255), center, 30)
        # Dessiner le pion en cours d'animation
        if self.animating_move:
            now = pygame.time.get_ticks()
            elapsed = now - self.animating_move["start_time"]
            progress = min(elapsed / self.animating_move["duration"], 1.0)
            start_center = self.get_cell_center(self.animating_move["start_index"])
            end_center = self.get_cell_center(self.animating_move["end_index"])
            current_x = start_center[0] + (end_center[0] - start_center[0]) * progress
            current_y = start_center[1] + (end_center[1] - start_center[1]) * progress
            pygame.draw.circle(self.screen, self.animating_move["color"], (int(current_x), int(current_y)), 30)
        # Mettre en évidence le pion sélectionné
        if self.selected is not None:
            center = self.get_cell_center(self.selected)
            pygame.draw.circle(self.screen, (0, 255, 0), center, 35, 3)
        # Afficher le tour en cours en haut de l'écran
        turn_text = "Tour: Joueur Rouge" if self.state.turn == 1 else "Tour: Joueur Bleu"
        text_surf = self.font.render(turn_text, True, (0, 0, 0))
        self.screen.blit(text_surf, (20, 20))
        pygame.display.flip()

    def apply_player_move(self, start_index, end_index):
        if self.state.turn == 1:
            self.state.board1 &= ~(1 << start_index)
            self.state.board1 |= (1 << end_index)
        else:
            self.state.board2 &= ~(1 << start_index)
            self.state.board2 |= (1 << end_index)
        self.state.turn *= -1
        self.selected = None

    def handle_player_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.animating_move:
                return
            mouse_x, mouse_y = event.pos
            col = mouse_x // self.cell_size
            row = mouse_y // self.cell_size
            pos = row * 3 + col
            if self.state.turn == 1:
                if self.selected is None:
                    if self.state.board1 & (1 << pos):
                        self.selected = pos
                else:
                    valid = self.get_valid_moves(self.selected)
                    if pos in valid:
                        def callback():
                            self.apply_player_move(self.selected, pos)
                        self.animate_move((255, 0, 0), self.selected, pos, callback)
                    else:
                        if self.state.board1 & (1 << pos):
                            self.selected = pos
                        else:
                            self.selected = None

    def start_ai_move(self):
        if not self.ai_thinking and self.state.turn == -1 and not self.animating_move:
            self.ai_thinking = True
            def ai_thread():
                score, new_state = alphabeta(self.state, 4, -math.inf, math.inf, False)
                self.ai_queue.put(new_state)
                self.ai_thinking = False
            threading.Thread(target=ai_thread, daemon=True).start()

    def process_ai_move(self):
        try:
            new_state = self.ai_queue.get_nowait()
            old_board = self.state.board2
            new_board = new_state.board2
            start_index = None
            end_index = None
            for i in range(9):
                bit = 1 << i
                if (old_board & bit) and not (new_board & bit):
                    start_index = i
                if (new_board & bit) and not (old_board & bit):
                    end_index = i
            def callback():
                self.state = new_state
            if start_index is not None and end_index is not None:
                self.animate_move((0, 0, 255), start_index, end_index, callback)
            else:
                self.state = new_state
        except queue.Empty:
            pass

    def check_game_over(self):
        """Vérifie si un joueur a gagné ou s'il n'existe plus aucun mouvement."""
        winner = self.state.is_win()
        if winner != 0:
            msg = "Joueur Rouge gagne!" if winner == 1 else "Joueur Bleu gagne!"
            self.show_game_over(msg)
            self.running = False
        elif self.state.phase == "movement" and len(self.state.get_successors()) == 0:
            # En cas d'impossibilité de mouvement, notifier et réinitialiser la partie.
            self.show_notification("Aucun mouvement possible! Réinitialisation.")
            self.reset_game()

    def show_game_over(self, message):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        self.screen.blit(overlay, (0, 0))
        text_surf = self.font.render(message, True, (0, 0, 0))
        rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surf, rect)
        pygame.display.flip()
        pygame.time.delay(3000)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.state.turn == 1:
                    self.handle_player_input(event)
            if self.state.turn == -1 and not self.animating_move:
                self.start_ai_move()
            if self.state.turn == -1 and not self.animating_move:
                self.process_ai_move()
            self.update_animation()
            self.draw_board()
            self.check_game_over()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = FanoronaTeloPygame()
    game.run()
