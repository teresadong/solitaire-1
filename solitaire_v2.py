import random
import re
import time
from cards import Card, Deck


BREAK_STRING = "-------------------------------------------------------------------"


class Tableau():
	# Class that keeps track of the seven piles of cards on the Tableau

	def __init__(self, card_list):
		self.unflipped = {x: card_list[x] for x in range(7)}
		self.flipped = {x: [self.unflipped[x].pop()] for x in range(7)}

	def flip_card(self, col):
		""" Flips a card under column col on the Tableau """
		if len(self.unflipped[col]) > 0:
			self.flipped[col].append(self.unflipped[col].pop())

	def pile_length(self):
		""" Returns the length of the longest pile on the Tableau """
		return max([len(self.flipped[x]) + len(self.unflipped[x]) for x in range(7)])



	def addCards(self, cards, column):
		""" Returns true if cards were successfully added to column on the Tableau.
			Returns false otherwise. """
		column_cards = self.flipped[column]
		if len(column_cards) == 0 and cards[0].value == 13:
			column_cards.extend(cards)
			return True
		elif len(column_cards) > 0 and column_cards[-1].canAttach(cards[0]):
			column_cards.extend(cards)
			return True
		else:
			return False

	def tableau_to_tableau(self, c1, c2):
		""" Returns True if any card(s) are successfully moved from c1 to c2 on
			the Tableau, returns False otherwise. """
		c1_cards = self.flipped[c1]

		for index in range(len(c1_cards)):
			if self.addCards(c1_cards[index:], c2):
				self.flipped[c1] = c1_cards[0:index]
				if index == 0:
					self.flip_card(c1)
				return True
		return False

	def tableau_to_foundation(self, foundation, column):
		""" Moves a card from the Tableau to the appropriate Foundation pile """
		column_cards = self.flipped[column]
		if len(column_cards) == 0:
			return False

		if foundation.addCard(column_cards[-1]):
			column_cards.pop()
			if len(column_cards) == 0:
				self.flip_card(column)
			return True
		else:
			return False

	def waste_to_tableau(self, waste_pile, column):
		""" Returns True if a card from the Waste pile is succesfully moved to a column
			on the Tableau, returns False otherwise. """
		card = waste_pile.waste[-1]
		if self.addCards([card], column):
			waste_pile.pop_waste_card()
			return True
		else:
			return False

class StockWaste():
	""" A StockWaste object keeps track of the Stock and Waste piles """

	def __init__(self, cards):
		self.deck = cards
		self.waste = []

	def stock_to_waste(self):
		""" Returns True if a card is sucessfully moved from the Stock pile to the
			Waste pile, returns False otherwise. """
		if len(self.deck) + len(self.waste) == 0:
			print("There are no more cards in the Stock pile!")
			return False

		if len(self.deck) == 0:
			self.waste.reverse()
			self.deck = self.waste.copy()
			self.waste.clear()

		self.waste.append(self.deck.pop())
		return True

	def pop_waste_card(self):
		""" Removes a card from the Waste pile. """
		if len(self.waste) > 0:
			return self.waste.pop()

	def getWaste(self):
		""" Retrieves the top card of the Waste pile. """
		if len(self.waste) > 0:
			return self.waste[-1]
		else:
			return "empty"

	def getStock(self):
		""" Returns a string of the number of cards in the stock. """
		if len(self.deck) > 0:
			return str(len(self.deck)) + " card(s)"
		else:
			return "empty"

class Foundation():

	def __init__(self):
		self.foundation_stacks = {"club":[], "heart":[], "spade":[], "diam":[]}

	def addCard(self, card):
		""" Returns True if a card is successfully added to the Foundation,
			otherwise, returns False. """
		stack = self.foundation_stacks[card.suit]
		if len(stack) == 0:
			if card.value == 1:
				stack.append(card)
				return True
			else:
				print('Error! Card Value Invalid for Foundation')
				return False
		elif stack[-1].isBelow(card):
			stack.append(card)
			return True
		else:
			print('Error! Card Value Invalid for Foundation')
			return False

	def getTopCard(self, suit):
		""" Return the top card of a foundation pile. If the pile
			is empty, return the letter of the suit."""
		stack = self.foundation_stacks[suit]
		if len(stack) == 0:
			return suit[0].upper()
		else:
			return self.foundation_stacks[suit][-1]

	def gameWon(self):
		""" Returns whether the user has won the game. """
		for suit, stack in self.foundation_stacks.items():
			if len(stack) == 0:
				return False
			card = stack[-1]
			if card.value != 13:
				return False
		return True



class Game:
	def __init__(self):
		self.d = Deck()
		self.t = Tableau([self.d.deal_cards(x) for x in range(1,8)])
		self.f = Foundation()
		self.sw = StockWaste(self.d.deal_cards(24))

		self.moves = 0
		self.score = 0
		self.start_time = time.time()
		self.end_time = None
		self.final_score = 0

		# print("\n" + BREAK_STRING)
		# print("Welcome to Danny's Solitaire!\n")
		# self.printValidCommands()
		# self.printTable()

	def getFinalMetrics(self):
		self.end_time = time.time()
		self.game_duration = self.end_time - self.start_time
		if self.gameWon():
			time_penalty = int(game_duration % 10)
			self.final_score = self.score - time_penalty

		return self.final_score, self.moves, self.game_duration

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



	def takeTurn(self, command):

		if command == "mv":
			if self.sw.stock_to_waste():
				self.moves += 1

		elif command == "wf":
			if self.f.addCard(self.sw.getWaste()):
				self.sw.pop_waste_card()
				self.score += 10
				self.moves += 1

			else:
				print("Error! No card could be moved from the Waste to the Foundation.")
		elif "wt" in command and len(command) == 3:
			try:
				col = int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')
			else:
				if self.t.waste_to_tableau(self.sw, col):
					self.score += 5
					self.moves += 1

				else:
					print("Error! No card could be moved from the Waste to the Tableau column.")
		elif "tf" in command and len(command) == 3:
			try:
				col = int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')
			else:
				if self.t.tableau_to_foundation(self.f, col):
					self.score += 10
					self.moves += 1

				else:
					print("Error! No card could be moved from the Tableau column to the Foundation.")
		elif "tt" in command and len(command) == 4:
			try:
				c1, c2 = int(command[-2]) - 1, int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')
			else:
				if self.t.tableau_to_tableau(c1, c2):
					self.score += 5
					self.moves += 1
				else:
					print("Error! No card could be moved from that Tableau column.")



		else:
			print('Error! Not a Valid Command')

		self.printTable()



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
			game.takeTurn(command)
		else:
			print("Sorry, that is not a valid command.")

	if game.gameWon():
		print("Congratulations! You've won!")

	final_score,num_moves, game_duration = game.getFinalMetrics()
 
	print(f"Final Score: {final_score} \nNum Moves: {num_moves} \nGame Duration: {game_duration} seconds ")
	new_line = f"{final_score},{num_moves},{game_duration}"
	with open("runs.log","a") as a_file:
		a_file.write("\n")
		a_file.write(new_line)


def gameAuto():
	game = Game()
	game.printValidCommands()
	game.printTable()
	#Turn Up the First Deck Card First (#4)
	game.takeTurn("mv")
	game.printTable()

	while not game.gameWon():
		possible_moves = []


	# Play the Ace or Two (#7)
		# Check if there is an Ace or 2 in the Waste Pile and Play it
		if game.sw.getWaste().value == 1 or game.sw.getWaste().value == 2:
			game.takeTurn("wf")
			game.printTable()
		# Check if there is an Ace or 2 in the Tableau Piles and Play it
		game.printTable()
		print(game.t.flipped)
		print(game.t.unflipped)
		raise('stp')


		# Expose Large Stacks First (#1)
			# Get length of each Tableau, Loop in that order
			# For Each Loop Run
				# Find all moves that can be moved
					# If you can expose a new card add 2 points
					# If can open a spot, check if any kings are available
						# if yes add 3 points
						# else add 0 points

		# Check if we can move any card from waste pile to tableau

		# Move any King to Open Spot (#2)
			# If only 1 king can be moved to it and end turn
			# Else Consider what Jack and Queens are exposed
				#Check exposed tableaus, if any of them start with a queen, prioritize that king












		#Generate All Possible Moves




if __name__ == "__main__":

	gameManual()
	# gameAuto()
