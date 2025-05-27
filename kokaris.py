import pygame
from pygame.locals import *
import sys
import random
import copy

# 定数
MAX_ROW = 20
MAX_COL = 10
BLOCK_SIZE = 35
BOARD_OFFSET_X = 30
BOARD_OFFSET_Y = 30

class Block:
    def __init__(self, block_type):
        self.shapes = [[], [],  # empty block and wall
                       [[0, -1], [0, 0], [0, 1], [0, 2]],  # I block
                       [[-1, -1], [0, -1], [0, 0], [0, 1]],  # J block
                       [[0, -1], [0, 0], [0, 1], [-1, 1]],  # L block
                       [[0, -1], [0, 0], [-1, 0], [-1, 1]],  # S block
                       [[-1, -1], [-1, 0], [0, 0], [0, 1]],  # Z block
                       [[0, -1], [0, 0], [-1, 0], [0, 1]],  # T block
                       [[0, 0], [-1, 0], [0, 1], [-1, 1]]]  # square

        self.block_type = block_type
        self.shape = copy.deepcopy(self.shapes[block_type])
        self.row = 1  # initial position
        self.col = 5
        self.level = 0
        self.drop_rate = 60  # 固定の落下速度
        self.count = 0

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
            if 0 <= row < MAX_ROW + 3 and 0 <= col < MAX_COL + 2 and board[row][col] != 0:
                return False

        return True
    
    def drop(self, board):
        if self.count < self.drop_rate:
            self.count += 1
            return 0
        elif self.moveable(board, [1, 0]):
            self.count = 0
            self.row += 1
            return 0
        else:
            return 1  # make new block

    def place(self, board):
        for dx in self.shape:
            row = self.row + dx[0]
            col = self.col + dx[1]
            if not (2 <= row < MAX_ROW + 2 and 1 <= col < MAX_COL + 1):
                return 1 # ゲームオーバー
            board[row][col] = self.block_type
        return 0

    def draw(self, screen, block_color):
        for row_offset, col_offset in self.shape:
            row = self.row + row_offset
            col = self.col + col_offset
            if row > 1:
                pygame.draw.rect(screen, (0, 0, 0),
                                 Rect(BOARD_OFFSET_X + BLOCK_SIZE * col,
                                      BOARD_OFFSET_Y + BLOCK_SIZE * (row - 2),
                                      BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, block_color[self.block_type],
                                 Rect(BOARD_OFFSET_X + 2 + BLOCK_SIZE * col,
                                      BOARD_OFFSET_Y + 2 + BLOCK_SIZE * (row - 2),
                                      BLOCK_SIZE - 4, BLOCK_SIZE - 4))

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


def gameover(screen, record):
    """
    gameover時に、リザルト画面を表示する

    処理内容:
    - 黒背景に「GAMEOVER」と「RESULT」の文字を描画する。
    - ゲーム中のスコア・レベルなどを表示する。
    - 画像（こうかとん）を表示する。
    - ユーザーが[ESC]キーを押すか、ウィンドウを閉じるまで待機する。
    """
    screen.fill((0, 0, 0))
    image = pygame.image.load("ex5/.fig/bijokokaton.png") #こうかとん（女）の画像
    image = pygame.transform.scale(image, (481, 565))  
    screen.blit(image, (400, 100))  
    #gameoverの文字表示
    font1 = pygame.font.Font(None, 80)
    text1 = font1.render("GAMEOVER", True, (255, 0, 0))
    screen.blit(text1, [200, 100])
    #resultの文字表示
    font2 = pygame.font.Font(None, 60)
    text2 = font2.render("RESULT", True, (255, 255, 255))
    screen.blit(text2, [200, 200])
    #revelの文字と数値を表示
    font = pygame.font.Font(None, 50)
    text3 = font.render("LEVEL:", True, (255, 255, 255))
    level = font.render("{}".format(record.level), True, (255, 255, 255))
    screen.blit(text3, [100, 300])
    screen.blit(level, [400, 300])
    #scoreの文字と数値を表示
    text4 = font.render("SCORE", True, (255, 255, 255))
    score = font2.render("{0:012d}".format(record.score), True, (255, 255, 255))
    screen.blit(text4, [100, 400])
    screen.blit(score, [200, 450])

    pygame.display.update()
    #リザルト画面からの退出
    while(1):
        pygame.time.wait(50)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def draw_board(screen, board, block_color):
    for row in range(2, MAX_ROW + 3):
        for col in range(MAX_COL + 2):
            pygame.draw.rect(screen, (0, 0, 0),
                             Rect(BOARD_OFFSET_X + BLOCK_SIZE * col,
                                  BOARD_OFFSET_Y + BLOCK_SIZE * (row - 2),
                                  BLOCK_SIZE, BLOCK_SIZE))
            if 2 <= board[row][col] <= 8:
                pygame.draw.rect(screen, block_color[board[row][col]],
                                 Rect(BOARD_OFFSET_X + 2 + BLOCK_SIZE * col,
                                      BOARD_OFFSET_Y + 2 + BLOCK_SIZE * (row - 2),
                                      BLOCK_SIZE - 4, BLOCK_SIZE - 4))

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((1000, 750))
    pygame.display.set_caption("Simple Tetris")

    block_color = [(50, 50, 50), (150, 150, 150), (255, 0, 0), (0, 0, 255), (255, 165, 0),
                   (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0)]

    board, block = initialize_game()
    game_over = False
    record = Record()

    while not game_over:
        pygame.time.wait(10)
        screen.fill((0, 0, 0))
        draw_board(screen, board, block_color)

        if block:
            pressed_key = pygame.key.get_pressed()
            if pressed_key[K_DOWN]:
                block.move(board, 0)
            if pressed_key[K_LEFT]:
                block.move(board, 1)
            if pressed_key[K_RIGHT]:
                block.move(board, 2)

            if block.drop(board) == 1:
                if block.place(board) == 1:
                    gameover(screen,record)
                    game_over = True
                else:
                    block_type = random.randint(2, 8)
                    block = Block(block_type)
            block.draw(screen, block_color)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    print("Game Over")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    