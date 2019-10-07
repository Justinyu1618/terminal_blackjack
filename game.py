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
	def __init__(self, name, player_num):
		self.name = name
		self.id = uuid4()
		self.score = 0
		self.cards = []
		self.color = eval(f"COLOR.{player_num}")
		self.symbol = chr(randint(33,126))
		self.avatar = [(randint(0,4), randint(0,4)) for i in range(20)]

	def add_card(self, card):
		self.cards.append(card)

	def add_score(self, earnings):
		self.score += earnings


class Dealer(Player):
	def __init__(self, num_decks=1):
		super().__init__("Dealer","DEALER")
		self.color = COLOR.DEALER
		self.avatar = [(randint(0,9), randint(0,5)) for i in range(45)]
		self.deck = []
		for i in range(num_decks):
			self.init_deck()

	def init_deck(self):
		for num in list(range(2,11)) + ['J','Q','K','A']:
			for suit in SUIT:
				self.deck.append(Card(suit, num))

	def deal(self, facedown=False):
		if len(self.deck) == 0:
			return False
		card = self.deck.pop(randint(0, len(self.deck) - 1))
		if facedown:
			card.flip()
		return card

class Game:
	def __init__(self, stdscr):
		self.players = []
		self.dealer = Dealer()
		self.display = DisplayTable(stdscr)
		self.screen = stdscr
		self.turn_order = []

	def sleep(self, time):
		self.screen.timeout(time)
		self.screen.getch()

	def run(self):
		self.start()
		self.display.next_state()
		self.gameplay()
		self.sleep(10000000)

	def start(self):
		curses.echo()
		self.display.set_dealer(self.dealer)
		self.display.refresh()

		#starting screen
		p_count = 0
		key = None
		while(p_count != 4 and key != ord('s')):
			key = self.screen.getch()
			if key == ord('n'):
				p_count += 1
				new_player = Player(f"Player {p_count}", f"P{p_count}")
				self.players.append(new_player)
				self.display.add_player(new_player)
		
	def gameplay(self):
		turn_order = self.players.copy()
		for player in s

		for i in range(2):
			for p in self.players:
				p.add_card(self.dealer.deal())
				self.display.refresh()
				self.sleep(300)
			self.dealer.add_card(self.dealer.deal(facedown = i == 1))
			self.display.refresh()
		while(self.turn_order):
			for i in range(turn_order):
				player = turn_order[i]
				self.display.set_turn(player)




def main(stdscr):
	init_colors()
	game = Game(stdscr)
	game.run()

if __name__ == '__main__':
	stdscr = curses.initscr()
	curses.wrapper(main)	

