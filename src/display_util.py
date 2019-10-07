from .constants import *
import curses

class Item:
	def __init__(self, obj, x, y):
		self.obj = obj
		self.x = x
		self.y = y

# class PlayerPartition:
# 	def __init__(self, x, y, w, h):
# 		self.x, self.y, self.w, self.h = x, y, w, h

# 	def get_player_coords(self):
# 		x = self.x + max(round(self.w/8), 1)
# 		y = self.y + round(self.h/2)
# 		return x,y

# 	def get_card_coords(self):
# 		x1 = self.x + round(self.w*3/8)
# 		w_h = round((self.w*5/8 - 3)/2)
# 		x2 = x1 + w_h + 1
# 		y1 = round((self.h - w_h)/2)
# 		y2 = y1
# 		return ((x1,y1,w_h,w_h), (x2,y2,w_h,w_h))

# 	def get_score_coords(self):
# 		x = self.x + max(round(self.w/8), 1)
# 		y = self.y + round(self.h/8)
# 		return x,y

# 	def get_bounds_coords(self):
# 		return self.x,self.y,self.w,self.h

# 	def scale(self, scale):
# 		self.x = int(self.x*scale)
# 		self.w = int(self.w*scale)

class PlayerPartition:
	def __init__(self, x, y, w, h):
		self.x, self.y, self.w, self.h = x, y, w, h

	def get_player_coords(self):
		x = self.x + max(round(self.w/8), 1)
		y = self.y + round(self.h/2) + 1
		return x,y

	def get_card_coords(self, num_cards):
		ret = []
		if num_cards == 0:
			return []
		card_dim = min(int((self.w - num_cards - 2)/num_cards)-1,int(self.h/2))
		temp_x = self.x
		for i in range(num_cards):
			x = temp_x + 1
			y = self.y + int((self.h/2 - card_dim)/2)
			ret.append((x,y,card_dim, card_dim))
			temp_x += card_dim + 2
		return ret

	def get_score_coords(self):
		x = self.x + max(round(self.w/8), 1)
		y = self.y + round(self.h/8)
		return x,y

	def get_bounds_coords(self):
		return self.x,self.y,self.w,self.h

	def get_coords(self, player):
		return {'bounds': self.get_bounds_coords(),
				'player': self.get_player_coords(),
				'cards': self.get_card_coords(len(player.cards)),
				'score': self.get_score_coords()}

class PartitionManager:
	def __init__(self, bound_x: tuple, bound_y: tuple, num_parts = 4):
		self.x_min, self.x_max = bound_x
		self.y_min, self.y_max = bound_y
		self.w = self.x_max - self.x_min
		self.h = self.y_max - self.y_min
		self.num_players = 0
		self.players = {}

		#temp
		self.partitions = []
		temp_x = self.x_min
		width = int(self.w / num_parts) - 1
		for i in range(num_parts):
			p = PlayerPartition(temp_x, self.y_min, width, self.h)
			self.partitions.append(p)
			temp_x += width + 1

	def add_player(self, player_id):
		# self.num_players += 1
		# for partition in self.players.values():
		# 	partition.scale((self.num_players-1)/self.num_players)
		# new_x = round(self.x_min + self.w * (self.num_players-1/self.num_players))
		# new_w = round(self.w * (1/self.num_players)) - 1
		# self.players[player_id] = PlayerPartition(new_x, self.y_min, new_w, self.h)
		self.players[player_id] = self.partitions.pop(0)

	def remove_player(self, player_id):
		pass 

	def get_coords(self, player):
		partition = self.players[player.id]
		return partition.get_coords(player)

class DisplayTable:
	def __init__(self, stdscr):
		self.items = []
		self.H = curses.LINES - 1
		self.W = curses.COLS - 1
		self.dealer_wind = stdscr.derwin(int(self.H/2-1), self.W, 0, 0)
		self.dealer_wind.box()
		self.player_wind = stdscr.derwin(int(self.H/2-1), self.W, int(self.H/2+1), 0)	
		self.players = set()
		self.partitions = PartitionManager((0,self.W-1), (0,round(self.H/2)))
		self.dealer = None
		self.dealer_partition = None
		#TODO make this not constants
		self.state = "starting"

	def refresh(self):
		if self.state == "starting":
			self.draw_starting_screen()
		elif self.state == "game":
			self.dealer_wind.clear()
			self.draw_game_screen()
			self.draw_dealer()
		self.player_wind.clear()
		for player in self.players:
			self.draw_player(player, self.player_wind)
		self.player_wind.refresh()
		self.dealer_wind.refresh()
	
	def add_player(self, player):
		self.partitions.add_player(player.id)
		self.players.add(player)
		self.refresh()

	def set_dealer(self, dealer):
		self.dealer = dealer
		self.dealer_partition = PlayerPartition(0, 0, int(self.W/2)-1, int(self.H/2)-1)

	def draw_player(self, player, window, coords=None):
		coords = self.partitions.get_coords(player) if not coords else coords
		self.draw_avatar(player, window, coords['player'])
		self.draw_score(player.score, window, coords['score'])
		for i in range(len(player.cards)):
			self.draw_card(player.cards[i], window, coords['cards'][i])
		self.draw_boundary(window, coords['bounds'])

	def draw_dealer(self):
		if not self.dealer:
			return False
		self.draw_player(self.dealer, self.dealer_wind, self.dealer_partition.get_coords(self.dealer))

	def draw_card(self, card, window, loc):
		x, y, w, h = loc
		for j in range(y,y+h):
			for i in range(x, x+w+1):
				window.addstr(j,i," ", curses.color_pair(1))
		if card.facedown:
			for j in range(y,y+h):
				for i in range(x, x+w+1):
					window.addstr(j,i,"@", curses.color_pair(COLOR.CARD_BLACK.value))
		else:
			window.addstr(y, x,
							card.symbol, curses.color_pair(card.color.value))
			window.addstr(y + h-1, x + w-1,
							card.symbol, curses.color_pair(card.color.value))
			window.addstr(y + int(h/2), x + int(w/2),
							card.num, curses.color_pair(card.color.value))

	def draw_boundary(self, window, loc):
		x,y,w,h = loc
		for j in range(y,y+h-1):
			window.addstr(j,x,"|")
			window.addstr(j,x+w-1,"|")

	def draw_score(self, score, window, loc):
		pass 

	def draw_avatar(self, player, window, loc):
		x,y = loc
		avatar = player.avatar
		for i,j in avatar:
			window.addstr(y + j, x + i, player.symbol, curses.color_pair(player.color.value))

	def draw_starting_screen(self):
		msg1 = "Press 'n' to add more players"
		msg2 = "Press 's' to start"
		self.dealer_wind.addstr(round(self.H/4), round(self.W/2 - len(msg1)), msg1)
		self.dealer_wind.addstr(round(self.H/4)+1, round(self.W/2 - len(msg2)), msg2)
		self.dealer_wind.refresh()

	def draw_betting_screen(self):
		msg1 = "Please place your bet (pick a number 5 - 500)"
		self.dealer_wind.addstr(int(self.H/2), max(0,int(self.W*3/4-len(msg1)/2)))


	def next_state(self):
		if self.state == "starting":
			self.state = "game"
		self.refresh()

def wait(stdscr):
	while(stdscr.getch() != ord('q')):
		pass
