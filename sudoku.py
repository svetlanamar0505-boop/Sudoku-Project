
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