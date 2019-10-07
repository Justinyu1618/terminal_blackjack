from .constants import *
from uuid import uuid4
from random import randint

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
		self.score = STARTING_SCORE
		self.cards = []
		self.color = eval(f"COLOR.{player_num}")
		self.symbol = chr(randint(33,126))
		self.avatar = [(randint(0,4), randint(0,4)) for i in range(20)]
		self.bet = 0
		self.options = []

	def reset(self):
		self.cards = []
		self.bet = 0
		self.options = []

	def add_card(self, card):
		self.cards.append(card)

	def add_score(self, earnings):
		self.score += int(earnings)
	
	def make_bet(self, amount):
		self.score -= int(amount)
		self.bet = int(amount) 

	def bust(self, cost=0):
		return len(self.sums()) == 0

	def lose(self):
		self.cards = []
		bet = self.bet
		self.bet = 0
		return bet

	def standoff(self):
		self.score += self.bet
		self.bet = 0

	def win(self):
		self.score += self.bet * 2
		self.bet = 0

	def sums(self):
		total = [0]
		for card in self.cards:
			if card.num == 'A':
				temp = [11 + t for t in total]
				total = [1 + t for t in total]
				total.extend(temp)
			elif not card.num.isdigit():
				total = [10 + t for t in total]
			else:
				total = [int(card.num) + t for t in total]
		total = [t for t in total if t <= 21]
		return total

	def get_options(self):
		ret = [CMD.HIT, CMD.STAND]
		sums = set(self.sums())
		if len(self.cards) == 2 and (9 in sums or 10 in sums or 11 in sums):
			ret.append(CMD.DOUBLE)
		self.options = ret


class Dealer(Player):
	def __init__(self, num_decks=NUM_DECKS):
		super().__init__("Dealer","DEALER")
		self.color = COLOR.DEALER
		self.avatar = [(randint(0,9), randint(-1,4)) for i in range(45)]
		self.deck = []
		for i in range(num_decks):
			self.init_deck()
		self.bet = "0"
		self.score = 0

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

	def reveal(self):
		self.cards[1].flip()