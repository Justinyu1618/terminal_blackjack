from enum import Enum
import curses

BET_MIN = 5
BET_MAX = 500
STARTING_SCORE = 10
NUM_DECKS = 3

class CMD(Enum):
	HIT = 'h'
	STAND = 's'
	DOUBLE = 'd'

class COLOR(Enum):
	CARD_BG = 1
	CARD_RED = 2
	CARD_BLACK = 3
	CARD_BACK = 4
	P1 = 5
	P2 = 6
	P3 = 7
	P4 = 8
	DEALER = 9

class SUIT(Enum):
	D = "diamonds"
	S = "spades"
	H = "hearts"
	C = "clubs"

def init_colors():
	curses.init_pair(COLOR.CARD_BG.value, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(COLOR.CARD_RED.value, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(COLOR.CARD_BLACK.value, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(COLOR.P1.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P2.value, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P3.value, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P4.value, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(COLOR.DEALER.value, curses.COLOR_WHITE, curses.COLOR_BLACK)
	