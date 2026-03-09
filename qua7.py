import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 1000, 740  # Extra width for the technical sidebar
BOARD_SIZE = 640
SQ = 80
TUNNEL_CHANCE = 0.3
COLORS = {
    "white_sq": (245, 245, 220), "black_sq": (110, 140, 70),
    "white_pc": (255, 255, 255), "black_pc": (20, 20, 20),
    "quantum": (0, 150, 255), "entangled": (255, 50, 50),
    "highlight": (255, 215, 0), "sidebar": (30, 33, 40)
}

class Piece:
    def __init__(self, name, r, c, color):
        self.name, self.r, self.c, self.color = name, r, c, color
        self.is_superposed, self.states, self.entangled_with = False, [], None

    def is_legal_move(self, tr, tc, pieces):
        dr, dc = tr - self.r, tc - self.c
        abs_dr, abs_dc = abs(dr), abs(dc)
        if self.name == "P":
            dir = -1 if self.color == 'W' else 1
            if dc == 0 and dr == dir: return not self.is_occ(tr, tc, pieces)
            if dc == 0 and dr == 2*dir and ((self.r==6 and self.color=='W') or (self.r==1 and self.color=='B')):
                return not self.is_occ(tr, tc, pieces) and not self.is_occ(self.r+dir, tc, pieces)
            if abs_dc == 1 and dr == dir: return self.is_occ(tr, tc, pieces)
            return False
        if self.name in ["R", "B", "Q"]:
            ok = (dr==0 or dc==0) if self.name=="R" else (abs_dr==abs_dc) if self.name=="B" else (dr==0 or dc==0 or abs_dr==abs_dc)
            return ok # Tunneling handles the path check later
        if self.name == "N": return (abs_dr==2 and abs_dc==1) or (abs_dr==1 and abs_dc==2)
        if self.name == "K": return abs_dr<=1 and abs_dc<=1
        return False

    def is_occ(self, r, c, pieces):
        return any(not p.is_superposed and p.r == r and p.c == c for p in pieces)

    def path_blocked(self, tr, tc, pieces):
        sr = 0 if tr == self.r else (1 if tr > self.r else -1)
        sc = 0 if tc == self.c else (1 if tc > self.c else -1)
        cr, cc = self.r + sr, self.c + sc
        while cr != tr or cc != tc:
            if self.is_occ(cr, cc, pieces): return True
            cr += sr; cc += sc
        return False

    def move(self, r, c):
        self.r, self.c, self.is_superposed, self.states = r, c, False, []

    def superpose(self, p1, p2):
        self.states, self.is_superposed = [p1, p2], True

    def collapse(self):
        if self.is_superposed:
            final = random.choice(self.states)
            self.move(final[0], final[1])
            if self.entangled_with and self.entangled_with.is_superposed:
                partner = self.entangled_with
                self.entangled_with = partner.entangled_with = None
                partner.collapse()

def draw_sidebar(screen, font, turn, split_mode, pieces):
    # Sidebar Background
    pygame.draw.rect(screen, COLORS["sidebar"], (BOARD_SIZE, 0, WIDTH - BOARD_SIZE, HEIGHT))
    s_font = pygame.font.SysFont("Arial", 16)
    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    
    x_offset = BOARD_SIZE + 20
    y = 20

    # 1. SCOREBOARD
    screen.blit(title_font.render("INVENTORY", True, COLORS["highlight"]), (x_offset, y))
    w_count = sum(1 for p in pieces if p.color == 'W')
    b_count = sum(1 for p in pieces if p.color == 'B')
    screen.blit(s_font.render(f"White Figures Left: {w_count}/16", True, (255,255,255)), (x_offset, y+35))
    screen.blit(s_font.render(f"Black Figures Left: {b_count}/16", True, (255,255,255)), (x_offset, y+55))

    # 2. QUANTUM GLOSSARY
    y += 110
    screen.blit(title_font.render("QUANTUM LAWS", True, COLORS["highlight"]), (x_offset, y))
    
    laws = [
        ("Superposition (S Key)", "Piece exists in 2 squares at once."),
        ("Tunneling (Passive)", "30% chance to pass through obstacles."),
        ("Entanglement (Red)", "Spooky link: 1 collapses, both collapse."),
        ("Measurement (Click)", "Clicking a Ghost forces it into reality.")
    ]
    
    for title, desc in laws:
        y += 40
        screen.blit(s_font.render(title, True, (0, 200, 255)), (x_offset, y))
        # Wrap text manually
        screen.blit(s_font.render(desc, True, (180, 180, 180)), (x_offset, y + 20))
        y += 20

    # 3. CURRENT STATE
    y += 80
    pygame.draw.rect(screen, (50, 60, 70), (x_offset - 10, y, 300, 100))
    curr_turn = "WHITE" if turn == 'W' else "BLACK"
    screen.blit(title_font.render(f"TURN: {curr_turn}", True, (255, 255, 255)), (x_offset, y + 10))
    mode = "SPLIT MODE ACTIVE" if split_mode else "NORMAL MOVEMENT"
    screen.blit(s_font.render(mode, True, COLORS["quantum"] if split_mode else (150, 255, 150)), (x_offset, y + 50))

def create_board():
    pieces = []
    layout = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for c, name in enumerate(layout):
        pieces.append(Piece(name, 0, c, 'B')); pieces.append(Piece("P", 1, c, 'B'))
        pieces.append(Piece(name, 7, c, 'W')); pieces.append(Piece("P", 6, c, 'W'))
    return pieces

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quantum Chess: Complete Version")
    font = pygame.font.SysFont("Arial", 28, bold=True)
    pieces = create_board()
    selected, turn, split_mode = None, 'W', False

    while True:
        screen.fill((20, 20, 20))
        for r in range(8):
            for c in range(8):
                col = COLORS["white_sq"] if (r+c)%2==0 else COLORS["black_sq"]
                pygame.draw.rect(screen, col, (c*SQ, r*SQ, SQ, SQ))
        
        draw_sidebar(screen, font, turn, split_mode, pieces)

        for p in pieces:
            if p.is_superposed:
                d_col = COLORS["entangled"] if p.entangled_with else COLORS["quantum"]
                for sr, sc in p.states:
                    pygame.draw.circle(screen, d_col, (sc*SQ+40, sr*SQ+40), 30)
                    screen.blit(font.render(p.name, True, (255,255,255)), (sc*SQ+30, sr*SQ+20))
            else:
                p_col = COLORS["white_pc"] if p.color == 'W' else COLORS["black_pc"]
                pygame.draw.circle(screen, p_col, (p.c*SQ+40, p.r*SQ+40), 35)
                screen.blit(font.render(p.name, True, (150,150,150) if p.color=='W' else (200,200,200)), (p.c*SQ+30, p.r*SQ+20))
            if p == selected: pygame.draw.rect(screen, COLORS["highlight"], (p.c*SQ, p.r*SQ, SQ, SQ), 4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                c, r = event.pos[0]//SQ, event.pos[1]//SQ
                if c >= 8 or r >= 8: continue
                
                ghost = next((p for p in pieces if p.is_superposed and (r, c) in p.states), None)
                if selected and ghost and selected != ghost:
                    if selected.is_legal_move(r, c, pieces):
                        selected.entangled_with, ghost.entangled_with = ghost, selected
                        selected.superpose((selected.r, selected.c), (r, c))
                        selected, turn = None, ('B' if turn == 'W' else 'W')
                    continue
                elif ghost: ghost.collapse(); continue

                clicked = next((p for p in pieces if not p.is_superposed and p.r == r and p.c == c), None)
                if split_mode and selected:
                    if selected.is_legal_move(r, c, pieces):
                        selected.superpose((selected.r, selected.c), (r, c))
                        split_mode, selected, turn = False, None, ('B' if turn == 'W' else 'W')
                elif clicked and clicked.color == turn: selected = clicked
                elif selected and selected.is_legal_move(r, c, pieces):
                    # TUNNELING LOGIC
                    can_move = True
                    if selected.name != "N" and selected.path_blocked(r, c, pieces):
                        if random.random() < TUNNEL_CHANCE: print("TUNNELED!")
                        else: can_move = False; print("REFLECTED!")
                    
                    if can_move:
                        target = next((p for p in pieces if p.r == r and p.c == c), None)
                        if target:
                            if target.name == "K": print("KING CAPTURED!"); return
                            pieces.remove(target)
                        selected.move(r, c)
                        selected, turn = None, ('B' if turn == 'W' else 'W')
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and selected: split_mode = True
        pygame.display.flip()

if __name__ == "__main__": main()