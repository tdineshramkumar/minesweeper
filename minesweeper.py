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
        self.uncertain = False
        if not self.mine:
            self.marked = False

    def __repr__(self):
        # Just for debugging.
        return f'SQUARE{{mine: {self.mine}, neighbours: {self.neighbouring_mines}, uncovered: {self.uncovered}, ' \
               f'marked: {self.marked}, uncertain: {self.uncertain} }}'


class MineSweeper:
    def __init__(self, field_width, field_height, field_mines):
        field_mines = min(field_width * field_height - 9, max(0, field_mines))
        self.field_width = field_width
        self.field_height = field_height
        self.field_mines = field_mines
        self.field_size = field_width, field_height
        self.total_non_mines = self.field_width * self.field_height - self.field_mines
        self.__reset__()

    def __reset__(self):
        # This methods constructs all fields which are mutated on operation.
        self.field = {(x, y): _Square() for x in range(self.field_width) for y in range(self.field_height)}
        self.uncovered = 0
        self.game_duration = 0
        self.__update_state__(INIT)

    def reset(self):
        self.__reset__()

    def __getitem__(self, position):
        # Just a utility to easy getting squares from the field
        return self.field[position]

    def __iter__(self):
        return iter(self.field.keys())

    def __bool__(self):
        # So that direct condition can be used to determine, if game in progress or not
        return not self.game_over()

    def _in_field(self, position):
        # checks if the given position lies within the field
        return 0 <= position[0] < self.field_width and 0 <= position[1] < self.field_height

    def neighbours(self, field_pos):
        # Obtains the neighbouring positions of the given position
        x, y = field_pos
        potential_neighbours = [(x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                                (x, y - 1), (x, y + 1)]
        return list(filter(self._in_field, potential_neighbours))

    def __update_state__(self, state):
        self.game_state = state

    def __init_game__(self, init_position):
        # This method is called when user selects the first position on the field,
        # it ensures that all the neighbours of selected position are mine free and places the remaining mines
        # accordingly. Updates the neighbouring_mines of squares.
        # Changes the state to PROGRESS and starts the timer.
        potential_mine_positions = [(x, y) for x in range(self.field_width) for y in range(self.field_height)
                                    if (x, y) != init_position and (x, y) not in self.neighbours(init_position)]
        mine_positions = sample(potential_mine_positions, self.field_mines)
        for position in mine_positions:
            self[position].mine = True
            for neighbour in self.neighbours(position):
                self[neighbour].neighbouring_mines += 1
        self.start_time = time()
        self.__update_state__(PROGRESS)

    def __start_time(self):
        self.start_time = time()

    def __stop_time(self):
        self.game_duration = time() - self.start_time

    def time_progressed(self):
        if self.game_state == INIT:
            return 0
        elif self.game_state == PROGRESS:
            # Game in PROGRESS, return time since game start.
            return int(time() - self.start_time)
        else:
            return int(self.game_duration)

    def pending_mines(self):
        # This methods returns number of mines that have not been marked
        # can go to negative if user marks more mines than those existing
        return self.field_mines - sum(map(lambda pos: self[pos].marked, self))

    def uncover(self, position):
        if self.game_state == INIT:
            self.__init_game__(init_position=position)
            # After initialization it goes into progress.

        if self.game_state == PROGRESS:
            # Clicking covered squares that are not marked nor uncertain,
            # will only uncover the square.
            if not self[position].uncovered and \
                    not self[position].marked and \
                    not self[position].uncertain:
                self[position].uncover()
                # After uncovering, determine the next set of actions, base on uncovered square

                if self[position].mine:
                    # If uncovered a mine
                    self.__update_state__(GAME_OVER)
                    self.__stop_time()
                    return

                self.uncovered += 1
                if self.uncovered >= self.total_non_mines:
                    # If all non-mine squares uncovered.
                    self.__update_state__(WINNER)
                    self.__stop_time()
                    return

                if not self[position].neighbour_mines:
                    for neighbour in self.neighbours(position):
                        # Remove flags on the neighbour to facilitate uncovering
                        # because of the above conditions to prevent mistakenly uncovering
                        # marked positions.
                        self[position].marked = False
                        self[position].uncertain = False
                        self.uncover(neighbour)

    def toggle(self, position, force_mark=False):
        """ This function is used to toggle a covered position to marked or uncertain or not flagged state.
        force_mark marks the position irrespective of previous state. """
        if self.game_state == PROGRESS:
            if not self[position].uncovered:
                if not force_mark:
                    """ TOGGLE in a sequence INITIAL -> MARKED -> UNCERTAIN """
                    if self[position].marked:
                        self[position].marked = False
                        self[position].uncertain = True
                    elif self[position].uncertain:
                        self[position].marked = False
                        self[position].uncertain = False
                    else:
                        self[position].marked = True
                        self[position].uncertain = False
                else:
                    """ Force mark """
                    self[position].marked = True
                    self[position].uncertain = False

    def uncover_neighbours(self, position):
        """ This function uncovers all unmarked neighbours of mine neighbour
        when number of marked neighbours equals the neighbouring mines.
            NOTE: none of the neighbours must uncertain.
        """
        if self.game_state == PROGRESS:
            if self[position].uncovered and self[position].neighbour_mines:
                neighbours = self.neighbours(position)
                marked_neighbour_mines = sum(map(lambda pos: self[pos].marked, neighbours))
                if any(map(lambda pos: self[pos].uncertain, neighbours)):
                    # If any of the neighbours are uncertain then return.
                    return

                if marked_neighbour_mines == self[position].neighbouring_mines:
                    # If number of marked mines matches the actual neighbouring mines
                    unmarked_positions = [pos for pos in self.neighbours(position) if not self[pos].marked]
                    for neighbour_position in unmarked_positions:
                        # Uncover all the unmarked squares.
                        self.uncover(neighbour_position)

    def game_over(self):
        return self.game_state == GAME_OVER or self.game_state == WINNER
