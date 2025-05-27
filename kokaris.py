import pygame
from pygame.locals import *
import sys
import random
import copy
from typing import List, Tuple
from pathlib import Path

# 定数
MAX_ROW: int = 20
MAX_COL: int = 10
BLOCK_SIZE: int = 35
GRID_OFFSET_X: int = 30
GRID_OFFSET_Y: int = 30
FALL_SPEED: int = 60  # 初期落下速度 (フレーム数)

class Block:
    """
    テトリスのブロックを表現するクラス。
    形状、位置、落下速度などを管理する。
    """
    def __init__(self, block_type: int) -> None:
        """
        Blockクラスの初期化。

        Args:
            block_type (int): ブロックの種類 (2から8までの整数)。
        """
        self.shapes: List[List[List[int]]] = [[], [],  # empty block and wall
                                                [[0, -1], [0, 0], [0, 1], [0, 2]],  # I block
                                                [[-1, -1], [0, -1], [0, 0], [0, 1]],  # J block
                                                [[0, -1], [0, 0], [0, 1], [-1, 1]],  # L block
                                                [[0, -1], [0, 0], [-1, 0], [-1, 1]],  # S blosk
                                                [[-1, -1], [-1, 0], [0, 0], [0, 1]],  # Z block
                                                [[0, -1], [0, 0], [-1, 0], [0, 1]],  # T block
                                                [[0, 0], [-1, 0], [0, 1], [-1, 1]]]  # square

        self.block_type: int = block_type
        self.shape: List[List[int]] = copy.deepcopy(self.shapes[block_type])
        self.row: int = 1  # 初期位置 (行)
        self.col: int = 5  # 初期位置 (列)
        self.count: int = 0  # 落下処理のためのカウンター

    def move(self, board: List[List[int]], direction: int) -> None:
        """
        ブロックを指定された方向に移動させる。

        Args:
            board (List[List[int]]): ゲームボードの状態。
            direction (int): 移動方向 (0: 下, 1: 左, 2: 右)。
        """
        if direction == 0 and self.moveable(board, [1, 0]):
            self.row += 1
        elif direction == 1 and self.moveable(board, [0, -1]):
            self.col -= 1
        elif direction == 2 and self.moveable(board, [0, 1]):
            self.col += 1

    def moveable(self, board: List[List[int]], direction: List[int]) -> bool:
        """
        指定された方向にブロックが移動可能かどうかを判定する。

        Args:
            board (List[List[int]]): ゲームボードの状態。
            direction (List[int]): 移動方向のオフセット ([delta_row, delta_col])。

        Returns:
            bool: 移動可能であればTrue、不可能であればFalse。
        """
        drow, dcol = direction

        for dx in self.shape:
            row: int = self.row + dx[0] + drow
            col: int = self.col + dx[1] + dcol
            if not (0 <= row < MAX_ROW + 3 and 0 <= col < MAX_COL + 2 and board[row][col] == 0):
                return False

        return True

    def rotate(self, board: List[List[int]], direction: int) -> None:
        """
        ブロックを指定された方向に回転させる。

        Args:
            board (List[List[int]]): ゲームボードの状態。
            direction (int): 回転方向 (0: 時計回り, 1: 反時計回り)。
        """
        # Iブロックの回転処理
        if self.block_type == 2:
            if direction == 0:
                for dx in self.shape:
                    dx[0], dx[1] = dx[1], 1 - dx[0]
            elif direction == 1:
                for dx in self.shape:
                    dx[0], dx[1] = 1 - dx[1], dx[0]
        # Oブロックは回転しない
        elif self.block_type == 8:
            pass
        # その他のブロックの回転処理
        elif direction == 0:
            for dx in self.shape:
                dx[0], dx[1] = dx[1], -dx[0]
        elif direction == 1:
            for dx in self.shape:
                dx[0], dx[1] = -dx[1], dx[0]

        self.rotate_correction(board)

    def rotate_correction(self, board: List[List[int]]) -> None:
        """
        回転後のブロックの位置を補正し、壁や他のブロックとの衝突を避ける。

        Args:
            board (List[List[int]]): ゲームボードの状態。
        """
        move_priority: List[List[int]] = [[0, 0], [0, -1], [0, 1], [-1, 0], [1, 0], [2, 0], [-1, 1], [1, 1]]
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

    def drop(self, board: List[List[int]]) -> int:
        """
        ブロックを時間経過によって下方向に落下させる。

        Args:
            board (List[List[int]]): ゲームボードの状態。

        Returns:
            int: 落下しなかった場合は0、新しいブロックを作成する必要がある場合は1。
        """
        if self.count < FALL_SPEED:
            self.count += 1
            return 0
        elif self.moveable(board, [1, 0]):
            self.count = 0
            self.row += 1
            return 0
        else:
            return 1  # 新しいブロックを作成

    def draw(self, screen: pygame.Surface, block_color: List[Tuple[int, int, int]]) -> None:
        """
        ブロックをゲーム画面に描画する。

        Args:
            screen (pygame.Surface): 描画先のPygameサーフェス。
            block_color (List[Tuple[int, int, int]]): ブロックの色リスト。
        """
        for row, col in self.shape:
            draw_x: int = GRID_OFFSET_X + BLOCK_SIZE * (self.col + col)
            draw_y: int = GRID_OFFSET_Y + BLOCK_SIZE * (self.row + row - 2)
            if self.row + row > 1:  # 画面外の部分は描画しない
                pygame.draw.rect(screen, (0, 0, 0), Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, block_color[self.block_type],
                                 Rect(draw_x + 2, draw_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4))

    def place(self, board: List[List[int]]) -> int:
        """
        ブロックをゲームボードに固定する。

        Args:
            board (List[List[int]]): ゲームボードの状態。

        Returns:
            int: ブロックが画面外に固定された場合は1 (ゲームオーバー)、正常に固定された場合は0。
        """
        for dx in self.shape:
            row: int = self.row + dx[0]
            col: int = self.col + dx[1]
            if not (2 <= row < MAX_ROW + 2 and 1 <= col < MAX_COL + 1):  # 固定されたブロックが画面外
                return 1
            board[row][col] = self.block_type
        return 0
    
class Score:
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
def initialize_game() -> Tuple[List[List[int]], Block]:
    """
    ゲームの初期化を行う。ゲームボードと最初のブロックを作成する。

    Returns:
        Tuple[List[List[int]], Block]: 初期化されたゲームボードと最初のブロック。
    """
    board: List[List[int]] = [[0 for _ in range(MAX_COL + 2)] for _ in range(MAX_ROW + 3)]
    # 壁の配置
    for col in range(MAX_COL + 2):
        board[-1][col] = 1
    for row in range(MAX_ROW + 3):
        board[row][0] = 1
        board[row][-1] = 1

    block_type: int = random.randint(2, 8)
    block: Block = Block(block_type)

    return board, block

# 入力　ボード
# 出力　消える行数、消える行の番号
def find_deleting_row(board: List[List[int]]) -> Tuple[int, List[int]]:
    """
    消去する行を探索する。

    Args:
        board (List[List[int]]): ゲームボードの状態。

    Returns:
        Tuple[int, List[int]]: 消去される行数と、それらの行番号のリスト。
    """
    count: int = 0
    row_numbers: List[int] = []
    for row in range(2, MAX_ROW + 2):
        if all(board[row][col] != 0 for col in range(1, MAX_COL + 1)):
            count += 1
            row_numbers.append(row)
    return count, row_numbers

# 行削除
# 入力　スクリーン、ボード、消す行番号
# 出力　なし
def delete_row(screen: pygame.Surface, board: List[List[int]], row_number: List[int],
               block_color: List[Tuple[int, int, int]]) -> None:
    """
    指定された行を削除し、上の行を詰めるアニメーションを行う。

    Args:
        screen (pygame.Surface): 描画先のPygameサーフェス。
        board (List[List[int]]): ゲームボードの状態。
        row_number (List[int]): 削除する行番号のリスト。
        block_color (List[Tuple[int, int, int]]): ブロックの色リスト。
    """
    n_col: int = 4  # 消去アニメーションの横方向の移動量
    for row in row_number:
        for col in range(1, MAX_COL + 1):
            board[row][col] = 0
    for _ in range(n_col + MAX_COL):
        for row in row_number:
            for col in reversed(range(1, MAX_COL + 1)):
                board[row][col] = board[row][col - 1]
            if _ < n_col:
                board[row][1] = 9  # 消去アニメーションの色
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
def draw_board(screen: pygame.Surface, board: List[List[int]],
               block_color: List[Tuple[int, int, int]]) -> None:
    """
    ゲームボードを描画する。

    Args:
        screen (pygame.Surface): 描画先のPygameサーフェス。
        board (List[List[int]]): ゲームボードの状態。
        block_color (List[Tuple[int, int, int]]): ブロックの色リスト。
    """
    for row in range(2, MAX_ROW + 3):
        for col in range(MAX_COL + 2):
            draw_x: int = GRID_OFFSET_X + BLOCK_SIZE * col
            draw_y: int = GRID_OFFSET_Y + BLOCK_SIZE * (row - 2)
            pygame.draw.rect(screen, (0, 0, 0), Rect(draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
            if board[row][col] < 2:  # 壁または空
                pygame.draw.rect(screen, block_color[board[row][col]],
                                 Rect(draw_x + 1, draw_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            else:  # ブロック
                pygame.draw.rect(screen, block_color[board[row][col]],
                                 Rect(draw_x + 2, draw_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4))
                


def start(screen: pygame.Surface):
    """
    追加機能
    引数：screen
    スタート画面を描画する
    ENTERでスタート、ESCAPEでゲーム終了
    """
    font1 = pygame.font.Font(None, 150)
    font2 = pygame.font.Font(None, 50)
    title = font1.render("KOKARIS", True, (255, 255, 255)) #画面に表示する文字
    text = font2.render("Press ENTER to start", True, (255, 255, 255)) #画面に表示する文字

    screen.blit(title, [270, 260])
    screen.blit(text, [320, 560])

    pygame.display.update() #スタート画面に更新する
    
    while True:
        pygame.time.wait(50)
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]: #escが押されたときゲームを閉じる
            pygame.quit()
            sys.exit()
        if keys[K_RETURN]: #enterがおされたとき、ゲーム画面に移行する
            break
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


def main() -> None:
    """
    メインゲームループ。
    """
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((1000, 770))
    pygame.display.set_caption("KOKARIS")  # タイトルバー

    block_color: List[Tuple[int, int, int]] = [(50, 50, 50), (150, 150, 150), (255, 0, 0), (0, 0, 255), (255, 165, 0),
                                                (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0),
                                                (200, 200, 200), (100, 100, 100)]

    board, block = initialize_game()
    next_block_type: int = random.randint(2, 8)

    game_over: bool = False
    record = Score()
    
    start_time: int = pygame.time.get_ticks()  # ゲーム開始時の時間を記録

    script_dir = Path(__file__).resolve().parent
    sound_path = script_dir / "fig/sample.wav"  #相対パス
    # pygame.mixer.music.load(str(sound_path))  #音声の再生
    # pygame.mixer.music.play()

    start(screen)  #スタート画面
    game_over = False
    
    

    while not game_over:
        pygame.time.wait(10)

        screen.fill((0, 0, 0))  # 画面を黒で塗りつぶす

        draw_board(screen, board, block_color)
        block.draw(screen, block_color)

        # キー入力処理
        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_DOWN]:
            block.move(board, 0)
        if pressed_key[K_LEFT]:
            block.move(board, 1)
        if pressed_key[K_RIGHT]:
            block.move(board, 2)

        # ブロックの落下処理
        bottom_flag: int = block.drop(board)
        if bottom_flag == 1:
            if block.place(board) == 1:
                game_over = True
            else:
                count, row_numbers = find_deleting_row(board)
                if count > 0:
                    delete_row(screen, board, row_numbers, block_color)
                    record.update(count) 
                screen.fill((0, 0, 0))
                draw_board(screen, board, block_color)
                block.draw(screen, block_color)
                record.show(screen)
                pygame.display.update()

                block = Block(next_block_type)
                next_block_type = random.randint(2, 8)
                if not block.moveable(board, [0, 0]):
                    game_over = True
        record.show(screen)
        pygame.display.update()

        # 時間経過による落下速度調整
        elapsed_time: int = pygame.time.get_ticks() - start_time
        global FALL_SPEED  # グローバル変数を変更するため
        if elapsed_time > 30000 and FALL_SPEED > 5:  # 30秒経過で少し速く
            FALL_SPEED -= 1
        elif elapsed_time > 60000 and FALL_SPEED > 1:  # 60秒経過でさらに速く
            FALL_SPEED -= 1
        elif elapsed_time > 90000 and FALL_SPEED > 1:  # 90秒経過でさらに速く
            FALL_SPEED -= 1

        pygame.display.update()

        for event in pygame.event.get():
            # 閉じるボタン
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # Escapeキーが押された場合
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # ブロックの回転
                if event.key == K_a or event.key == K_SPACE:  # 反時計回り
                    block.rotate(board, 1)
                if event.key == K_s:  # 時計回り
                    block.rotate(board, 0)

    # Game Over時の処理 (現状は何もしない)
    while game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
if __name__ == "__main__":
    main()