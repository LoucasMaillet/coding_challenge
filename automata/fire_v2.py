#!/usr/bin/env python3.10
#coding: utf-8


from math import sqrt
from random import random
from tkinter import Frame, Canvas, Tk, Event
from perlin_noise import PerlinNoise


class Cell(int):

    def __init__(self, _, rgb) -> None:
        self.hex_color = "#%02x%02x%02x" % rgb
        self.rgb_color = "%02d;%02d;%02d" % rgb

    def __new__(cls, v, *_) -> None:
        return super(Cell, cls).__new__(cls, v)


class CellGradient(int):

    def __init__(self, _, rgb_from, rgb_to) -> None:
        self.rgb_from = rgb_from
        self.rgb_to = rgb_to

    def gradient(self, f: float):
        f_ = 1 - f
        return Cell(self, (
            int(self.rgb_from[0] * f_ + self.rgb_to[0] * f),
            int(self.rgb_from[1] * f_ + self.rgb_to[1] * f),
            int(self.rgb_from[2] * f_ + self.rgb_to[2] * f)
        ))

    def __new__(cls, v, *_) -> None:
        return super(CellGradient, cls).__new__(cls, v)


c = Cell
# Delay between each update (in seconde)
T_DELAY = 50
# Based number of octaves for PerlinNoise
OCTAVES = 5
# Risk of instant propagation
RISK_BURN = .5
RISK_INSTANT_BURN = .2
# Different types of cells
CL_WATER = CellGradient(0x0, (52, 118, 199), (24, 87, 163))
CL_SAND = Cell(0x1, (255, 246, 125))
CL_ROCK = CellGradient(0x2, (70, 74, 79), (103, 108, 115))
CL_SNOW = Cell(0x3, (213, 217, 222))
CL_TREE = CellGradient(0x4, (52, 199, 101), (34, 133, 67))
CL_FIRE = Cell(0x5, (199, 52, 52))
CL_ASH = Cell(0x6, (22, 26, 25))


class AutoCell(list):

    def __init__(self, r: int, n: int, seed: int) -> None:
        noises = (
            PerlinNoise(octaves=OCTAVES, seed=seed),
            PerlinNoise(octaves=OCTAVES*2, seed=seed),
            PerlinNoise(octaves=OCTAVES*3, seed=seed),
        )
        list.__init__(self,([sum(noise([i/n, j/n]) / (k+1)
                              for k, noise in enumerate(noises))
                          for j in range(n+2)]
                         for i in range(r+2)))
        self.c_spread = 0
        self.c_uninfected = int(.5*n*r)
        self.c_infected = 0
        self._r = r + 1
        self._n = n + 1
        self._spreader_queue = set()
        self._spreader = set()
        i = 1
        i_center = r / 2
        j_center = n / 2
        o = min(n, r)
        i = 1
        # Hummmmm spaghetti code
        while i < self._r:
            j = 1
            while j < self._n:
                self[i][j] -= (sqrt((i-i_center)**2 +
                               (j-j_center) ** 2) / o) ** 2
                if self[i][j] < 0:
                    self[i][j] %= -1
                    self[i][j] = CL_WATER.gradient(1+self[i][j])
                else:
                    self[i][j] %= 1
                    if self[i][j] < .1:
                        self[i][j] = CL_SAND
                    elif self[i][j] < .3:
                        self[i][j] = CL_TREE.gradient(1-self[i][j]*2)
                    elif self[i][j] < .35:
                        self[i][j] = CL_TREE.gradient(1-self[i][j]*2) if random() < .5\
                            else CL_ROCK.gradient(1-self[i][j])
                    elif self[i][j] < .5:
                        self[i][j] = CL_ROCK.gradient(1-self[i][j]*2)
                    else:
                        self[i][j] = CL_SNOW
                j += 1
            i += 1

    def spread(self, i: int, j: int):
        i += self._r if i < 0 else 1
        j += self._n if j < 0 else 1
        if self[i][j] == CL_TREE:
            self.c_uninfected -= 1
            self.c_infected -= 1
            self.c_spread += 1
            self._spreader.add((i, j))
            self[i][j] = CL_FIRE
            return True
        return False

    def update(self) -> bool:
        spreader = self._spreader_queue
        self._spreader_queue = set()
        for i, j in self._spreader:
            self[i][j] = CL_ASH
            self.c_spread -= 1
            for i, j in ((i-1, j-1), (i-1, j), (i-1, j+1),  # A B C
                         (i, j-1), (i, j+1),                # D _ E
                         (i+1, j-1), (i+1, j), (i+1, j+1)):  # F G H
                if self[i][j] == CL_TREE:
                    if random() < RISK_BURN:
                        spreader.add((i, j))
                    elif random() > .5:
                        self._spreader_queue.add((i, j))
        for i, j in spreader:
            self[i][j] = CL_FIRE
            self.c_uninfected -= 1
            self.c_spread += 1
        self._spreader = spreader
        return self.c_spread != 0

    def __str__(self) -> str:
        repr_ = ""
        i = 1
        while i < self._r:
            repr_ += '['
            j = 1
            while j < self._n:
                repr_ += f"{self[i][j]}, "
                j += 1
            repr_ += f"{self[i][j]}],\n"
            i += 1
        repr_ += '['
        j = 1
        while j < self._n:
            repr_ += f"{self[i][j]}, "
            j += 1
        repr_ += f"{self[i][j]}]"
        return repr_

    def draw(self) -> None:
        print("\033c", end='')
        i = 1
        while i < self._r:
            j = 1
            while j < self._n:
                print(f"\033[48;2;{self[i][j].rgb_color}m\a   \033[0m", end='')
                j += 1
            print()
            i += 1


class AutoCellCanvas(AutoCell, Canvas):

    def __init__(self, frame: Frame, width: int, height: int, r: int, n: int, seed: int, **kwargs) -> None:
        AutoCell.__init__(self, r, n, seed)
        Canvas.__init__(self, frame, width=width, height=height)
        self.c_height = height / r
        self.c_width = width / n

        def __listener_button_1__(event: Event):
            i, j = int(event.y // self.c_height), int(event.x // self.c_width)
            self.spread(i, j)

        self.bind("<Button-1>", __listener_button_1__)

        def __update_loop__():
            self.update()
            self._id = self.after(T_DELAY, __update_loop__)

        self.after(T_DELAY, __update_loop__)

    def __draw_cell__(self, i: int, j: int):
        x, y = (j-1) * self.c_width, (i-1) * self.c_height
        self.create_rectangle(x, y, x + self.c_width, y +
                              self.c_height, fill=self[i][j].hex_color, width=0)

    def update(self) -> bool:
        spreader = self._spreader_queue
        self._spreader_queue = set()
        for i, j in self._spreader:
            self[i][j] = CL_ASH
            self.c_spread -= 1
            self.__draw_cell__(i, j)
            for i, j in ((i-1, j-1), (i-1, j), (i-1, j+1),  # A B C
                         (i, j-1), (i, j+1),                # D _ E
                         (i+1, j-1), (i+1, j), (i+1, j+1)):  # F G H
                if self[i][j] == CL_TREE:
                    if random() < RISK_INSTANT_BURN:
                        spreader.add((i, j))
                    elif random() < RISK_BURN:
                        self._spreader_queue.add((i, j))
        for i, j in spreader:
            self[i][j] = CL_FIRE
            self.c_uninfected -= 1
            self.c_spread += 1
            self.__draw_cell__(i, j)
        self._spreader = spreader
        return self.c_spread != 0

    def draw(self):
        i = 1
        while i < self._r:
            j = 1
            while j < self._n:
                self.__draw_cell__(i, j)
                j += 1
            i += 1
        self.pack()


if __name__ == "__main__":

    seed = int(random()*2**64)
    # 585635 973001 482104 293417 69420 795822

    # from os import get_terminal_size
    # cols, rows = get_terminal_size()
    # fm = AutoCell(rows-1, cols//3, seed)

    gui = Tk()
    gui.title(f"- {seed} - Spreading Cellular Automata")
    frame = Frame()
    frame.pack()
    f = 10
    fm = AutoCellCanvas(frame,
                        1920/2,
                        1080/2,
                        9*f,
                        16*f,
                        seed)

    fm.draw()
    gui.mainloop()

    # while fm.update():
    #     fm.draw()
    #     sleep(T_DELAY)
    # fm.draw()
