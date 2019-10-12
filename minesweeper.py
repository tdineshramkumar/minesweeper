from random import sample
from time import time

INIT = 'INIT'
PROGRESS = 'PROGRESS'
WINNER = 'WINNER'
GAME_OVER = 'GAME_OVER'


class _Square:
    def __init__(self):
        # Initial configurations.
        self.mine = False
        self.neighbouring_mines = 0
        # Base on user input
        self.uncovered = False
        self.marked = False
        self.uncertain = False

    @property
    def neighbour_mines(self):
        return self.neighbouring_mines > 0

    def uncover(self):
        self.uncovered = True
        if not self.mine:
            self.marked = False
            self.uncertain = False


class MineSweeper:
    def __init__(self, field_width, field_height, field_mines):
        field_mines = min(field_width * field_height - 9, max(0, field_mines))
        self.field_width = field_width
        self.field_height = field_height
        self.field_mines = field_mines
        self.field_size = field_width, field_height
        self.__reset__()

    def __reset__(self):
        self.field = {(x, y): _Square() for x in range(self.field_width) for y in range(self.field_height)}
        self.game_state = INIT
        self.uncovered = 0
        self.total_non_mines = self.field_width * self.field_height - self.field_mines
        self.total_time = 0

    def reset(self):
        self.__reset__()

    def _neighbours(self, field_pos):
        x, y = field_pos
        potential_neighbours = [(x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1),
                                (x, y + 1)]
        return list(filter(
            lambda pos: 0 <= pos[0] < self.field_width and 0 <= pos[1] < self.field_height, potential_neighbours))

    def __init_game__(self, init_position):
        potential_mine_positions = [(x, y) for x in range(self.field_width) for y in range(self.field_height)
                                    if (x, y) != init_position and (x, y) not in self._neighbours(init_position)]
        print(len(potential_mine_positions), len(self.field))
        print(init_position, self._neighbours(init_position))
        print([pos for pos in [(x, y) for x in range(self.field_width) for y in range(self.field_height)] if pos not in potential_mine_positions])
        mine_positions = sample(potential_mine_positions, self.field_mines)
        for position in mine_positions:
            self.field[position].mine = True
            for neighbour in self._neighbours(position):
                self.field[neighbour].neighbouring_mines += 1
        self.start_time = time()
        self.game_state = PROGRESS

    def time(self):
        if self.game_state == INIT:
            return 0
        elif self.game_state == PROGRESS:
            # Time since game started.
            return int(time() - self.start_time)
        else:
            return int(self.total_time)

    def pending_mines(self):
        return self.field_mines - sum(map(lambda pos: self.field[pos].marked, self.field))

    def uncover(self, position):
        if self.game_state == INIT:
            print('INIT:', position)
            self.__init_game__(init_position=position)
            print(self.field)
            # After initialization it goes into progress.

        if self.game_state == PROGRESS:
            if not self.field[position].uncovered and \
                    not self.field[position].marked and \
                    not self.field[position].uncertain:

                self.field[position].uncover()
                if self.field[position].mine:
                    self.game_state = GAME_OVER
                    self.total_time = time() - self.start_time
                    return

                self.uncovered += 1
                if self.uncovered >= self.total_non_mines:
                    self.game_state = WINNER
                    self.total_time = time() - self.start_time
                    return

                if not self.field[position].neighbour_mines:
                    for neighbour in self._neighbours(position):
                        # Un-mark the neighbour.
                        self.field[position].marked = False
                        self.field[position].uncertain = False
                        self.uncover(neighbour)

    def toggle(self, position):
        if self.game_state == PROGRESS:
            if not self.field[position].uncovered:
                if self.field[position].marked:
                    self.field[position].marked = False
                    self.field[position].uncertain = True
                elif self.field[position].uncertain:
                    self.field[position].marked = False
                    self.field[position].uncertain = False
                else:
                    self.field[position].marked = True
                    self.field[position].uncertain = False

    def uncover_neighbours(self, position):
        if self.game_state == PROGRESS:
            if self.field[position].uncovered and self.field[position].neighbour_mines:
                neighbours = self._neighbours(position)
                marked_neighbour_mines = sum(map(lambda pos: self.field[pos].marked, neighbours))
                if any(map(lambda pos: self.field[pos].uncertain, neighbours)):
                    # If any of the neighbours are uncertain then return.
                    return

                if marked_neighbour_mines == self.field[position].neighbouring_mines:
                    # If number of marked mines matches the actual neighbouring mines
                    unmarked_positions = [pos for pos in self._neighbours(position) if not self.field[pos].marked]
                    for neighbour in unmarked_positions:
                        self.uncover(neighbour)

    def game_over(self):
        return self.game_state == GAME_OVER or self.game_state == WINNER


