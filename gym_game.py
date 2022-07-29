import numpy as np
import random
import sys
#import pygame
import tf_agents
import time
import keyboard
import copy
class Game():
    def __init__(self, discount = 1.):
        super().__init__()
        self.discount = discount
        #init
        self.width = 800
        self.square_size = self.width / 4
        #self.screen = pygame.display.set_mode((self.width, self.width))
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.background = (187, 173, 160)
        self.square = (205, 193, 180)
        self.DARK = (119, 110, 101)
        self.is_ended = False
        #self.batch_size = 1
        self.numbers = [
        (238, 228, 218), # 2
        (238, 225, 201), # 4
        (243, 179, 122), # 8
        (245, 152, 100), # 16
        (247, 124, 95), # 32
        (247, 95, 59), # 64
        (237, 208, 115), # 128
        (237, 204, 99), #256
        (237, 201, 80), #512
        (238, 200, 71), #1024
        (237, 194, 46), #2048
                ]
        self.num_to_index = {2: 0, 4: 1, 8:2, 16: 3, 32: 4, 64: 5, 128:6, 256: 7, 512: 8, 1024: 9, 2048: 10}
    # def step(self, action):
    #     return _step(action)
    # def reset(self):
    #     return _reset()
    def action_spec(self):
        return self._action_spec
    def observation_spec(self):
        return self._observation_spec
    def get_starting_indices(self):
        nums = list(range(16))
        num_1 = random.choice(nums)
        final_1 = [num_1 // 4, num_1 % 4]
        nums.pop(num_1)
        num_2 = random.choice(nums)
        final_2 = [num_2 // 4, num_2 % 4]
        return np.array([final_1, final_2])
    def get_num(self, prob = 0.9):
        num = 2 if np.random.uniform() < 0.9 else 4
        return num
    def reset(self):
        self.is_ended = False
        self.board = np.zeros((4,4),dtype=np.int32)
        #get starting indices
        indices = self.get_starting_indices()
        for index in indices:
            row = index[0]
            col = index[1]
            self.board[row][col] = self.get_num()
        return copy.deepcopy(self.board)
    def count_nonzero(self):
        count = 0
        for row in range(3):
            for col in range(3):
                if(self.board[row][col] != 0):
                    count += 1
        return count
    def step(self, action):
        #print(self.board)
        reward = 0
        past_size = self.count_nonzero()
        if(not(self.is_ended)):
            self.make_move(action)
            current_size = self.count_nonzero()
            reward += (past_size - current_size) * 10
            return copy.deepcopy(self.board), reward, self.is_ended, ""
        else:
            if self.result() == 1: reward += 1000000
            #reward -= 100 if self.result() == -1
            #print(self.result())
            #print("terminating")
            return copy.deepcopy(self.board), reward, self.is_ended, ""


    def draw_board(self, square_size):
        self.screen.fill(self.background)
        for row in range(4):
            for col in range(4):
                num = self.board[row][col]
                if(num == 0):
                    color = self.square
                else:
                    color = self.numbers[self.num_to_index[num]]
                rect = pygame.Rect(square_size * col + 10, square_size * row + 10, square_size - 20, square_size - 20)
                pygame.draw.rect(self.screen, color, rect)
                if(num != 0):
                    self.display_num(num, (square_size * col + (square_size / 4)), (square_size * row + (square_size / 4)))
    def display_num(self, num, x, y):
        font = pygame.font.SysFont('helvetica', 100)
        text = font.render(str(num), True, self.DARK)
        self.screen.blit(text, (x, y))
    def make_move(self, direction):
        drow, dcol = 0, 0
        if direction == 0: drow = 1
        if direction == 1: drow = -1
        if direction == 2: dcol = 1
        if direction == 3: dcol = -1
        if(drow == -1 or dcol == -1):
            for row in range(4):
                for col in range(4):
                    if self.board[row][col] != 0:
                        self.move_square(row, col, (drow, dcol))
        else:
            for row in range(3, -1, -1):
                for col in range(3, -1, -1):
                    if self.board[row][col] != 0:
                        self.move_square(row, col, (drow, dcol))
        if(self.result() == 0):
            self.add_random()
        else:
            self.is_ended = True
    def inBounds(self, row, col):
        return row >= 0 and row <= 3 and col >= 0 and col <= 3
    def move_square(self, row, col, direction):
        drow, dcol = direction
        num = self.board[row][col]
        for i in range(1,5):
            newrow, newcol = row + drow * i, col + dcol * i
            if(self.inBounds(newrow, newcol)):
                newnum = self.board[newrow][newcol]
                if(newnum != 0):
                    if(newnum == num):
                        self.board[row][col] = 0
                        self.board[newrow][newcol] = num * 2
                        return
                    else:
                        self.board[row][col] = 0
                        self.board[newrow - drow][newcol - dcol] = num
                        return
            else:
                self.board[row][col] = 0
                self.board[newrow - drow][newcol - dcol] = num
                return
    def add_random(self):
        num = self.get_num()
        empty_squares = []
        for row in range(4):
            for col in range(4):
                if(self.board[row][col] == 0):
                    empty_squares.append((row, col))
        chosen_square = random.choice(empty_squares)
        self.board[chosen_square[0]][chosen_square[1]] = num
    def render(self, mode):
        if(mode == "human"):
            self.draw_board(self.square_size)
            pygame.display.flip()
        else:
            return self.board
    def stop_render(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()
    def result(self):
        if 2048 in self.board:
            return 1
        elif 0 not in self.board:
            return -1
        else:
            return 0
if __name__ == "__main__":
    #pygame.init()
    game = Game()
    game._reset()
    print(game.render(""))
    keys = ["s","w","d","a"]
    timer = time.time()
    while True:
        # for index, key in enumerate(keys):
        #     if keyboard.is_pressed(key):
        #         action = np.zeros(4, dtype = np.int32)
        #         action[index] = 1
        #         game.make_move(action)
        # if(time.time() - timer > 1):
        #     game.make_move([0,0,0,1])
        #     timer = time.time()
        #print(game.board)
        #PYGAME STUFF
        # events = pygame.event.get()
        # keyRegistered = False
        # for event in events:
        #     if(not(keyRegistered)):
        #         if event.type == pygame.KEYDOWN:
        #             key = event.key
        #             if(key == pygame.K_ESCAPE):
        #                 game.stop_render()
        #             pygame_keys = [pygame.K_s, pygame.K_w, pygame.K_d, pygame.K_a]
        #             for index, pygame_key in enumerate(pygame_keys):
        #                 if(key == pygame_key):
        #                     action = np.zeros(4, dtype = np.int32)
        #                     action[index] = 1
        #                     game.make_move(action)
        #                     keyRegistered = True
        #                     print(game.render("e"))
        #                     break
        if(keyboard.is_pressed('z')):
            sys.exit()
        if(time.time() - timer > 0.2):
            for index, key in enumerate(keys):
                if keyboard.is_pressed(key):
                    game._step(index)
                    print(game.render(""))
                    timer = time.time()
                    break

        #game.render("human")
