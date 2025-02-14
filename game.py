# game.py
import copy

# Conditions de victoire définies par trois motifs :
# - Rangée du milieu : indices 3,4,5 -> 0b000111000
# - Diagonale anti principale : indices 2,4,6 -> 0b001010100
# - Diagonale principale : indices 0,4,8 -> 0b100010001
WINNING_MASKS = [
    0b000111000,  # Rangée du milieu
    0b001010100,  # Diagonale anti principale
    0b100010001   # Diagonale principale
]

# Coefficient pour le critère de mobilité
MOBILITY_WEIGHT = 1

# Coefficient pour le critère d'adjacence (pénalise la combinaison des pièces)
ADJACENCY_WEIGHT = 5

def count_bits(x):
    return bin(x).count("1")

# Dictionnaire des voisins autorisés pour chaque case (indices 0 à 8)
# Ces connexions correspondent aux lignes tracées sur le plateau de Fanorona Telo,
# et n'incluent pas les "petits diagonals" non conformes.
ALLOWED_NEIGHBORS = {
    0: [1, 3, 4],      # Coin supérieur gauche
    1: [0, 2, 4],      # Bord supérieur central
    2: [1, 4, 5],      # Coin supérieur droit
    3: [0, 4, 6],      # Bord gauche central
    4: [0, 1, 2, 3, 5, 6, 7, 8],  # Centre : toutes les directions sont autorisées
    5: [2, 4, 8],      # Bord droit central
    6: [3, 4, 7],      # Coin inférieur gauche
    7: [4, 6, 8],      # Bord inférieur central
    8: [4, 5, 7]       # Coin inférieur droit
}

class GameState:
    def __init__(self, board1=0, board2=0, turn=1, phase="placement", placements=(0, 0)):
        """
        board1 : BitBoard du joueur 1 (Rouge)
        board2 : BitBoard du joueur 2 (Bleu)
        turn   : 1 (Rouge) ou -1 (Bleu)
        phase  : "placement" ou "movement"
        placements : tuple (pièces placées par Rouge, par Bleu)
        """
        self.board1 = board1
        self.board2 = board2
        self.turn = turn
        self.phase = phase
        self.placements = placements

    def clone(self):
        return GameState(self.board1, self.board2, self.turn, self.phase, self.placements)

    def get_empty_positions(self):
        full = self.board1 | self.board2
        return [i for i in range(9) if not (full & (1 << i))]

    def index_to_coord(self, index):
        return (index // 3, index % 3)

    def coord_to_index(self, row, col):
        return row * 3 + col

    def get_neighbors(self, index):
        # Retourne les cases accessibles depuis "index" selon ALLOWED_NEIGHBORS
        return ALLOWED_NEIGHBORS.get(index, [])

    def is_win(self):
        """Retourne 1 si Rouge gagne, -1 si Bleu gagne, 0 sinon."""
        for mask in WINNING_MASKS:
            if (self.board1 & mask) == mask:
                return 1
            if (self.board2 & mask) == mask:
                return -1
        return 0

    def is_terminal(self):
        """
        La partie se termine si un joueur gagne ou s'il n'existe aucun mouvement possible.
        (En cas d'absence de coup, une notification de réinitialisation sera déclenchée.)
        """
        if self.is_win() != 0:
            return True
        if self.phase == "movement" and len(self.get_successors()) == 0:
            return True
        return False

    def get_successors(self):
        successors = []
        if self.phase == "placement":
            if self.placements[0] < 3 or self.placements[1] < 3:
                for pos in self.get_empty_positions():
                    new_state = self.clone()
                    if new_state.turn == 1:
                        new_state.board1 |= (1 << pos)
                        new_state.placements = (new_state.placements[0] + 1, new_state.placements[1])
                    else:
                        new_state.board2 |= (1 << pos)
                        new_state.placements = (new_state.placements[0], new_state.placements[1] + 1)
                    new_state.turn *= -1
                    if new_state.placements[0] == 3 and new_state.placements[1] == 3:
                        new_state.phase = "movement"
                    successors.append(new_state)
        elif self.phase == "movement":
            current_board = self.board1 if self.turn == 1 else self.board2
            for i in range(9):
                if current_board & (1 << i):
                    for nb in self.get_neighbors(i):
                        if not ((self.board1 | self.board2) & (1 << nb)):
                            new_state = self.clone()
                            if self.turn == 1:
                                new_state.board1 &= ~(1 << i)
                                new_state.board1 |= (1 << nb)
                            else:
                                new_state.board2 &= ~(1 << i)
                                new_state.board2 |= (1 << nb)
                            new_state.turn *= -1
                            successors.append(new_state)
        return successors

    def get_mobility(self, player):
        count = 0
        board = self.board1 if player == 1 else self.board2
        for i in range(9):
            if board & (1 << i):
                for nb in self.get_neighbors(i):
                    if not ((self.board1 | self.board2) & (1 << nb)):
                        count += 1
        return count

    def get_adjacency(self, player):
        adjacency = 0
        board = self.board1 if player == 1 else self.board2
        for i in range(9):
            if board & (1 << i):
                for nb in self.get_neighbors(i):
                    if board & (1 << nb):
                        adjacency += 1
        return adjacency // 2

    def evaluate(self):
        winner = self.is_win()
        if winner == 1:
            return float('inf')
        if winner == -1:
            return float('-inf')
        
        score = 0
        # Évaluation des motifs de victoire potentiels
        for mask in WINNING_MASKS:
            p1_count = count_bits(self.board1 & mask)
            p2_count = count_bits(self.board2 & mask)
            if p1_count > 0 and p2_count > 0:
                continue
            if p1_count > 0:
                score += (10 ** p1_count)
            if p2_count > 0:
                score -= (10 ** p2_count)
        
        # Mobilité
        mobility_advantage = self.get_mobility(1) - self.get_mobility(-1)
        score += MOBILITY_WEIGHT * mobility_advantage

        # Adjacence (pénalise les regroupements)
        ai_adj = self.get_adjacency(-1)
        player_adj = self.get_adjacency(1)
        score -= ADJACENCY_WEIGHT * ai_adj
        score += ADJACENCY_WEIGHT * player_adj
        
        return score

    def __str__(self):
        board_str = ""
        for i in range(9):
            if self.board1 & (1 << i):
                board_str += "X "
            elif self.board2 & (1 << i):
                board_str += "O "
            else:
                board_str += ". "
            if (i + 1) % 3 == 0:
                board_str += "\n"
        return board_str
