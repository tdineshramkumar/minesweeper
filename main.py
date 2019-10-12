import pygame

from minesweeper import INIT, WINNER, PROGRESS, GAME_OVER
from minesweeper import MineSweeper

pygame.init()


def load_image(file_name):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (25, 25))


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

tile_width, tile_height = initial_tile.get_rect().size

field_width, field_height, field_mines = 10, 8, 10

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

digit_width, digit_height = minus_image.get_rect().size


def draw_minesweeper(win, minesweeper, offset=(0, 0)):
    width = field_width * tile_width
    height = field_height * tile_height
    surface = pygame.Surface((width, height))
    for position, square in minesweeper.field.items():
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
    surf = pygame.Surface((3 * digit_width, digit_height))
    number = max(-99, min(number, 999))
    digit2, digit3 = (abs(number) % 100) // 10, (abs(number) % 10)
    surf.blit(minus_image if number < 0 else digit_images[number // 100], (0, 0))
    surf.blit(digit_images[digit2], (digit_width, 0))
    surf.blit(digit_images[digit3], (digit_width * 2, 0))
    return surf


def handle_clicks(event, minesweeper, offset=(0, 0)):
    if event.type == pygame.MOUSEBUTTONDOWN:
        print('Event:', event)
        for position in minesweeper.field:
            if 0 < event.pos[0] - position[0] * tile_width - offset[0] < tile_width and \
                    0 < event.pos[1] - position[1] * tile_height - offset[1] < tile_height:
                if event.button == 1:
                    print('LEFT CLICK AT', position)
                    # minesweeper.uncover(position)

                    if not minesweeper.field[position].uncovered:
                        minesweeper.uncover(position)
                    else:
                        minesweeper.uncover_neighbours(position)
                elif event.button == 3:
                    print('RIGHT CLICK AT', position)

                    minesweeper.toggle(position)


def draw_smiley(win, minesweeper, offset):
    if minesweeper.game_state == INIT or minesweeper.game_state == PROGRESS:
        win.blit(progress_smiley, offset)
    elif minesweeper.game_state == GAME_OVER:
        win.blit(game_over_smiley, offset)
    elif minesweeper.game_state == WINNER:
        win.blit(winner_smiley, offset)


def handle_click_smiley(event, minesweeper, offset):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if 0 < event.pos[0] - offset[0] < digit_width and \
                0 < event.pos[1] - offset[1] < digit_height:
            minesweeper.reset()


def main_loop():
    minesweeper = MineSweeper(field_width, field_height, field_mines)

    width = field_width * tile_width + 10
    height = field_height * tile_height + digit_height + 15

    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Minesweeper')
    clock = pygame.time.Clock()
    smiley_offset = (width // 2 - digit_height // 2, 5)
    run = True
    while run:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE))):
                run = False
            handle_clicks(event, minesweeper, offset=(5, digit_height + 10))
            handle_click_smiley(event, minesweeper, offset=smiley_offset)
        win.fill((255, 255, 255))
        time_surf = number_surface(minesweeper.time())
        time_rect = time_surf.get_rect()
        count_surf = number_surface(minesweeper.pending_mines())
        win.blit(count_surf, (5, 5))
        win.blit(time_surf, (width - time_rect.width - 5, 5))
        draw_minesweeper(win, minesweeper, offset=(5, digit_height + 10))
        draw_smiley(win, minesweeper, offset=smiley_offset)
        pygame.display.update()
        clock.tick(60)


main_loop()
