import pygame
import sys
import copy

WIDTH, HEIGHT = 600, 600  # screen size
LINE_WIDTH = 3 # boards in one row

pygame.init()
FONT = pygame.font.SysFont("Arial", 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic-Tac-Toe ")

def empty_board():
    return [["" for _ in range(3)] for _ in range(3)]  # sub ttt boards using lists

class UltimateTicTacToe:
    def __init__(self):
        self.boards = [[empty_board() for _ in range(3)] for _ in range(3)]  # main ttt boards
        self.winners = [["" for _ in range(3)] for _ in range(3)]  # board for marking winners
        self.player = 'X'
        self.opponent = 'O'
        self.active_board = None  # (r, c)  # current active sub board coor
        self.current_player = 'X' 
        self.last_ai_move = None

    def make_move(self, br, bc, cr, cc, player):
        if self.active_board is not None and (br, bc) != self.active_board:
            return False
        
        if self.winners[br][bc] or self.boards[br][bc][cr][cc]:
            return False
        
        self.boards[br][bc][cr][cc] = player
        if self.check_winner(self.boards[br][bc]) == player:
            self.winners[br][bc] = player
            
        self.active_board = (cr, cc) if not self.winners[cr][cc] and not self.board_full(self.boards[cr][cc]) else None
        if self.current_player == 'X':
            self.current_player = 'O' 
        else:
            self.current_player = 'X'
        
        if player == 'O':
            self.last_ai_move = (br, bc, cr, cc)
        return True

    def board_full(self, board):
        return all(cell for row in board for cell in row)

    def game_winner(self):
        return self.check_winner(self.winners)

    def check_winner(self, board):  #check for winner on a sub board
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != "": return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != "": return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != "": return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != "": return board[0][2]
        return None

    def available_moves(self):  # check for all available moves
        moves = []
        for br in range(3):
            for bc in range(3):
                if self.winners[br][bc]: continue
                for cr in range(3):
                    for cc in range(3):
                        if self.boards[br][bc][cr][cc] == "":
                            if self.active_board is None or self.active_board == (br, bc):
                                moves.append((br, bc, cr, cc))
        return moves


def line_score(line):  # heruristics for chances of winning in a sub board
    if line.count('O') == 2 and line.count('') == 1:
        return 5
    if line.count('X') == 2 and line.count('') == 1:
        return -5
    return 0

def evaluate(game):  # heuristics for winning a sub board
    score = 0
    subgrid_win_score = 20
    center_cell_bonus = 2

    for br in range(3):
        for bc in range(3):
            winner = game.winners[br][bc]
            if winner == 'O':
                score += subgrid_win_score
            elif winner == 'X':
                score -= subgrid_win_score

    for br in range(3):
        for bc in range(3):
            board = game.boards[br][bc]
            for i in range(3):
                row = board[i]
                col = [board[r][i] for r in range(3)]
                score += line_score(row)
                score += line_score(col)
            diag1 = [board[i][i] for i in range(3)]
            diag2 = [board[i][2 - i] for i in range(3)]
            score += line_score(diag1)
            score += line_score(diag2)

            if board[1][1] == 'O':
                score += center_cell_bonus
            elif board[1][1] == 'X':
                score -= center_cell_bonus

    return score

def minimax(game, depth, alpha, beta, maximizing):  # minimax algo with alpha and beta pruning
    winner = game.game_winner()
    if winner == 'O': return 100 - depth, None
    if winner == 'X': return depth - 100, None
    if not game.available_moves() or depth == 4:
        return evaluate(game), None

    best_move = None
    if maximizing:  # AI max
        max_eval = -float('inf')
        for move in game.available_moves():
            new_game = copy.deepcopy(game)
            new_game.make_move(*move, 'O')
            eval, _ = minimax(new_game, depth + 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')  # human min
        for move in game.available_moves():
            new_game = copy.deepcopy(game)
            new_game.make_move(*move, 'X')
            eval, _ = minimax(new_game, depth + 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move


def draw_board(game):  # draw board GUI using pygame 
    screen.fill((245, 245, 245))
    cell_w = WIDTH // 9
    cell_h = HEIGHT // 9
    subgrid_w = WIDTH // 3
    subgrid_h = HEIGHT // 3

    for br in range(3):
        for bc in range(3):
            bx = bc * 3 * cell_w
            by = br * 3 * cell_h

            if game.active_board == (br, bc):
                highlight_rect = pygame.Rect(bx, by, 3 * cell_w, 3 * cell_h)
                pygame.draw.rect(screen, (210, 230, 255), highlight_rect)

            for cr in range(3):
                for cc in range(3):
                    x = bx + cc * cell_w
                    y = by + cr * cell_h
                    rect = pygame.Rect(x, y, cell_w, cell_h)
                    pygame.draw.rect(screen, (180, 180, 180), rect, 1)

                    mark = game.boards[br][bc][cr][cc]
                    if mark:
                        color = (0, 102, 204) if mark == 'X' else (204, 0, 0)
                        text = FONT.render(mark, True, color)
                        text_rect = text.get_rect(center=(x + cell_w // 2, y + cell_h // 2))
                        screen.blit(text, text_rect)

            winner = game.winners[br][bc]
            if winner:
                
                overlay_surf = pygame.Surface((3 * cell_w, 3 * cell_h), pygame.SRCALPHA)
                if winner == 'X' :
                    overlay_color = (0, 102, 204, 70) 
                else :
                    overlay_color = (204, 0, 0, 70)
                overlay_surf.fill(overlay_color)
                screen.blit(overlay_surf, (bx, by))
                                                    
                big_font = pygame.font.SysFont("Arial", 72, bold=True)
                win_text = big_font.render(winner, True, (0, 0, 0))
                text_rect = win_text.get_rect(center=(bx + 1.5 * cell_w, by + 1.5 * cell_h))
                screen.blit(win_text, text_rect)

    # Highlight AI move
    if game.last_ai_move:
        br, bc, cr, cc = game.last_ai_move
        x = (bc * 3 + cc) * cell_w
        y = (br * 3 + cr) * cell_h
        pygame.draw.rect(screen, (255, 100, 100), (x, y, cell_w, cell_h), 3)

    for i in range(1, 3):
        pygame.draw.line(screen, (0, 0, 0), (0, i * subgrid_h), (WIDTH, i * subgrid_h), LINE_WIDTH)
        pygame.draw.line(screen, (0, 0, 0), (i * subgrid_w, 0), (i * subgrid_w, HEIGHT), LINE_WIDTH)

    pygame.display.flip()


def cell_pos(pos): # calculate position of cell clicked with mouse
    x, y = pos
    cell_w = WIDTH // 9
    cell_h = HEIGHT // 9
    return y // cell_h // 3, x // cell_w // 3, (y // cell_h) % 3, (x // cell_w) % 3


def main():
    game = UltimateTicTacToe()
    draw_board(game)
    running = True

    while running:
        if game.current_player == 'X':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    br, bc, cr, cc = cell_pos(pygame.mouse.get_pos())
                    if game.make_move(br, bc, cr, cc, 'X'):
                        draw_board(game)
        else:
            _, move = minimax(game, 0, -float('inf'), float('inf'), True)  # player = AI then initiate minimax
            if move:
                game.make_move(*move, 'O')
                draw_board(game)

        winner = game.game_winner()
        if winner:
            draw_board(game)
            big_font = pygame.font.SysFont("Arial", 48, bold=True)
            text = big_font.render(f"{winner} wins!", True, (0, 128, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(5000)
            running = False

if __name__ == "__main__":
    main()
