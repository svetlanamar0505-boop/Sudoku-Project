
import pygame
import sys
from sudoku_generator import SudokuGenerator

pygame.init()

screen = pygame.display.set_mode((540, 780))
pygame.display.set_caption('Sudoku')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)


class Cell:
    def __init__(self, value, row, col, screen):
        self.row = row
        self.col = col
        self.value = value
        self.screen = screen
        self.sketched_value = 0
        self.selected = False
        self.is_given = value != 0

    def set_cell_value(self, value):
        self.value = value

    def set_sketched_value(self, value):
        self.sketched_value = value

    def draw(self):
        x = self.col * 60
        y = self.row * 60 + 150

        if self.selected:
            pygame.draw.rect(self.screen, LIGHT_GRAY, (x, y, 60, 60))
        else:
            pygame.draw.rect(self.screen, WHITE, (x, y, 60, 60))

        if self.selected:
            pygame.draw.rect(self.screen, RED, (x, y, 60, 60), 2)

        if self.value != 0:
            if self.is_given:
                font = pygame.font.SysFont('Arial', 30, bold=True)
                # fixed: str(self.value) -- value is an int, can't render int directly
                text = font.render(str(self.value), True, BLACK)
            else:
                font = pygame.font.SysFont('Arial', 30)
                text = font.render(str(self.value), True, BLUE)
            self.screen.blit(text, (x + (60 - text.get_width()) // 2, y + (60 - text.get_height()) // 2))

        elif self.sketched_value != 0:
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(str(self.sketched_value), True, GRAY)
            self.screen.blit(text, (x + 5, y + 5))


class Board:
    def __init__(self, width, height, screen, difficulty):
        self.width = width
        self.height = height
        self.screen = screen
        self.difficulty = difficulty

        if difficulty == "easy":
            removed = 30
        elif difficulty == "medium":
            removed = 40
        else:
            removed = 50

        # fixed: generate_sudoku only returns the board, not the solution
        # so we use SudokuGenerator directly to save the solution first
        gen = SudokuGenerator(9, removed)
        gen.fill_values()
        self.solution = [row[:] for row in gen.get_board()]
        gen.remove_cells()
        self.board = gen.get_board()

        self.cells = [
            [Cell(self.board[row][col], row, col, screen) for col in range(9)]
            for row in range(9)
        ]

        self.selected = None

    def draw(self):
        for row in range(9):
            for col in range(9):
                self.cells[row][col].draw()

        for i in range(10):
            if i % 3 == 0:
                thickness = 4
            else:
                thickness = 1

            pygame.draw.line(self.screen, BLACK, (0, 150 + i * 60), (540, 150 + i * 60), thickness)
            pygame.draw.line(self.screen, BLACK, (i * 60, 150), (i * 60, 690), thickness)

    def select(self, row, col):
        for r in range(9):
            for c in range(9):
                self.cells[r][c].selected = False

        self.cells[row][col].selected = True
        self.selected = (row, col)

    def click(self, x, y):
        if y < 150:
            return None

        row = (y - 150) // 60
        col = x // 60

        if row < 9 and col < 9:
            return (row, col)

        return None

    def clear(self):
        if self.selected:
            row, col = self.selected
            if not self.cells[row][col].is_given:
                self.cells[row][col].set_cell_value(0)
                self.cells[row][col].set_sketched_value(0)

    def sketch(self, value):
        if self.selected:
            row, col = self.selected
            if not self.cells[row][col].is_given:
                self.cells[row][col].set_sketched_value(value)
                self.cells[row][col].set_cell_value(0)

    def place_number(self, value):
        if self.selected:
            row, col = self.selected
            if not self.cells[row][col].is_given:
                self.cells[row][col].set_cell_value(value)
                self.cells[row][col].set_sketched_value(0)

    def reset_to_original(self):
        for row in range(9):
            for col in range(9):
                if not self.cells[row][col].is_given:
                    self.cells[row][col].set_cell_value(0)
                    self.cells[row][col].set_sketched_value(0)

    def is_full(self):
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].value == 0:
                    return False
        return True

    def update_board(self):
        # fixed: needs to return the board so check_board can use it
        current = []
        for row in range(9):
            r = []
            for col in range(9):
                r.append(self.cells[row][col].value)
            current.append(r)
        return current

    def find_empty(self):
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].value == 0:
                    return (row, col)
        return None

    def check_board(self):
        # fixed: compare return value of update_board to solution
        return self.update_board() == self.solution

    def move_selection(self, dr, dc):
        if self.selected:
            row, col = self.selected
            new_r = row + dr
            new_c = col + dc
            if 0 <= new_r < 9 and 0 <= new_c < 9:
                self.select(new_r, new_c)

def start_screen():
        while True:
            screen.fill(WHITE)
            mx, my = pygame.mouse.get_pos()

            font = pygame.font.SysFont('Arial', 50, bold=True)
            text = font.render("SUDOKU", True, BLACK)
            screen.blit(text, (270 - text.get_width() // 2, 250))

            font2 = pygame.font.SysFont('Arial', 20)
            text2 = font2.render("Select a Difficulty:", True, BLACK)
            screen.blit(text2, (270 - text2.get_width() // 2, 330))

            easy_rect = pygame.Rect(75, 390, 120, 40)
            medium_rect = pygame.Rect(210, 390, 120, 40)
            hard_rect = pygame.Rect(345, 390, 120, 40)

            pygame.draw.rect(screen, LIGHT_GRAY, easy_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, medium_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, hard_rect)

            font3 = pygame.font.SysFont('Arial', 18)
            screen.blit(font3.render("Easy", True, BLACK), (75 + 60 - font3.size("Easy")[0] // 2, 400))
            screen.blit(font3.render("Medium", True, BLACK), (210 + 60 - font3.size("Medium")[0] // 2, 400))
            screen.blit(font3.render("Hard", True, BLACK), (345 + 60 - font3.size("Hard")[0] // 2, 400))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_rect.collidepoint(mx, my):
                        return "easy"
                    if medium_rect.collidepoint(mx, my):
                        return "medium"
                    if hard_rect.collidepoint(mx, my):
                        return "hard"

            pygame.display.flip()

def game_screen(difficulty):
        board = Board(540, 780, screen, difficulty)

        while True:
            screen.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            font = pygame.font.SysFont('Arial', 30, bold=True)
            text = font.render("SUDOKU", True, BLACK)
            screen.blit(text, (270 - text.get_width() // 2, 20))
            board.draw()
            reset_rect = pygame.Rect(80, 700, 120, 40)
            restart_rect = pygame.Rect(210, 700, 120, 40)
            exit_rect = pygame.Rect(340, 700, 120, 40)

            pygame.draw.rect(screen, LIGHT_GRAY, reset_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, restart_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, exit_rect)
            font2 = pygame.font.SysFont('Arial', 18)
            screen.blit(font2.render("Reset", True, BLACK), (80 + 60 - font2.size("Reset")[0] // 2, 710))
            screen.blit(font2.render("Restart", True, BLACK), (210 + 60 - font2.size("Restart")[0] // 2, 710))
            screen.blit(font2.render("Exit", True, BLACK), (340 + 60 - font2.size("Exit")[0] // 2, 710))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if reset_rect.collidepoint(mx, my):
                        board.reset_to_original()
                    elif restart_rect.collidepoint(mx, my):
                        return "restart"
                    elif exit_rect.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
                    else:
                        pos = board.click(mx, my)
                        if pos is not None:
                            board.select(pos[0], pos[1])
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        board.move_selection(-1, 0)
                    elif event.key == pygame.K_DOWN:
                        board.move_selection(1, 0)
                    elif event.key == pygame.K_LEFT:
                        board.move_selection(0, -1)
                    elif event.key == pygame.K_RIGHT:
                        board.move_selection(0, 1)
                    elif event.key == pygame.K_BACKSPACE:
                        board.clear()
                    elif event.key == pygame.K_RETURN:
                        if board.selected:
                            row, col = board.selected
                            cell = board.cells[row][col]
                            if cell.sketched_value != 0:
                                board.place_number(cell.sketched_value)
                                if board.is_full():
                                    if board.check_board():
                                        return "win"
                                    else:
                                        return "lose"
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        board.sketch(event.key - pygame.K_0)
            pygame.display.flip()

def win_screen():
        while True:
            screen.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            font = pygame.font.SysFont('Arial', 50, bold=True)
            text = font.render("You Win!", True, GREEN)
            screen.blit(text, (270 - text.get_width() // 2, 300))
            again_rect = pygame.Rect(100, 400, 150, 40)
            quit_rect = pygame.Rect(290, 400, 150, 40)
            pygame.draw.rect(screen, LIGHT_GRAY, again_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, quit_rect)

            font2 = pygame.font.SysFont('Arial', 18)
            screen.blit(font2.render("Play Again", True, BLACK), (100 + 75 - font2.size("Play Again")[0] // 2, 410))
            screen.blit(font2.render("Quit", True, BLACK), (290 + 75 - font2.size("Quit")[0] // 2, 410))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if again_rect.collidepoint(mx, my):
                        return "restart"
                    if quit_rect.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()

def game_over_screen():
        while True:
            screen.fill(WHITE)
            mx, my = pygame.mouse.get_pos()

            font = pygame.font.SysFont('Arial', 50, bold=True)
            text = font.render("Game Over :(", True, RED)
            screen.blit(text, (270 - text.get_width() // 2, 300))
            again_rect = pygame.Rect(100, 400, 150, 40)
            quit_rect = pygame.Rect(290, 400, 150, 40)
            pygame.draw.rect(screen, LIGHT_GRAY, again_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, quit_rect)
            font2 = pygame.font.SysFont('Arial', 18)
            screen.blit(font2.render("Play Again", True, BLACK), (100 + 75 - font2.size("Play Again")[0] // 2, 410))
            screen.blit(font2.render("Quit", True, BLACK), (290 + 75 - font2.size("Quit")[0] // 2, 410))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if again_rect.collidepoint(mx, my):
                        return "restart"
                    if quit_rect.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()

while True:
        difficulty = start_screen()
        result = game_screen(difficulty)

        if result == "win":
            action = win_screen()
        elif result == "lose":
            action = game_over_screen()
        else:
            action = "restart"
        if action == "restart":
            continue