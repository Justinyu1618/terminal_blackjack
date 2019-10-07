import game
import curses

def main(stdscr):
	# game = game.Game(stdscr)
	# game.start()
	print(curses.COLS, curses.LINES)
	p = stdscr.derwin(15,15,10,10)
	p1 = stdscr.derwin(5,5,30,10)
	stdscr.timeout(30)
	count = 0
	while(stdscr.getch() != ord('q')):
		p.box()
		p.bkgd('$')
		count+=1
		if count > 9:
			count = 0
		p.addstr(count,0,"p")
		p1.box()
		p1.bkgd('@')
		p1.refresh()
		p.refresh()
		

if __name__ == '__main__':
	stdscr = curses.initscr()
	curses.wrapper(main)	