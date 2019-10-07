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
		y = self.y + round(self.h/2)
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

	def scale(self, scale):
		self.x = int(self.x*scale)
		self.w = int(self.w*scale)

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
		return {'bounds': partition.get_bounds_coords(),
				'player': partition.get_player_coords(),
				'cards': partition.get_card_coords(len(player.cards)),
				'score': partition.get_score_coords()}

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

	def refresh(self):
		self.player_wind.clear()
		for player in self.players:
			self.draw_player(player)
		self.player_wind.refresh()
	
	def add_player(self, player):
		self.partitions.add_player(player.id)
		self.players.add(player)
		self.refresh()

	def draw_player(self, player):
		coords = self.partitions.get_coords(player)
		self.draw_player(player, coords['player'])
		self.draw_score(player.score, coords['score'])
		for i in range(len(player.cards)):
			self.draw_card(player.cards[i], coords['cards'][i])
		self.draw_boundary(coords['bounds'])

	def draw_card(self, card, loc):
		x, y, w, h = loc
		for j in range(y,y+h):
			for i in range(x, x+w+1):
				self.player_wind.addstr(j,i," ", curses.color_pair(1))
		if card.facedown:
			for j in range(y,y+h):
				for i in range(x, x+w+1):
					self.player_wind.addstr(j,i,"%", curses.color_pair(COLOR.CARD_BLACK.value))
		else:
			self.player_wind.addstr(y, x,
							card.symbol, curses.color_pair(card.color.value))
			self.player_wind.addstr(y + h-1, x + w-1,
							card.symbol, curses.color_pair(card.color.value))
			self.player_wind.addstr(y + int(h/2), x + int(w/2),
							card.num, curses.color_pair(card.color.value))

	def draw_boundary(self, loc):
		x,y,w,h = loc
		for j in range(y,y+h-1):
			self.player_wind.addstr(j,x,"|")
			self.player_wind.addstr(j,x+w-1,"|")

	def draw_score(self, score, loc):
		pass 

	def draw_player(self, player, loc):
		x,y = loc
		avatar = player.avatar
		for i,j in avatar:
			self.player_wind.addstr(y + j, x + i, player.symbol, curses.color_pair(player.color.value))

	def draw_starting_screen(self):
		msg1 = "Press 'n' to add more players"
		msg2 = "Press 's' to start"
		self.dealer_wind.addstr(round(self.H/4), round(self.W/2 - len(msg1)), msg1)
		self.dealer_wind.addstr(round(self.H/4)+1, round(self.W/2 - len(msg2)), msg2)

	def draw_game_screen(self):
		pass

def wait(stdscr):
	while(stdscr.getch() != ord('q')):
		pass
