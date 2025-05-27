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
FALL_SPEED = 30  # 一定の落下速度 (フレーム数)

class Block:
    def __init__(self, block_type):
        self.shapes = [[], [],  # empty block and wall
                       [[0, -1], [0, 0], [0, 1], [0, 2]],  # I block
                       [[-1, -1], [0, -1], [0, 0], [0, 1]],  # J block
                       [[0, -1], [0, 0], [0, 1], [-1, 1]],  # L block
                       [[0, -1], [0, 0], [-1, 0], [-1, 1]],  # S blosk
                       [[-1, -1], [-1, 0], [0, 0], [0, 1]],  # Z block
                       [[0, -1], [0, 0], [-1, 0], [0, 1]],  # T block
                       [[0, 0], [-1, 0], [0, 1], [-1, 1]]]  # square

        self.block_type = block_type
        self.shape = copy.deepcopy(self.shapes[block_type])
        self.row = 1  # initial position
        self.col = 5
        self.level = 0
        self.count = 0

    # key command movement
    def move(self, board, direction):  # direction down:0 left:1 right:2
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

    def rotate(self, board, direction):  # clockwise:0 anticloskwise:1
        # long bar rotates differently
        if self.block_type == 2:
            if direction == 0:
                for dx in self.shape:
                    dx[0], dx[1] = dx[1], 1 - dx[0]
            elif direction == 1:
                for dx in self.shape:
                    dx[0], dx[1] = 1 - dx[1], dx[0]

        # square doesn`t rotate
        elif self.block_type == 8:
            pass

        # other blocks
        elif direction == 0:
            for dx in self.shape:
                dx[0], dx[1] = dx[1], -dx[0]
        elif direction == 1:
            for dx in self.shape:
                dx[0], dx[1] = -dx[1], dx[0]

        self.rotate_correction(board)

    def rotate_correction(self, board):
        move_priority = [[0, 0], [0, -1], [0, 1], [-1, 0], [1, 0], [2, 0], [-1, 1], [1, 1]]
        for direction in move_priority:
            if self.moveable(board, direction):
                self.row += direction[0]
                self.col += direction[1]
                return

        direction = [0, 2]
        while not self.moveable(board, direction):
            direction[1] += 1
        self.row += direction[0]
        self.col += direction[1]

    # moving downward due to time
    def drop(self, board):
        if self.count < FALL_SPEED:
            self.count += 1
            return 0
        elif self.moveable(board, [1, 0]):
            self.count = 0
            self.row += 1
            return 0
        else:
            return 1  # make new block

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
            if not (2 <= row < MAX_ROW + 2 and 1 <= col < MAX_COL + 1):  # placed block outside screen
                return 1
            board[row][col] = self.block_type
        return 0
    
class Record:
    def __init__(self):
        self.cleared_row = 0
        self.score = 0
        self.level = 0
        self.score_table = [0, 80, 100, 300, 1200]
        self.level_up = [2, 5, 8, 12, 16, 20, 25, 30, 35, 40, # level 0 to 9
                         46, 52, 58, 64, 70, 77, 84, 91, 98, 105, # level 10 to 19
                         112, 120, 128, 136, 144, 152, 160, 168, 177, 186, # level 20 to 29
                         195, 204, 213, 222, 231, 240, 255, 270, 285, 300, 1000] # 30 to 40
        
    def update(self, count):
        self.score += self.score_table[count]*(self.level+1)
        self.cleared_row += count
        
        if self.level < 40 and self.level_up[self.level] <= self.cleared_row: # level 40 is max
            self.level += 1
    
    def show(self, screen):
        font = pygame.font.Font(None, 50)
        text1 = font.render("LEVEL:", True, (255, 255, 255))
        level = font.render("{}".format(self.level), True, (255, 255, 255))
        screen.blit(text1, [500, 300])
        screen.blit(level, [700, 300])
        
        text2 = font.render("CLEARED ROW:", True, (255, 255, 255))
        cleared_row = font.render("{}".format(self.cleared_row), True, (255, 255, 255))
        screen.blit(text2, [500, 360])
        screen.blit(cleared_row, [900, 360])
        
        text3 = font.render("SCORE", True, (255, 255, 255))
        score = font.render("{0:012d}".format(self.score), True, (255, 255, 255))
        screen.blit(text3, [500, 420])
        screen.blit(score, [600, 480])
        
# ブロックとボードの初期化
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

# 入力　ボード
# 出力　消える行数、消える行の番号
def find_deleting_row(board):
    count = 0
    row_numbers = []
    for row in range(2, MAX_ROW + 2):
        if all(board[row][col] != 0 for col in range(1, MAX_COL + 1)):
            count += 1
            row_numbers.append(row)
    return count, row_numbers

# 行削除
# 入力　スクリーン、ボード、消す行番号
# 出力　なし
def delete_row(screen, board, row_number, block_color):
    n_col = 4
    for row in row_number:
        for col in range(1, MAX_COL + 1):
            board[row][col] = 0
    for _ in range(n_col + MAX_COL):
        for row in row_number:
            for col in reversed(range(1, MAX_COL + 1)):
                board[row][col] = board[row][col - 1]
            if _ < n_col:
                board[row][1] = 9
        pygame.time.wait(8)
        draw_board(screen, board, block_color)
        pygame.display.update()

    for deleting_row in row_number:
        for row in reversed(range(2, deleting_row + 1)):
            for col in range(1, MAX_COL + 1):
                board[row][col] = board[row - 1][col]

# ゲームボードの描画
# 入力　スクリーン、ゲームボード、ブロックの色
# 出力　なし
def draw_board(screen, board, block_color):
    for row in range(2, MAX_ROW + 3):
        for col in range(MAX_COL + 2):
            draw_x = GRID_OFFSET_X + BLOCK_SIZE * col
            draw_y = GRID_OFFSET_Y + BLOCK_SIZE * (row - 2)
            pygame.draw.rect(screen, (0, 0, 0), Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
            if board[row][col] < 2:
                pygame.draw.rect(screen, block_color[board[row][col]],
                                 Rect(draw_x + 1, draw_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            else:
                pygame.draw.rect(screen, block_color[board[row][col]],
                                 Rect(draw_x + 2, draw_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 770))
    pygame.display.set_caption("KOKARIS")  # title bar

    block_color = [(50, 50, 50), (150, 150, 150), (255, 0, 0), (0, 0, 255), (255, 165, 0),
                   (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (200, 200, 200), (100, 100, 100)]

    board, block = initialize_game()
    next_block_type = random.randint(2, 8)

    game_over = False

    while not game_over:
        pygame.time.wait(10)

        screen.fill((0, 0, 0))  # fill with black

        draw_board(screen, board, block_color)
        block.draw(screen, block_color)
        record = Record()
        # move command
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
                if not block.moveable(board, [0, 0]):
                    game_over = True
        record.show(screen)
        pygame.display.update()

        for event in pygame.event.get():
            # close button
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # escape key pressed
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # block rotation
                if event.key == K_a or event.key == K_SPACE:  # anti-clockwise
                    block.rotate(board, 1)
                if event.key == K_s:  # clockwise
                    block.rotate(board, 0)

    # Game Over: Do nothing, the loop will just stop
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