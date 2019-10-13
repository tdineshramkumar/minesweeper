from argparse import ArgumentParser

import pygame

from minesweeper import INIT, WINNER, PROGRESS, GAME_OVER
from minesweeper import MineSweeper
from utilities import solver, UNCOVER, MARK

MIN_FIELD_MINES = 10
MIN_FIELD_WIDTH = 10
MAX_FIELD_WIDTH = 30
MIN_FIELD_HEIGHT = 8
MAX_FIELD_HEIGHT = 20

parser = ArgumentParser(description='Yet Another Minesweeper Game.')
parser.add_argument('--field_width', type=int, default=MIN_FIELD_WIDTH, help="the number of columns in the field.")
parser.add_argument('--field_height', type=int, default=MIN_FIELD_HEIGHT, help="the number of rows in the field.")
parser.add_argument('--field_mines', type=int, default=MIN_FIELD_MINES, help='the number of mines in the field.')
args = parser.parse_args()

# Obtain the arguments from the command line.
field_width = min(MAX_FIELD_WIDTH, max(args.field_width, MIN_FIELD_WIDTH))
field_height = min(MAX_FIELD_HEIGHT, max(args.field_height, MIN_FIELD_HEIGHT))
field_mines = min(field_width * field_height - 9, max(args.field_mines, MIN_FIELD_MINES))

pygame.init()

def load_image(file_name):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (25, 25))

# Load all the image assets.
initial_tile = load_image('assets/initial.PNG')
empty_tile = load_image('assets/empty.PNG')
marked_tile = load_image('assets/marked.PNG')
uncertain_tile = load_image('assets/uncertain.PNG')
mine_tile = load_image('assets/mine1.PNG')
selected_mine_tile = load_image('assets/mine2.PNG')
wrong_marked_tile = load_image('assets/mine3.PNG')
neighbour_tiles = {
    1: load_image('assets/1.PNG'),
    2: load_image('assets/2.PNG'),
    3: load_image('assets/3.PNG'),
    4: load_image('assets/4.PNG'),
    5: load_image('assets/5.PNG'),
    6: load_image('assets/6.PNG'),
    7: load_image('assets/7.PNG'),
    8: load_image('assets/8.PNG'),
}

minus_image = pygame.image.load('assets/header/-.PNG')
digit_images = {
    0: pygame.image.load('assets/header/0.PNG'),
    1: pygame.image.load('assets/header/1.PNG'),
    2: pygame.image.load('assets/header/2.PNG'),
    3: pygame.image.load('assets/header/3.PNG'),
    4: pygame.image.load('assets/header/4.PNG'),
    5: pygame.image.load('assets/header/5.PNG'),
    6: pygame.image.load('assets/header/6.PNG'),
    7: pygame.image.load('assets/header/7.PNG'),
    8: pygame.image.load('assets/header/8.PNG'),
    9: pygame.image.load('assets/header/9.PNG'),
}

progress_smiley = pygame.image.load('assets/header/progress.PNG')
winner_smiley = pygame.image.load('assets/header/winner.PNG')
game_over_smiley = pygame.image.load('assets/header/game_over.PNG')


tile_width, tile_height = initial_tile.get_rect().size
digit_width, digit_height = minus_image.get_rect().size


def draw_minesweeper(win, minesweeper, offset=(0, 0)):
    # Draws the minesweeper field on the given window starting at the given offset.
    width = field_width * tile_width
    height = field_height * tile_height
    surface = pygame.Surface((width, height))

    for position, square in minesweeper.field.items():
        # Draws the squares based on their flags (marked/ uncertain) and game state.
        blit_position = (position[0] * tile_width, position[1] * tile_height)
        if not square.mine and square.uncovered:
            if square.neighbour_mines:
                surface.blit(neighbour_tiles[square.neighbouring_mines], blit_position)
            if not square.neighbour_mines:
                surface.blit(empty_tile, blit_position)

        if minesweeper.game_over():
            if square.mine and square.marked:
                surface.blit(marked_tile, blit_position)
            elif square.mine and not square.marked:
                if not square.uncovered:
                    surface.blit(mine_tile if minesweeper.game_state == GAME_OVER else marked_tile, blit_position)
                else:
                    surface.blit(selected_mine_tile, blit_position)
            elif not square.mine and square.marked:
                surface.blit(wrong_marked_tile, blit_position)
            elif not square.uncovered:
                surface.blit(initial_tile, blit_position)
        else:
            if not square.uncovered:
                surface.blit(marked_tile if square.marked else uncertain_tile if square.uncertain else initial_tile,
                             blit_position)

    win.blit(surface, offset)


def number_surface(number):
    # Return a surface blitted with digits corresponding to the given integer.
    # It has a limit of numbers between -99 to 999
    surf = pygame.Surface((3 * digit_width, digit_height))
    number = max(-99, min(number, 999))
    digit2, digit3 = (abs(number) % 100) // 10, (abs(number) % 10)
    surf.blit(minus_image if number < 0 else digit_images[number // 100], (0, 0))
    surf.blit(digit_images[digit2], (digit_width, 0))
    surf.blit(digit_images[digit3], (digit_width * 2, 0))
    return surf


def handle_clicks(event, minesweeper, offset=(0, 0)):
    # This function handles clicks on the minesweeper.
    # Calls appropriate method on the minesweeper and specified the position base on click location
    # This function calls uncover on LEFT click on covered location and
    # uncover_neighbours on LEFT click on uncovered location. It calls toggle on RIGHT click.
    if event.type == pygame.MOUSEBUTTONDOWN:
        for position in minesweeper.field:
            if 0 < event.pos[0] - position[0] * tile_width - offset[0] < tile_width and \
                    0 < event.pos[1] - position[1] * tile_height - offset[1] < tile_height:
                if event.button == 1:
                    if not minesweeper.field[position].uncovered:
                        print(f'UNCOVER {position[0]}, {position[1]}')
                        minesweeper.uncover(position)
                    else:
                        print(f'UNCOVER NEIGHBOURS {position[0]}, {position[1]}')
                        minesweeper.uncover_neighbours(position)
                    return True
                elif event.button == 3:
                    print(f'TOGGLE {position[0]}, {position[1]}')
                    minesweeper.toggle(position)
                    return True
    return False

def draw_smiley(win, minesweeper, offset):
    # This function draws the corresponding image based on game state on the window at specified offset.
    if minesweeper.game_state == INIT or minesweeper.game_state == PROGRESS:
        win.blit(progress_smiley, offset)
    elif minesweeper.game_state == GAME_OVER:
        win.blit(game_over_smiley, offset)
    elif minesweeper.game_state == WINNER:
        win.blit(winner_smiley, offset)


def handle_click_smiley(event, minesweeper, offset):
    # This function calls reset on minesweeper when smiley is clicked.
    # Also returns whether reset was called or not.
    if event.type == pygame.MOUSEBUTTONDOWN:
        if 0 < event.pos[0] - offset[0] < digit_width and \
                0 < event.pos[1] - offset[1] < digit_height:
            minesweeper.reset()
            # Indicate that click has been handled
            print('RESET')
            return True
    return False


def main_loop():
    # Obtain the width and height of the screen.
    width = field_width * tile_width + 10
    height = field_height * tile_height + digit_height + 15
    smiley_offset = (width // 2 - digit_height // 2, 5)

    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Minesweeper')
    clock = pygame.time.Clock()

    minesweeper = MineSweeper(field_width, field_height, field_mines)
    steps = solver(minesweeper)

    run = True
    while run:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key in [pygame.K_q, pygame.K_ESCAPE])):
                run = False
            # Handle mouse clicks.
            if handle_clicks(event, minesweeper, offset=(5, digit_height + 10)):
                # On user input, just in case reset the solver.
                steps = solver(minesweeper)

            if handle_click_smiley(event, minesweeper, offset=smiley_offset):
                # On reset, create a new solver.
                steps = solver(minesweeper)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset the minesweeper.
                minesweeper.reset()
                print('RESET')
                steps = solver(minesweeper)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                # Try twice if in case generator was exhausted in which case we use a newer one.
                # If solver can't solve it in second try don't simply keep calling it.
                tries = 0
                while tries <= 1:
                    try:
                        # Obtain the step from the solver.
                        position, operation = next(steps)
                        if operation == MARK:
                            print(f'[AI] MARK {position[0]}, {position[1]}')
                            minesweeper.toggle(position, force_mark=True)
                        elif operation == UNCOVER:
                            print(f'[AI] UNCOVER {position[0]}, {position[1]}')
                            minesweeper.uncover(position)
                        break
                    except StopIteration:
                        # reset the solver in case previous one exhausted and check if it can solve
                        steps = solver(minesweeper)
                        tries += 1

        win.fill((255, 255, 255))
        # Render the time and number of mines.
        count_surf = number_surface(minesweeper.pending_mines())
        win.blit(count_surf, (5, 5))
        time_surf = number_surface(minesweeper.time_progressed())
        time_rect = time_surf.get_rect()
        win.blit(time_surf, (width - time_rect.width - 5, 5))
        # Render the smiley
        draw_smiley(win, minesweeper, offset=smiley_offset)

        # Render the minesweeper field
        draw_minesweeper(win, minesweeper, offset=(5, digit_height + 10))
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main_loop()
