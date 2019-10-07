from uuid import uuid4
from src.display_util import DisplayTable
from src.constants import *
from random import randint
import curses

class Card:
	suit_chars = {SUIT.D: "\u2666",
				SUIT.S: "\u2660",
				SUIT.H: "\u2665",
				SUIT.C: "\u2663"}

	def __init__(self, suit, num, facedown=False):
		self.suit = suit
		self.symbol = self.suit_chars[suit]
		self.num = str(num)
		self.facedown = facedown
		self.color = COLOR.CARD_RED if suit == SUIT.D or suit == SUIT.H else COLOR.CARD_BLACK

	def flip(self):
		self.facedown = not self.facedown

class Player:
	def __init__(self, name, num):
		self.name = name
		self.id = uuid4()
		self.score = 0
		self.cards = []
		self.color = eval(f"COLOR.P{num}")
		self.symbol = chr(randint(33,126))
		self.avatar = [(randint(0,4), randint(0,4)) for i in range(9)]

	def add_card(self, card):
		self.cards.append(card)

	def add_score(self, earnings):
		self.score += earnings


class Dealer:
	def __init__(self, num_decks=1):
		self.deck = []
		for i in range(num_decks):
			self.init_deck()

	def init_deck(self):
		for num in list(range(2,11)) + ['J','Q','K','A']:
			for suit in SUIT:
				self.deck.append(Card(suit, num))

	def deal(self, facedown=False):
		if len(deck) == 0:
			return False
		card = deck.pop(random.randint(0, len(self.deck) - 1))
		if facedown:
			card.flip()
		return card





class Game:
	def __init__(self, stdscr):
		self.players = set()
		self.dealer = Dealer()
		self.display = DisplayTable(stdscr)
		self.screen = stdscr

	def start(self):
		curses.echo()
		self.display.refresh()
		p_count = 0
		while(True):
			key = self.screen.getch()
			if key == ord('n'):
				p_count += 1
				new_player = Player(f"Player {p_count}", p_count)
				self.players.add(new_player)
				self.display.add_player(new_player)
			if p_count == 4 or key == ord('s'):
				break
		while(True):
			key = self.screen.getch()
			if key == ord('d'):
				for p in self.players:
					new_card = Card(SUIT.D, randint(0,9))
					p.add_card(new_card)
					self.display.refresh()

def main(stdscr):
	curses.init_pair(COLOR.CARD_BG.value, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(COLOR.CARD_RED.value, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(COLOR.CARD_BLACK.value, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(COLOR.P1.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P2.value, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P3.value, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(COLOR.P4.value, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	game = Game(stdscr)
	game.start()

if __name__ == '__main__':
	stdscr = curses.initscr()
	curses.wrapper(main)	

