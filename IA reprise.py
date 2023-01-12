import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue

disk_color = ['white', 'red', 'orange']
disks = list()

iteration = 0

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level ' + str(i + 1))


def my_count(l):
    retour = [0, 0, 0]
    for i in l:
        retour[i] += 1
    return retour


def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    global iteration
    global max_value
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = 0.
    out_list = []
    # out_list = {}
    jobs = []
    alpha = 0.
    beta = 1.
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
    value = alpha_min_value(board, turn, ai_level, max_player, 0, 1)
    out_list[move] = value


def alpha_min_value(board, turn, ai_level, max_player, alpha, beta):
    aux = board.check_victory()
    if aux[0] and aux[1] == max_player:
        return 1
    elif aux[0]:
        return 0
    elif ai_level == 0:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = 1
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
    aux = board.check_victory()
    if aux[0] and aux[1] == max_player:
        return 1
    elif aux[0]:
        return 0
    elif ai_level == 0:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = 0
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.add_disk(move, turn % 2 + 1, update_display=False)
        min_val = alpha_min_value(updated_board, turn + 1, ai_level - 1, max_player, alpha, beta)
        value = max(value, min_val)
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value


class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0]])

    points = [0, 0, 2, 3, 10000]
    default = 0.5

    def __eval_lignes__(self, player):
        moi = 0.
        autre = 0
        for colonne in range(4):
            for ligne in range(6):
                count_value = my_count([self.grid[colonne + i][ligne] for i in range(4)])
                if count_value[player] == 0:
                    autre += self.points[count_value[player % 2+1]]
                elif count_value[player % 2+1] == 0:
                    moi += self.points[count_value[player]]
        return moi, autre

    def __eval_colonnes__(self, player):
        moi = 0.
        autre = 0
        for colonne in range(7):
            for ligne in range(3):
                count_value = my_count([self.grid[colonne][ligne + i] for i in range(4)])
                if count_value[player] == 0:
                    autre += self.points[count_value[player % 2+1]]
                elif count_value[player % 2+1] == 0:
                    moi += self.points[count_value[player]]
        return moi, autre

    def __eval_diagonales__(self, player):
        moi = 0.
        autre = 0
        for colonne in range(4):
            for ligne in range(3):
                count_value = my_count([self.grid[colonne + i][ligne + i] for i in range(4)])
                if count_value[player] == 0:
                    autre += self.points[count_value[player % 2+1]]
                elif count_value[player % 2+1] == 0:
                    moi += self.points[count_value[player]]
                count_value = my_count([self.grid[-(colonne + i + 1)][ligne + i] for i in range(4)])
                if count_value[player] == 0:
                    autre += self.points[count_value[player % 2+1]]
                elif count_value[player % 2+1] == 0:
                    moi += self.points[count_value[player]]
        return moi, autre

    def eval(self, player):
        moi, autre = self.__eval_lignes__(player)
        if moi >= self.points[-1]:
            return 1
        if autre >= self.points[-1]:
            return 0
        moi_2, autre_2 = self.__eval_colonnes__(player)
        if moi_2 >= self.points[-1]:
            return 1
        if autre_2 >= self.points[-1]:
            return 0
        moi_3, autre_3 = self.__eval_diagonales__(player)
        if moi_3 >= self.points[-1]:
            return 1
        if autre_3 >= self.points[-1]:
            return 0
        moi += moi_2 + moi_3
        autre += autre_2 + autre_3
        if moi + autre == 0:
            return self.default
        return moi / (moi + autre**3)

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

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def __check_lignes__(self):
        for colonne in range(4):
            for ligne in range(6):
                count_value = my_count([self.grid[colonne + i][ligne] for i in range(4)])
                if count_value[1] == 4 or count_value[2] == 4:
                    return [True, self.grid[colonne ][ligne]]
        return [False, None]

    def __check_colonnes__(self):
        for colonne in range(7):
            for ligne in range(3):
                count_value = my_count([self.grid[colonne][ligne + i] for i in range(4)])
                if count_value[1] == 4 or count_value[2] == 4:
                    return [True, self.grid[colonne][ligne]]
        return [False, None]

    def __check_diagonales__(self):
        for colonne in range(4):
            for ligne in range(3):
                count_value = my_count([self.grid[colonne + i][ligne + i] for i in range(4)])
                if count_value[1] == 4 or count_value[2] == 4:
                    return [True, self.grid[colonne][ligne]]

                count_value = my_count([self.grid[-(colonne + i + 1)][ligne + i] for i in range(4)])
                if count_value[1] == 4 or count_value[2] == 4:
                    return [True, self.grid[colonne][ligne]]
        return [False, None]

    def check_victory(self):
        l = self.__check_lignes__()
        if l[0]:
            return l
        c = self.__check_colonnes__()
        if c[0]:
            return c
        return  self.__check_diagonales__()


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
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(4)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
