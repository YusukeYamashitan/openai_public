import curses
import random
import time

# Game configuration
WIDTH = 10
HEIGHT = 20
TICK_RATE = 0.3  # seconds per automatic drop

# Tetromino definitions: list of rotations, each rotation is a list of (x,y)
# Coordinates are relative to top-left corner of 4x4 grid
PIECES = {
    'I': [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
    ],
    'O': [
        [(1,0),(2,0),(1,1),(2,1)],
    ],
    'T': [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)],
    ],
    'S': [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
    ],
    'Z': [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)],
    ],
    'J': [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)],
    ],
    'L': [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)],
    ],
}

PIECE_TYPES = list(PIECES.keys())


def create_board():
    return [[0]*WIDTH for _ in range(HEIGHT)]


def check_collision(board, piece, offset_x, offset_y, rotation):
    cells = PIECES[piece][rotation]
    for x, y in cells:
        bx = x + offset_x
        by = y + offset_y
        if bx < 0 or bx >= WIDTH or by < 0 or by >= HEIGHT:
            return True
        if board[by][bx]:
            return True
    return False


def place_piece(board, piece, offset_x, offset_y, rotation):
    cells = PIECES[piece][rotation]
    for x, y in cells:
        board[offset_y + y][offset_x + x] = 1


def clear_lines(board):
    new_board = [row for row in board if not all(row)]
    cleared = HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0]*WIDTH)
    return new_board, cleared


def draw_board(stdscr, board, piece, offset_x, offset_y, rotation, score):
    stdscr.clear()
    # Draw board border
    for y in range(HEIGHT):
        stdscr.addstr(y, 0, '|')
        stdscr.addstr(y, WIDTH+1, '|')
    stdscr.addstr(HEIGHT, 0, '+' + '-'*WIDTH + '+')

    # Draw existing blocks
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if val:
                stdscr.addstr(y, x+1, '#')

    # Draw current piece
    cells = PIECES[piece][rotation]
    for x, y in cells:
        stdscr.addstr(offset_y + y, offset_x + x + 1, '*')

    stdscr.addstr(0, WIDTH + 4, f'Score: {score}')
    stdscr.refresh()


def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    board = create_board()
    score = 0

    current = random.choice(PIECE_TYPES)
    rotation = 0
    pos_x = WIDTH // 2 - 2
    pos_y = 0

    last_drop = time.time()

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key in (curses.KEY_LEFT, ord('a')):
            if not check_collision(board, current, pos_x-1, pos_y, rotation):
                pos_x -= 1
        elif key in (curses.KEY_RIGHT, ord('d')):
            if not check_collision(board, current, pos_x+1, pos_y, rotation):
                pos_x += 1
        elif key in (curses.KEY_UP, ord('w')):
            new_rot = (rotation + 1) % len(PIECES[current])
            if not check_collision(board, current, pos_x, pos_y, new_rot):
                rotation = new_rot
        elif key in (curses.KEY_DOWN, ord('s')):
            if not check_collision(board, current, pos_x, pos_y+1, rotation):
                pos_y += 1
                last_drop = time.time()

        if time.time() - last_drop > TICK_RATE:
            if not check_collision(board, current, pos_x, pos_y+1, rotation):
                pos_y += 1
            else:
                place_piece(board, current, pos_x, pos_y, rotation)
                board, cleared = clear_lines(board)
                score += cleared
                current = random.choice(PIECE_TYPES)
                rotation = 0
                pos_x = WIDTH // 2 - 2
                pos_y = 0
                if check_collision(board, current, pos_x, pos_y, rotation):
                    draw_board(stdscr, board, current, pos_x, pos_y, rotation, score)
                    stdscr.addstr(HEIGHT//2, WIDTH//2-4, 'Game Over')
                    stdscr.refresh()
                    stdscr.nodelay(False)
                    stdscr.getch()
                    break
            last_drop = time.time()

        draw_board(stdscr, board, current, pos_x, pos_y, rotation, score)
        time.sleep(0.01)


if __name__ == '__main__':
    curses.wrapper(game_loop)
