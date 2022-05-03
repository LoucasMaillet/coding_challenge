#!/usr/bin/env python3.10
#coding: utf-8


from tkinter import Event, Frame, Canvas, Tk
from random import sample
from collections import deque


class Cell(int):

    def __init__(self, _, rgb) -> None:
        self.hex = "#%02x%02x%02x" % rgb
        self.rgb = "%02d;%02d;%02d" % rgb

    def __new__(cls, v, *_) -> None:
        return super(Cell, cls).__new__(cls, v)


# Next element base of each cell
NEXTS = (
    (1, -1), (1, 0), (1, 1),
    (0, -1), (0, 1),
    (-1, -1), (-1, 0), (-1, 1)
)
# Delay between each update (in ms)
UPD_TIME = 1
# Percent of initialised uninfected cells
DENSITY = .5
# Different types of cells
CL_BLANK = Cell(0x0, (255, 255, 240))
CL_UNINFECTED = Cell(0x1, (50, 205, 50))
CL_SPREAD = Cell(0x2, (255, 5, 5))
CL_INFECTED = Cell(0x3, (191, 191, 191))


class AutoMatrix(list):

    def __init__(self, rows: int, cols: int) -> None:
        list.__init__(self, ([CL_BLANK for _ in range(cols)] for _ in range(rows)))
        self.n_spread: int = 0
        self.n_infected: int = 0
        self.n_uninfected: int = int(DENSITY*cols*rows)
        self._rows: int = rows
        self._cols: int = cols
        self._r_rows: range = range(rows)
        self._r_cols: range = range(cols)
        self._spreader: list = deque(maxlen=int(self.n_uninfected * .5)) # A top size of the potential spreader (sure overestimed)
        for i, j in sample([(i, j) for j in range(self._cols) for i in range(self._rows)], self.n_uninfected):
            self[i][j] = CL_UNINFECTED

    def __repr__(self) -> str:
        repr_ = ""
        for i in range(self._rows-1):
            repr_ += '['
            for j in range(self._cols-1):
                repr_ += f"{self[i][j]}, "
            repr_ += f"{self[i][-1]}],\n"
        repr_ += '['
        for j in self._r_cols:
            repr_ += f"{self[-1][j]}, "
        repr_ += f"{self[-1][j]}]"
        return repr_

    def spread(self, i: int, j: int) -> bool:
        if i < 0:
            i += self._rows
        if j < 0:
            j += self._cols
        self.n_spread += 1
        self.n_uninfected -= 1
        self._spreader.appendleft((i, j))

    def update(self) -> None:
        self.n_infected += self.n_spread
        i = 0
        for _ in range(self.n_spread):
            coord = self._spreader.popleft()
            self[coord[0]][coord[1]] = CL_INFECTED
            for coord_next in NEXTS:
                coord_ = (coord[0] + coord_next[0], coord[1] + coord_next[1])
                if coord_[0] < 0 or coord_[0] == self._rows or \
                        coord_[1] < 0 or coord_[1] == self._cols:
                    continue
                if self[coord_[0]][coord_[1]] == CL_UNINFECTED:
                    self._spreader.append(coord_)
                    i += 1

        self.n_spread = 0
        for _ in range(i):
            coord = self._spreader.popleft()
            if self[coord[0]][coord[1]] == CL_UNINFECTED:
                self[coord[0]][coord[1]] = CL_SPREAD
                self._spreader.append(coord)
                self.n_spread += 1
        self.n_uninfected -= self.n_spread


class AutoMatrixCanvas(AutoMatrix, Canvas):

    def __init__(self, frame: Frame, width: int, height: int, rows: int, cols: int, upd_time: int = UPD_TIME, **kwargs) -> None:
        AutoMatrix.__init__(self, rows, cols)
        Canvas.__init__(self, frame, width=width, height=height, **kwargs)
        self.c_height = height / rows
        self.c_width = width / cols
        self.upd_time = upd_time

        def __listener_button_1__(ev: Event):
            i, j = int(ev.y // self.c_height - 1), int(ev.x // self.c_width - 1)
            self.spread(i, j)
            x, y = j * self.c_width, i * self.c_height
            self.create_rectangle(x, y, x + self.c_width, y + self.c_height, fill=self[i][j].hex, width=0)

        self.bind("<Button-1>", __listener_button_1__)

        def __update_loop__():
            self.update()
            self._id = self.after(self.upd_time, __update_loop__)

        self._id = self.after(self.upd_time, __update_loop__)

        self.draw()
        self.pack()

    def draw(self) -> None:
        for i in self._r_rows:
            for j in self._r_cols:
                x, y = j * self.c_width, i * self.c_height
                self.create_rectangle(x, y, x + self.c_width, y + self.c_height, fill=self[i][j].hex, width=0)

    def update(self) -> None:
        self.n_infected += self.n_spread
        i = 0
        for _ in range(self.n_spread):
            coord = self._spreader.popleft()
            self[coord[0]][coord[1]] = CL_INFECTED
            x, y = coord[1] * self.c_width, coord[0] * self.c_height
            self.create_rectangle(x, y, x + self.c_width, y + self.c_height, fill=self[coord[0]][coord[1]].hex, width=0)
            for coord_next in NEXTS:
                coord_ = (coord[0] + coord_next[0], coord[1] + coord_next[1])
                if coord_[0] < 0 or coord_[0] == self._rows or \
                        coord_[1] < 0 or coord_[1] == self._cols:
                    continue
                if self[coord_[0]][coord_[1]] == CL_UNINFECTED:
                    self._spreader.append(coord_)
                    i += 1

        self.n_spread = 0
        for _ in range(i):
            coord = self._spreader.popleft()
            if self[coord[0]][coord[1]] == CL_UNINFECTED:
                self[coord[0]][coord[1]] = CL_SPREAD
                x, y = coord[1] * self.c_width, coord[0] * self.c_height
                self.create_rectangle(x, y, x + self.c_width, y + self.c_height, fill=self[coord[0]][coord[1]].hex, width=0)
                self._spreader.append(coord)
                self.n_spread += 1
        self.n_uninfected -= self.n_spread


class AutoMatrixShell(AutoMatrix):

    def __init__(self, rows: int, cols: int) -> None:
        AutoMatrix.__init__(self, rows, cols)

    def draw(self) -> None:
        print("\033c", end='')
        for row in self:
            for cell in row:
                print(f"\033[48;2;{cell.rgb}m   \033[0m", end='')
            print()

    def update(self) -> None:
        self.n_infected += self.n_spread
        i = 0
        for _ in range(self.n_spread):
            coord = self._spreader.popleft()
            self[coord[0]][coord[1]] = CL_INFECTED
            print(f"\033[?25l\033[{coord[0]};{coord[1]*3-2}f\033[48;2;{self[coord[0]][coord[1]].rgb}m   \033[0m")
            for coord_next in NEXTS:
                coord_ = (coord[0] + coord_next[0], coord[1] + coord_next[1])
                if coord_[0] < 0 or coord_[0] == self._rows or \
                        coord_[1] < 0 or coord_[1] == self._cols:
                    continue
                if self[coord_[0]][coord_[1]] == CL_UNINFECTED:
                    self._spreader.append(coord_)
                    i += 1

        self.n_spread = 0
        for _ in range(i):
            coord = self._spreader.popleft()
            if self[coord[0]][coord[1]] == CL_UNINFECTED:
                self[coord[0]][coord[1]] = CL_SPREAD
                print(f"\033[?25l\033[{coord[0]};{coord[1]*3-2}f\033[48;2;{self[coord[0]][coord[1]].rgb}m   \033[0m")
                self._spreader.append(coord)
                self.n_spread += 1
        self.n_uninfected -= self.n_spread

if __name__ == "__main__":

    # 252 2582 2453 358 3813 1154 3010 1304 3481 3669 2665
    # from keyboard import on_press_key, wait
    # from time import sleep
    # from os import get_terminal_size
    # from time import sleep
    # cols, rows = get_terminal_size()
    # fm = AutoMatrixShell(rows-1, cols//3)
    # fm.draw()
    # fm.spread(0, 0)
    # cursor = [0, 0]

    # def __key_event__(key):
    #     print(key)
    #     # if key == Key.up:
    #     #     if cursor[0] < fm._rows:
    #     #         cursor[0] += 1
    #     #         print("\033[s", end='')
    #     # elif key == Key.down:
    #     #     if 0 < cursor[0]:
    #     #         cursor[0] -= 1
    #     #         print("\033[s", end='')
    #     # elif key == Key.left:
    #     #     ...
    #     # elif key == Key.right:
    #     #     ...
    # on_press_key("up arrow", __key_event__)
    # UPD_TIME *= 1e-3
    # while True:
    #     fm.update()
    #     # fm.draw()
    #     sleep(UPD_TIME * 1e-1)

    gui = Tk()
    gui.title(f"Spreading Cellular Automata")
    frame = Frame()
    frame.pack()
    s = .5
    f = 50
    fm = AutoMatrixCanvas(frame,
                          1920*s,
                          1080*s,
                          9*f,
                          16*f)
    fm.mainloop()
