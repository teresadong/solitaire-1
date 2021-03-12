import random
import re
import time
from card_elements import Card, Deck
from game_elements import Tableau, StockWaste, Foundation

BREAK_STRING = "-------------------------------------------------------------------"

class Game:
	def __init__(self):
		self.d = Deck()
		self.t = Tableau([self.d.deal_cards(x) for x in range(1,8)])
		self.f = Foundation()
		self.sw = StockWaste(self.d.deal_cards(24))

		self.num_turns = 0
		self.moves = 0
		self.score = 0
		self.start_time = time.time()
		self.end_time = None
		self.successful_moves = []

	def getFinalMetrics(self):
		self.end_time = time.time()
		self.game_duration = self.end_time - self.start_time
		win_indicator = 1 if self.gameWon() else 0
		return self.score, self.moves, self.game_duration, win_indicator

	def gameWon(self):
		return self.f.gameWon()


	def printValidCommands(self):
		""" Provides the list of commands, for when users press 'h' """
		print("Valid Commands: ")
		print("\tmv - move card from Stock to Waste")
		print("\twf - move card from Waste to Foundation")
		print("\twt #T - move card from Waste to Tableau")
		print("\ttf #T - move card from Tableau to Foundation")
		print("\ttt #T1 #T2 - move card from one Tableau column to another")
		print("\th - help")
		print("\tq - quit")
		print("\t*NOTE: Hearts/diamonds are red. Spades/clubs are black.")


	def printTable(self, tableau=None, foundation=None, stock_waste=None):
		""" Prints the current status of the table """

		print(BREAK_STRING)
		print("Waste \t Stock \t\t\t\t Foundation")
		print("{}\t{}\t\t{}\t{}\t{}\t{}".format(self.sw.getWaste(), self.sw.getStock(),
			self.f.getTopCard("club"), self.f.getTopCard("heart"),
			self.f.getTopCard("spade"), self.f.getTopCard("diam")))
		print("\nTableau\n\t1\t2\t3\t4\t5\t6\t7\n")
		# Print the cards, first printing the unflipped cards, and then the flipped.
		for x in range(self.t.pile_length()):
			print_str = ""
			for col in range(7):
				hidden_cards = self.t.unflipped[col]
				shown_cards = self.t.flipped[col]
				if len(hidden_cards) > x:
					print_str += "\tx"
				elif len(shown_cards) + len(hidden_cards) > x:
					print_str += "\t" + str(shown_cards[x-len(hidden_cards)])
				else:
					print_str += "\t"
			print(print_str)
		print("\n"+BREAK_STRING)



	def takeTurn(self, command,verbose=False):
		turn_success = False

		if command == "mv":
			if self.sw.stock_to_waste():
				turn_success = True

		elif command == "wf":
			if self.sw.getWaste() != "empty":
				if self.f.addCard(self.sw.getWaste()):
					self.sw.pop_waste_card()
					self.score += 10
					turn_success = True

			else:
				if verbose:
					print("Error! No card could be moved from the Waste to the Foundation.")


		elif "wt" in command and len(command) == 3:
			try:
				col = int(command[-1]) - 1
			except ValueError:
				if verbose:
					print('Error! Invalid Tableau Value')

			else:
				if col < 8:
					if self.t.waste_to_tableau(self.sw, col):
						self.score += 5
						turn_success = True

					else:
						if verbose:
							print("Error! No card could be moved from the Waste to the Tableau column.")

				else:
					if verbose:
						print('Error! Invaid Tableau Value')


		elif "tf" in command and len(command) == 3:
			try:
				col = int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')

			else:
				if col < 8:
					if self.t.tableau_to_foundation(self.f, col):
						self.score += 10
						turn_success = True

					else:
						if verbose:
							print("Error! No card could be moved from the Tableau column to the Foundation.")


				else:
					if verbose:
						print("Error: Invalid Tablue Value")


		elif "tt" in command and len(command) == 4:
			try:
				c1, c2 = int(command[-2]) - 1, int(command[-1]) - 1
			except ValueError:
				if verbose:
					print('Error! Invalid Tableau Value')


			else:
				if c1 < 8 and c2 < 8:
					if self.t.tableau_to_tableau(c1, c2):
						self.score += 5
						turn_success = True

					else:
						if verbose:
							print("Error! No card could be moved from that Tableau column.")

				else:
					if verbose:
						print("Error! Invalid Tableau Value")

		else:
			if verbose:
				print('Error! Not a Valid Command')


		if turn_success == True:
			self.moves += 1
			if verbose:
				print(f"Success! {command}")
			self.successful_moves.append(command)

		return turn_success


	def simulateBasic(self,verbose=False):
		self.num_turns +=1

		#Turn Up the First Deck Card First (#4)
		if self.sw.getWaste() == "empty":
			if self.takeTurn("mv"):
				if verbose:
					print("mv")
				return True

		#Check if can move any Tableau Cards to Foundation
		for col_index in range(7):
			column_cards = self.t.flipped[col_index]			
			if len(column_cards)>0:
				command = f"tf{col_index+1}"
				if self.takeTurn(command):
					if verbose:
						print(command)
					return True

		# Check if I can move any Waste to Foundation
		if self.takeTurn("wf"):
			if verbose:
				print("wf")
			return True

		# If there is an open tableau, move king to it:
		for col_index in range(7):
			if len(self.t.flipped[col_index])==0:
				#Check if we can move from any Tableau to Foundation
				for col_index2 in range(7): 
					if col_index != col_index2:
						# Only move King if its part of a pile with Unexposed cards (Don't want to move king from one blank pile to other)
						if len(self.t.flipped[col_index2]) > 0 and len(self.t.unflipped[col_index2])>0 and self.t.flipped[col_index2][0].value == 13:
							command = f"tt{col_index2+1}{col_index+1}"
							if self.takeTurn(command):
								if verbose:
									print(command)
								return True


				#Check if we can move any king from waste to tableau
				if self.sw.getWaste()!="empty":
					if self.takeTurn(f"wt{col_index+1}"):
						if verbose:
							print(f"wt{col_index+1}")	
						return True 


		# Add Waste Cards to Tableau
		for col_index in range(7):
			column_cards = self.t.flipped[col_index]			
			if len(column_cards)>0:
				# Make sure Waste is not Empty
				if self.sw.getWaste()!="empty":    
					if self.takeTurn(f"wt{col_index+1}"):
						if verbose:
							print(f"wt{col_index+1}")
						return True

		# Only Move Cards from Pile 1 to Pile 2 if Can Expose New Cards
		for p1_index in range(7):			
			if len(self.t.flipped[p1_index])>0:
				for p2_index in range(7):
					if p1_index != p2_index and len(self.t.flipped[p2_index])>0:
						# Move only if the last card in Pile 2 Flipped can be attached to first card for Pile 1 Fixed
						if self.t.flipped[p2_index][-1].canAttach(self.t.flipped[p1_index][0]):
							command = f"tt{p1_index+1}{p2_index+1}"
							if self.takeTurn(command):
									if verbose:
										print(command)	
									return True


		return False


	def basicAuto(self, verbose = False):
		if self.gameWon():
			return False

		turnResult = self.simulateBasic(verbose=verbose)
		if verbose:
			self.printTable()

		if turnResult:
			self.basicAuto(verbose=verbose)

		else: 

			#End draw from deck 
			if self.sw.getStock()!="empty":
				self.takeTurn("mv")
				return self.basicAuto(verbose=verbose)
			else: 				
				return False

def gameManual():
	game = Game()
	game.printValidCommands()
	game.printTable()

	while not game.gameWon():
		command = input("Enter a command (type 'h' for help): ")
		command = command.lower().replace(" ", "")
		if command == "h":
			game.printValidCommands()
		elif command == "q":
			print("Game exited.")
			break
		elif re.match("|".join(['mv','wf','wt','tf','tt']), command):
			game.takeTurn(command,verbose=True)
		else:
			print("Sorry, that is not a valid command.")

	if game.gameWon():
		print("Congratulations! You've won!")

	score,num_moves, game_duration, did_win = game.getFinalMetrics()

	print(f"Final Score: {score} \nNum Moves: {num_moves} \nGame Duration: {game_duration} seconds")
	new_line = f"{score},{num_moves},{game_duration},{did_win}"
	with open("runs_manual.log","a") as a_file:
		a_file.write("\n")
		a_file.write(new_line)

def gameAutoBasic():
	game = Game()
	game.printValidCommands()
	game.printTable()

	game.basicAuto()

	score,num_moves, game_duration, did_win = game.getFinalMetrics()

	print(f"Final Score: {score} \nNum Moves: {num_moves} \nGame Duration: {game_duration} seconds ")
	new_line = f"{score},{num_moves},{game_duration},{did_win}"
	with open("runs_auto_basic.log","a") as a_file:
		a_file.write("\n")
		a_file.write(new_line)


if __name__ == "__main__":

	# gameManual()
	for i in range(100):
		gameAutoBasic()
