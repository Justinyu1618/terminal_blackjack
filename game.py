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
		self.score = 1000
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
		if len(self.sums()) == 0:
			return self.lose()
		else:
			return False
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
				temp = [11 + t for t in total.copy()]
				total = [1 + t for t in total]
				total.extend(temp)
			elif not card.num.isdigit():
				total = [10 + t for t in total]
			else:
				total = [int(card.num) + t for t in total]
		total = [t for t in total if t <= 21]
		return total

	def get_options(self):
		#TODO make these constants
		ret = [CMD.HIT, CMD.STAND]
		sums = set(self.sums())
		if len(self.cards) == 2 and (9 in sums or 10 in sums or 11 in sums):
			self.options.append(CMD.DOUBLE)
		self.options = ret


class Dealer(Player):
	def __init__(self, num_decks=1):
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


class Game:
	def __init__(self, stdscr):
		self.players = []
		self.dealer = Dealer()
		self.display = DisplayTable(stdscr)
		self.screen = stdscr

	def sleep(self, time):
		self.screen.timeout(time)
		self.screen.getch()
		self.screen.notimeout(True)

	def run(self):
		self.start()
		keep_playing = True
		while(keep_playing):
			self.reset()
			self.sleep(1000)
			self.gameplay()
			keep_playing = self.end()

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
		self.display.set_state("betting")
		for player in turn_order:
			self.display.set_turn(player)
			bet = ""
			while(not bet.isdigit() or int(bet) > player.score
					or int(bet) < BET_MIN or int(bet) > BET_MAX):
				bet = self.screen.getstr()
				# if self.display.state != "betting_error":
				# 	self.display.set_state("betting_error")
			player.make_bet(bet)
		self.display.set_turn(None)

		self.display.set_state("dealing")
		for i in range(2):
			for p in self.players:
				p.add_card(self.dealer.deal())
				self.display.refresh()
				self.sleep(300)
			self.dealer.add_card(self.dealer.deal(facedown = i == 1))
			self.display.refresh()
		
		self.display.set_state("turn")
		for i in range(len(turn_order)):
			player = turn_order[i]
			player.get_options()
			self.display.set_turn(player)
			while(True):
				cmd = self.screen.getch()
				while(cmd not in list(map(lambda x:ord(x.value), CMD))):
					cmd = self.screen.getch()
				self.display.draw_starting_screen()
				self.display.refresh()
				if cmd == ord('h'):
					player.add_card(self.dealer.deal())
				elif cmd == ord(CMD.STAND.value):
					break
				elif cmd == ord(CMD.DOUBLE.value):
					player.score -= player.bet
					player.bet *= 2
					player.add_card(self.dealer.deal())
				self.display.refresh()
				self.sleep(300)
				bet = player.bust()
				if bet:
					self.dealer.add_score(bet)
					break
		self.dealer.reveal()
		self.display.refresh()
		self.sleep(1000)
		while(True):
			if self.dealer.bust() == False:
				for p in self.players:
					if p.cards: 
						self.dealer.score -= p.bet
						p.win()
				self.display.refresh()
				break
			elif max(self.dealer.sums()) < 17:
				self.dealer.add_card(self.dealer.deal())
				self.display.refresh()
				self.sleep(1000)
			else:
				dealer_sum = max(self.dealer.sums())
				for p in self.players:
					if p.cards:
						self.display.set_turn(p)
						self.sleep(1000)
						p_sum = max(p.sums())
						if p_sum > dealer_sum: 
							self.dealer.score -= p.bet
							p.win()
						elif p_sum < dealer_sum:
							self.dealer.add_score(p.lose())
						else:
							p.standoff()
				break

	def end(self):
		self.display.set_state("end")
		while(True):
			cmd = self.screen.getch()
			if cmd == ord('y'):
				return True 
			elif cmd == ord('n'):
				return False

	def reset(self):
		for p in self.players:
			p.reset()
		self.dealer.reset()
		
				

		
					






def main(stdscr):
	init_colors()
	game = Game(stdscr)
	game.run()

if __name__ == '__main__':
	stdscr = curses.initscr()
	curses.wrapper(main)	

