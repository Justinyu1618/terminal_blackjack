from enum import Enum

class COLOR(Enum):
	CARD_BG = 1
	CARD_RED = 2
	CARD_BLACK = 3
	CARD_BACK = 4
	P1 = 5
	P2 = 6
	P3 = 7
	P4 = 8

class SUIT(Enum):
	D = "diamonds"
	S = "spades"
	H = "hearts"
	C = "clubs"