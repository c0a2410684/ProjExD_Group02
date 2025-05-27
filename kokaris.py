import pygame
from pygame.locals import *
import sys
import random
import copy

# 定数
MAX_ROW = 20
MAX_COL = 10
BLOCK_SIZE = 35
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 30
FALL_SPEED = 30

class Block:
    def __init__(self, block_type):
        self.shapes = [[], [],  # empty block and wall
                       [[0, -1], [0, 0], [0, 1], [0, 2]],  # I
                       [[-1, -1], [0, -1], [0, 0], [0, 1]],  # J
                       [[0, -1], [0, 0], [0, 1], [-1, 1]],  # L
                       [[0, -1], [0, 0], [-1, 0], [-1, 1]],  # S
                       [[-1, -1], [-1, 0], [0, 0], [0, 1]],  # Z
                       [[0, -1], [0, 0], [-1, 0], [0, 1]],  # T
                       [[0, 0], [-1, 0], [0, 1], [-1, 1]]]  # O

        self.block_type = block_type
        self.shape = copy.deepcopy(self.shapes[block_type])
        self.row = 1
        self.col = 5
        self.count = 0

    def move(self, board, direction):
        if direction == 0 and self.moveable(board, [1, 0]):
            self.row += 1
        elif direction == 1 and self.moveable(board, [0, -1]):
            self.col -= 1
        elif direction == 2 and self.moveable(board, [0, 1]):
            self.col += 1

    def moveable(self, board, direction):
        drow, dcol = direction
        for dx in self.shape:
            row = self.row + dx[0] + drow
            col = self.col + dx[1] + dcol
            if not (0 <= row < MAX_ROW + 3 and 0 <= col < MAX_COL + 2 and board[row][col] == 0):
                return False
        return True

    def rotate(self, board, direction):
        old_shape = copy.deepcopy(self.shape)

        if self.block_type == 2:
            if direction == 0:
                for dx in self.shape:
                    dx[0], dx[1] = dx[1], 1 - dx[0]
            elif direction == 1:
                for dx in self.shape:
                    dx[0], dx[1] = 1 - dx[1], dx[0]
        elif self.block_type == 8:
            return
        else:
            if direction == 0:
                for dx in self.shape:
                    dx[0], dx[1] = dx[1], -dx[0]
            elif direction == 1:
                for dx in self.shape:
                    dx[0], dx[1] = -dx[1], dx[0]

        if not self.rotate_correction(board):
            self.shape = old_shape

    def rotate_correction(self, board):
        move_priority = [[0, 0], [0, -1], [0, 1], [-1, 0], [1, 0]]
        for direction in move_priority:
            if self.moveable(board, direction):
                self.row += direction[0]
                self.col += direction[1]
                return True
        return False

    def drop(self, board):
        if self.count < FALL_SPEED:
            self.count += 1
            return 0
        elif self.moveable(board, [1, 0]):
            self.count = 0
            self.row += 1
            return 0
        else:
            return 1

    def draw(self, screen, block_color):
        for row, col in self.shape:
            draw_x = GRID_OFFSET_X + BLOCK_SIZE * (self.col + col)
            draw_y = GRID_OFFSET_Y + BLOCK_SIZE * (self.row + row - 2)
            if self.row + row > 1:
                pygame.draw.rect(screen, (0, 0, 0), Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, block_color[self.block_type],
                                 Rect(draw_x + 2, draw_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4))

    def place(self, board):
        for dx in self.shape:
            row = self.row + dx[0]
            col = self.col + dx[1]
            if not (2 <= row < MAX_ROW + 2 and 1 <= col < MAX_COL + 1):
                return 1
            board[row][col] = self.block_type
        return 0

def initialize_game():
    board = [[0 for _ in range(MAX_COL + 2)] for _ in range(MAX_ROW + 3)]
    for col in range(MAX_COL + 2):
        board[-1][col] = 1
    for row in range(MAX_ROW + 3):
        board[row][0] = 1
        board[row][-1] = 1

    block_type = random.randint(2, 8)
    block = Block(block_type)
    return board, block

def find_deleting_row(board):
    count = 0
    row_numbers = []
    for row in range(2, MAX_ROW + 2):
        if all(board[row][col] != 0 for col in range(1, MAX_COL + 1)):
            count += 1
            row_numbers.append(row)
    return count, row_numbers

def delete_row(screen, board, row_number, block_color):
    for row in row_number:
        for col in range(1, MAX_COL + 1):
            board[row][col] = 0
    for deleting_row in row_number:
        for row in reversed(range(2, deleting_row + 1)):
            for col in range(1, MAX_COL + 1):
                board[row][col] = board[row - 1][col]

def draw_board(screen, board, block_color):
    for row in range(2, MAX_ROW + 3):
        for col in range(MAX_COL + 2):
            draw_x = GRID_OFFSET_X + BLOCK_SIZE * col
            draw_y = GRID_OFFSET_Y + BLOCK_SIZE * (row - 2)
            pygame.draw.rect(screen, (0, 0, 0), Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, block_color[board[row][col]],
                             Rect(draw_x + 1, draw_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 770))
    pygame.display.set_caption("KOKARIS")

    block_color = [(50, 50, 50), (150, 150, 150), (255, 0, 0), (0, 0, 255), (255, 165, 0),
                   (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (200, 200, 200), (100, 100, 100)]

    board, block = initialize_game()
    next_block_type = random.randint(2, 8)

    game_over = False
    hold_block = None
    can_hold = True

    while not game_over:
        pygame.time.wait(10)
        screen.fill((0, 0, 0))

        draw_board(screen, board, block_color)
        block.draw(screen, block_color)

        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_DOWN]:
            block.move(board, 0)
        if pressed_key[K_LEFT]:
            block.move(board, 1)
        if pressed_key[K_RIGHT]:
            block.move(board, 2)

        bottom_flag = block.drop(board)
        if bottom_flag == 1:
            if block.place(board) == 1:
                game_over = True
            else:
                count, row_numbers = find_deleting_row(board)
                if count > 0:
                    delete_row(screen, board, row_numbers, block_color)
                block = Block(next_block_type)
                next_block_type = random.randint(2, 8)
                can_hold = True
                if not block.moveable(board, [0, 0]):
                    game_over = True

        if hold_block is not None:
            for dx in hold_block.shape:
                row = 2 + dx[0]
                col = 15 + dx[1]
                pygame.draw.rect(screen, block_color[hold_block.block_type],
                                 Rect(GRID_OFFSET_X + col * BLOCK_SIZE,
                                      GRID_OFFSET_Y + row * BLOCK_SIZE, BLOCK_SIZE - 4, BLOCK_SIZE - 4))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_LSHIFT:
                    if can_hold:
                        if hold_block is None:
                            hold_block = block
                            block = Block(next_block_type)
                            next_block_type = random.randint(2, 8)
                        else:
                            hold_block, block = block, hold_block
                        block.row, block.col = 1, 5
                        can_hold = False
                elif event.key == K_a or event.key == K_SPACE:
                    block.rotate(board, 1)
                elif event.key == K_s:
                    block.rotate(board, 0)

    while game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
