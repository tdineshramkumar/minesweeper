from minesweeper import INIT, PROGRESS, WINNER, GAME_OVER

MARK = 'MARK'
UNCOVER = 'UNCOVER'


def solver(minesweeper):
    """ This is a basic solver, which uses mine neighbours to mark potential mines
        and uncover the field. However does not yield solutions in any of the indirect cases.
        This solver returns a generator. Use the returned values to either uncover or mark a square.
        First it returns squares it feels should be marked, then squares which it thinks should be uncovered.
        Once generator stopped yielding, create a new generator and use it obtain solutions.
        However if a generator never yielded a value, then the solver does not know how to proceed,
        then there is no use using the solver again until the change in the field (new square uncovered or marked).
        """
    if minesweeper.game_state == INIT:
        # If game is just started uncover a square in the middle, it may most likely uncover more area.
        init_position = minesweeper.field_width // 2, minesweeper.field_height // 2
        yield init_position, UNCOVER

    if minesweeper.game_state == PROGRESS:
        for position, square in minesweeper.field.items():
            if square.uncovered and square.neighbour_mines:
                # Find number of uncovered squares surrounding the mine neighbour.
                # if it matches the number of mines, mark the remaining unmarked squares as mines
                covered = list(
                    filter(lambda pos: not minesweeper.field[pos].uncovered, minesweeper.neighbours(position)))
                if len(covered) == square.neighbouring_mines:
                    for pos in covered:
                        if not minesweeper.field[pos].marked:
                            yield pos, MARK

        for position, square in minesweeper.field.items():
            if square.uncovered and square.neighbour_mines:
                # Find the marked and unmarked covered squares surrounding the mine neighbour.
                # If the number of marked matches the number of mines, uncover the covered squares surrounding it.
                unmarked = list(
                    filter(lambda pos: not (minesweeper.field[pos].uncovered or minesweeper.field[pos].marked),
                           minesweeper.neighbours(position)))
                marked = list(
                    filter(lambda pos: minesweeper.field[pos].marked, minesweeper.neighbours(position)))
                if len(marked) == square.neighbouring_mines:
                    # Then all unmarked covered can be uncovered
                    for pos in unmarked:
                        if not minesweeper.field[pos].uncovered:
                            # Any previous uncover operation may have potentially uncovered the square
                            # thus to avoid redundant operation.
                            yield pos, UNCOVER

    if minesweeper.game_state == WINNER or minesweeper.game_state == GAME_OVER:
        # Game is over! Nothing to do.
        pass

