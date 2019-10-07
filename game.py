from uuid import uuid4
from src.display_util import DisplayTable
from src.constants import *
from src.objects import Card, Player, Dealer
from random import randint
import curses

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
		while(True):
			self.start()
			keep_playing = True
			while(keep_playing):
				self.sleep(1000)
				self.gameplay()
				self.reset()
				if not self.players:
					break
				keep_playing = self.end()
			self.end_game()

	def start(self):
		curses.echo()
		self.display.set_dealer(self.dealer)
		self.display.refresh()
		self.display.set_state("starting")
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
		self.display.set_state("betting")
		self._betting()
		self.display.set_state("dealing")
		self._dealing()
		self.display.set_state("turn")
		self._turn()
		self.display.set_state("scoring")
		self._scoring()
		self.sleep(1000)
		self.check_losers()	

	def _betting(self):
		for player in self.players:
			self.display.set_turn(player)
			bet = ""
			while(not bet.isdigit() or int(bet) > player.score
					or int(bet) < BET_MIN or int(bet) > BET_MAX):
				bet = self.screen.getstr()
				# if self.display.state != "betting_error":
				# 	self.display.set_state("betting_error")
			player.make_bet(bet)
		self.display.set_turn(None)
	
	def _dealing(self):
		for i in range(2):
			for p in self.players:
				p.add_card(self.dealer.deal())
				self.display.refresh()
				self.sleep(300)
			self.dealer.add_card(self.dealer.deal(facedown = i == 1))
			self.display.refresh()

	def _turn(self):
		for i in range(len(self.players)):
			player = self.players[i]
			player.get_options()
			self.display.set_turn(player)
			while(True):
				cmd = self.screen.getch()
				while(cmd not in list(map(lambda x:ord(x.value), CMD))):
					cmd = self.screen.getch()
				if cmd == ord('h'):
					player.add_card(self.dealer.deal())
				elif cmd == ord(CMD.STAND.value):
					break
				elif cmd == ord(CMD.DOUBLE.value):
					player.score -= player.bet
					player.bet *= 2
					player.add_card(self.dealer.deal())
					if player.bust():
						self.dealer.add_score(player.lose())
					break
				self.display.refresh()
				self.sleep(300)
				if player.bust():
					self.dealer.add_score(player.lose())
					break
		self.display.set_turn(None)
		self.dealer.reveal()
		while(not self.dealer_bust() and max(self.dealer.sums()) < 17):
			self.dealer.add_card(self.dealer.deal())
			self.print("Dealing....", 1000)

	def _scoring(self):
		if(not self.dealer.bust() and any([p.cards for p in self.players])):
			dealer_sum = max(self.dealer.sums())
			for p in self.players:
				if p.cards:
					self.display.set_turn(p)
					self.print(f"{p.name} vs Dealer", 1000)
					if max(p.sums()) > dealer_sum: 
						self.print(f"{p.name} Wins!")
						self.dealer.score -= p.bet
						p.win()
					elif max(p.sums()) < dealer_sum:
						self.print("Dealer Wins!")
						self.dealer.add_score(p.lose())
					else:
						self.print("Standoff!")
						p.standoff()
					self.sleep(1000)

	def end(self):
		self.display.set_state("end")
		while(True):
			cmd = self.screen.getch()
			if cmd == ord('y'):
				return True 
			elif cmd == ord('n'):
				return False

	def end_game(self):
		for i in range(5,0,-1):
			self.print(f" Game Over! (restarting in {i})",1000)
		self.display.restart()


	def print(self, msg, delay=0):
		self.display.print(msg)
		self.sleep(delay)

	def reset(self):
		for p in self.players:
			p.reset()
		self.dealer.reset()
		self.display.set_turn(None)
	
	def check_losers(self):
		to_remove = set()
		for p in self.players:
			if p.score <= 0:
				self.print(f"{p.name} has lost!", 1000)
				to_remove.add(p)
				self.display.remove_player(p)
		for p in to_remove:
			self.players.remove(p)

		
	def dealer_bust(self):
		if self.dealer.bust():
			self.print("Dealer BUST!", 1000)
			for p in self.players:
				if p.cards: 
					self.dealer.score -= p.bet
					p.win()
			self.display.refresh()
			return True
		return False


def main(stdscr):
	init_colors()
	game = Game(stdscr)
	game.run()

if __name__ == '__main__':
	stdscr = curses.initscr()
	curses.wrapper(main)	

