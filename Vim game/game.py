import pyxel
import os
import pygame
import datetime
import csv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
EMACS_INTERVAL = 20
VIM_INTERVAL = 160
START_SCENE = "start"
PLAY_SCENE = "play"
STOP_SCENE = "stop"
GAME_OVER_SCENE = "game over"
SCORE_RECORD_SCENE = "score record"
GAME_OVER_DISPLAY_TIME = 150
LIFE = 3
SCORE_RECORD_DISPLAY = 3
ORDINAL_NUMBER = {1:"st", 2:"nd", 3:"rd", 4:"th", 5:"th", 6:"th", 7:"th", 8:"th", 9:"th", 10:"th"}

class MusicPlayer:
    def __init__(self,filename):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(1)

    def loop(self,time=0.0):
        pos = pygame.mixer.music.get_pos()
        if int(pos) == -1:
            pygame.mixer.music.play(-1,time)

class Vim:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, pyxel.COLOR_BLACK)

class Emacs:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 32, 16, 16, pyxel.COLOR_BLACK)

#過去のスコアデータを読み込んでスコアで降べきにソート
def record_ordering():
    filepath = os.path.join(BASE_DIR,"score.csv")
    with open(filepath, "r", encoding="shift_jis") as file:
        lines = csv.reader(file)
        int_lines =[]
        for line in lines:
            int_line = int(line[0])
            int_lines.append([int_line, line[1], line[2], line[3], line[4], line[5], line[6]])
        sorted_reader = sorted(int_lines, key=lambda x:x[0], reverse=True)
        score_list = []
        for i in range(SCORE_RECORD_DISPLAY):
            score_list.append(sorted_reader[i])
        return score_list

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Vim Game(テスト版)")
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        self.current_scene = START_SCENE
        self.music_player = MusicPlayer("poppippo.mp3")
        pyxel.run(self.update, self.draw)

    def reset_play_scene(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT * 4 // 5
        self.emacses = []
        self.vims = []
        self.is_collision = False
        self.score = 0
        self.life = LIFE
        self.emacs_interval = EMACS_INTERVAL
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME

    def update_start_scene(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.reset_play_scene()
            self.current_scene = PLAY_SCENE
        elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (SCREEN_WIDTH // 2  - 25 <= pyxel.mouse_x <= SCREEN_WIDTH // 2 + 25 and
                SCREEN_HEIGHT // 2 + 33 <= pyxel.mouse_y <= SCREEN_HEIGHT // 2 + 40):
                self.current_scene = SCORE_RECORD_SCENE
                self.score_list = record_ordering()

    def update_play_scene(self):
        #ゲームオーバーのとき
        if self.is_collision:
            self.current_scene = GAME_OVER_SCENE
            self.this_time = datetime.datetime.now()
            self.record = [self.score, self.this_time.year, self.this_time.month,
                           self.this_time.day, self.this_time.hour, self.this_time.minute, self.this_time.second]
            filepath = os.path.join(BASE_DIR,"score.csv")
            with open(filepath, "a", encoding="shift_jis") as file:
                self.writer = csv.writer(file, lineterminator="\n")
                self.writer.writerow(self.record)
            return

        # 一時停止モード
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = STOP_SCENE

        self.score += 1

        # Emacsの出現間隔の調整
        if pyxel.frame_count % 300 == 0:
            if self.emacs_interval > 1:
                self.emacs_interval -= 1

        # 人の移動
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < SCREEN_WIDTH - 12:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > -4:
            self.player_x -= 1

        # Vimの追加
        if pyxel.frame_count % VIM_INTERVAL == 0:
            self.vims.append(Vim(pyxel.rndi(0, SCREEN_WIDTH - 8), 0))

        # Emacsの追加
        if pyxel.frame_count % self.emacs_interval == 0:
            self.emacses.append(Emacs(pyxel.rndi(0, SCREEN_WIDTH - 8), 0))

        # vimの落下
        for vim in self.vims.copy():
            vim.update()

            # 衝突
            if (self.player_x - 8 <= vim.x <= self.player_x + 8 and
                    self.player_y - 8 <= vim.y <= self.player_y + 8):
                self.vims.remove(vim)
                if self.life < 5:
                    self.life += 1

            # 画面外のvimを削除
            if vim.y >= SCREEN_HEIGHT:
                self.vims.remove(vim)

        # Emacsの落下
        for emacs in self.emacses.copy():
            emacs.update()

            # 衝突
            if (self.player_x - 8 <= emacs.x <= self.player_x + 8 and
                    self.player_y - 8 <= emacs.y <= self.player_y + 8):
                self.life -= 1
                self.emacses.remove(emacs)
                if self.life == 0:
                    self.is_collision = True

            # 画面外のEmacsを削除
            if emacs.y >= SCREEN_HEIGHT:
                self.emacses.remove(emacs)

    def update_stop_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if(SCREEN_WIDTH // 2 - 35 <= pyxel.mouse_x <= SCREEN_WIDTH //2 + 35 and
                SCREEN_HEIGHT // 2 - 17 <= pyxel.mouse_y <= SCREEN_HEIGHT // 2 - 10):
                self.current_scene = START_SCENE
            elif(SCREEN_WIDTH // 2 - 20 <= pyxel.mouse_x <= SCREEN_WIDTH //2 + 20 and
                SCREEN_HEIGHT // 2 + 3 <= pyxel.mouse_y <= SCREEN_HEIGHT // 2 + 10):
                self.current_scene = PLAY_SCENE
            elif(SCREEN_WIDTH // 2 - 30 <= pyxel.mouse_x <= SCREEN_WIDTH //2 + 30 and
                SCREEN_HEIGHT // 2 + 23 <= pyxel.mouse_y <= SCREEN_HEIGHT // 2 + 30):
                self.reset_play_scene()
                self.current_scene = PLAY_SCENE

    def update_game_over_scene(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = START_SCENE

    def update_score_record_scene(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = START_SCENE

    def update(self):
        self.music_player.loop(time=0.0)

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()
        elif self.current_scene == GAME_OVER_SCENE:
            self.update_game_over_scene()
        elif self.current_scene == SCORE_RECORD_SCENE:
            self.update_score_record_scene()
        elif self.current_scene == STOP_SCENE:
            self.update_stop_scene()

    def draw_start_scene(self):
        pyxel.blt(0, 0, 0, 32, 0, 160,120)
        pyxel.text(SCREEN_WIDTH // 10, SCREEN_HEIGHT // 10, "Press Space to Start", pyxel.COLOR_CYAN)
        pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 + 35, "Score Record", pyxel.COLOR_CYAN)

    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        # vim
        for vim in self.vims:
            vim.draw()
        # emacs
        for emacs in self.emacses:
            emacs.draw()
        # 人
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)

        # スコア
        pyxel.text(SCREEN_WIDTH // 15, SCREEN_HEIGHT // 15, f"SCORE:{self.score}", pyxel.COLOR_RED)

        # ライフ
        pyxel.text(SCREEN_WIDTH  * 7 // 10,SCREEN_HEIGHT // 15, f"LIFE:{self.life}/5", pyxel.COLOR_RED)

    def draw_stop_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        # vim
        for vim in self.vims:
            vim.draw()
        # emacs
        for emacs in self.emacses:
            emacs.draw()
        # 人
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)

        # スコア
        pyxel.text(SCREEN_WIDTH // 15, SCREEN_HEIGHT // 15, f"SCORE:{self.score}", pyxel.COLOR_RED)

        # ライフ
        pyxel.text(SCREEN_WIDTH * 7 // 10, SCREEN_HEIGHT // 15, f"LIFE:{self.life}/5", pyxel.COLOR_RED)

        pyxel.text(SCREEN_WIDTH // 2 - 33, SCREEN_HEIGHT // 2 - 15, "Go to Start Screen", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 2 - 21, SCREEN_HEIGHT // 2 + 5, "Back to Game", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 2 - 29, SCREEN_HEIGHT // 2 + 25, "Start Over Again", pyxel.COLOR_YELLOW)

    def draw_game_over_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        # vim
        for vim in self.vims:
            vim.draw()
        # emacs
        for emacs in self.emacses:
            emacs.draw()
        # 人
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK)

        # スコア
        pyxel.text(SCREEN_WIDTH // 15, SCREEN_HEIGHT // 15, f"SCORE:{self.score}", pyxel.COLOR_RED)

        # ライフ
        pyxel.text(SCREEN_WIDTH  * 7 // 10,SCREEN_HEIGHT // 15, f"LIFE:{self.life}/5", pyxel.COLOR_RED)

        pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20, "GAME OVER", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2, f"Your Score:{self.score}", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 20, "Press Space to return", pyxel.COLOR_YELLOW)

    def draw_score_record_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        for i in range(SCORE_RECORD_DISPLAY):
            pyxel.text(SCREEN_WIDTH // 10, SCREEN_HEIGHT * (i * 2 + 1) // 10, f"{i+1}{ORDINAL_NUMBER[i+1]}"
                f"{self.score_list[i][0]:>8}{self.score_list[i][1]:>8}-{self.score_list[i][2]}-{self.score_list[i][3]}"
                f"{self.score_list[i][4]:>4}:{self.score_list[i][5]}:{self.score_list[i][6]}", pyxel.COLOR_WHITE)
        pyxel.text(SCREEN_WIDTH * 4 // 10, SCREEN_HEIGHT * 9 // 10, "Press Space to return", pyxel.COLOR_WHITE)

    def draw(self):
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()
        elif self.current_scene == GAME_OVER_SCENE:
            self.draw_game_over_scene()
        elif self.current_scene == SCORE_RECORD_SCENE:
            self.draw_score_record_scene()
        elif self.current_scene == STOP_SCENE:
            self.draw_stop_scene()

App()