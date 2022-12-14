import multiprocessing
import threading
import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue

disk_color = ['white', 'red', 'orange']
disks = list()
iteration = 0

max_value = 1000000

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level ' + str(i + 1))


def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    global iteration
    global max_value
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = -max_value
    out_list = []
    # out_list = {}
    jobs = []
    alpha = -max_value
    beta = max_value
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.add_disk(move, max_player,
                               update_display=False)  # l'IA met une valeur dans la grille , soit 1 soit 2 (dÃ©pend de son tour de jeu, pour Ãªtre en accord avec la mÃ©thode move)
        # thread = multiprocessing.Process(target=alpha_aux_func(move, updated_board, turn, ai_level, max_player, out_list))
        # jobs.append(thread)
        value = alpha_min_value(updated_board, turn+1, ai_level-1, max_player, alpha, beta)
        out_list.append(value)
        if value > best_value:
            best_value = value
            best_move = move
            if best_value >= beta:
                queue.put(best_move)
                print(iteration)
                iteration = 0
                return
        alpha = max(alpha, value)

    # for j in jobs:
    #     j.start()
    #
    # for j in jobs:
    #     j.join()
    #
    # for move in possible_moves:
    #     if out_list[move] > best_value:
    #         best_value = out_list[move]
    #         best_move = move
    queue.put(best_move)
    print(iteration)
    iteration = 0


def alpha_aux_func(move, board, turn, ai_level, max_player, out_list):
    global max_value
    value = alpha_min_value(board, turn, ai_level, max_player, -max_value, max_value)
    out_list[move] = value


def alpha_min_value(board, turn, ai_level, max_player, alpha, beta):
    global max_value
    aux = board.check_victory()
    if aux[0] and aux[1] == max_player:
        return max_value
    elif aux[0]:
        return -max_value
    elif ai_level == 0:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = max_value
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.add_disk(move, turn % 2 + 1, update_display=False)
        max_val = alpha_max_value(updated_board, turn + 1, ai_level - 1, max_player, alpha, beta)
        value = min(value, max_val)
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


def alpha_max_value(board, turn, ai_level, max_player, alpha, beta):
    global max_value
    aux = board.check_victory()
    if aux[0] and aux[1] == max_player:
        return max_value
    elif aux[0]:
        return -max_value
    elif ai_level == 0:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = -max_value
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.add_disk(move, turn % 2 + 1, update_display=False)
        min_val = alpha_min_value(updated_board, turn + 1, ai_level - 1, max_player, alpha, beta)
        value = max(value, min_val)
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value


def eval_list(l, player):
    retour = 0
    if l.count(0) == 1:
        if l.count(player) == 3:
            retour -= 1
        elif l.count(player) == 0:
            retour += 1
    # elif l.count(0) == 2:
    #     if l.count(player) == 2:
    #         retour -= 1
    #     elif l.count(player) == 0:
    #         retour += 1
    return retour


class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0]])

    def __eval_lignes__(self, player):
        retour = 0
        for colonne in range(4):
            for ligne in range(6):
                tuple = [self.grid[colonne+i][ligne] for i in range(4)]
                retour += eval_list(tuple, player)
        return retour

    def __eval_colonnes__(self, player):
        retour = 0
        for colonne in range(7):
            for ligne in range(3):
                tuple = [self.grid[colonne][ligne+i] for i in range(4)]
                retour += eval_list(tuple, player)
        return retour

    def eval(self, player):
        return self.__eval_lignes__(player)+self.__eval_colonnes__(player)

    def copy(self):
        global iteration
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        iteration += 1
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves
        # return [i for i in range(7) if (self.grid[i][5] == 0)]

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        # j = self.grid[column].index(0)
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal alignment check
        for line in range(6):
            for horizontal_shift in range(4):
                if self.grid[horizontal_shift][line] == self.grid[horizontal_shift + 1][line] == \
                        self.grid[horizontal_shift + 2][line] == self.grid[horizontal_shift + 3][line] != 0:
                    return [True, self.grid[horizontal_shift][line]]
        # Vertical alignment check
        for column in range(7):
            for vertical_shift in range(3):
                if self.grid[column][vertical_shift] == self.grid[column][vertical_shift + 1] == \
                        self.grid[column][vertical_shift + 2] == self.grid[column][vertical_shift + 3] != 0:
                    return [True, self.grid[column][vertical_shift]]
        # Diagonal alignment check
        for horizontal_shift in range(4):
            for vertical_shift in range(3):
                if self.grid[horizontal_shift][vertical_shift] == self.grid[horizontal_shift + 1][vertical_shift + 1] == \
                        self.grid[horizontal_shift + 2][vertical_shift + 2] == self.grid[horizontal_shift + 3][
                    vertical_shift + 3] != 0:
                    return [True, self.grid[horizontal_shift][vertical_shift]]
                elif self.grid[horizontal_shift][5 - vertical_shift] == self.grid[horizontal_shift + 1][
                    4 - vertical_shift] == \
                        self.grid[horizontal_shift + 2][3 - vertical_shift] == self.grid[horizontal_shift + 3][
                    2 - vertical_shift] != 0:
                    return [True, self.grid[horizontal_shift][5 - vertical_shift]]
        return [False, None]


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision,
               args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory()[0]:
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 700
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height,
                                            (i + 1) * row_width - row_margin,
                                            (j + 1) * row_height - row_margin, fill='white'))

canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(6)
combobox_player2['values'] = player_type
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()







