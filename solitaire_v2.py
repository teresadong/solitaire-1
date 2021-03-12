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

		self.num_turns = 0
		self.moves = 0
		self.score = 0
		self.start_time = time.time()
		self.end_time = None
		self.successful_moves = []

	def getFinalMetrics(self):
		self.end_time = time.time()
		self.game_duration = self.end_time - self.start_time

		return self.score, self.moves, self.game_duration

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
		turn_success = False


		if command == "mv":
			if self.sw.stock_to_waste():
				turn_success = True

		elif command == "wf":
			if self.f.addCard(self.sw.getWaste()):
				self.sw.pop_waste_card()
				self.score += 10
				turn_success = True

			else:
				print("Error! No card could be moved from the Waste to the Foundation.")


		elif "wt" in command and len(command) == 3:
			try:
				col = int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')

			else:
				if col < 8:
					if self.t.waste_to_tableau(self.sw, col):
						self.score += 5
						turn_success = True

					else:
						print("Error! No card could be moved from the Waste to the Tableau column.")

				else:
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
						print("Error! No card could be moved from the Tableau column to the Foundation.")
						print(command)

				else:
					print("Error: Invalid Tablue Value")


		elif "tt" in command and len(command) == 4:
			try:
				c1, c2 = int(command[-2]) - 1, int(command[-1]) - 1
			except ValueError:
				print('Error! Invalid Tableau Value')


			else:
				if c1 < 8 and c2 < 8:
					if self.t.tableau_to_tableau(c1, c2):
						self.score += 5
						turn_success = True

					else:
						print("Error! No card could be moved from that Tableau column.")

				else:
					print("Error! Invalid Tableau Value")




		else:
			print('Error! Not a Valid Command')


		if turn_success == True:
			self.moves += 1
			print(f"Success! {command}")
			self.successful_moves.append(command)

		return turn_success

	def checkCardOrder(self,higherCard,lowerCard):
		suitsDifferent = higherCard.isOppositeSuit(lowerCard)
		valueConsecutive = lowerCard.isBelow(higherCard)
		return suitsDifferent and valueConsecutive

	def simulateTurn(self,verbose=False):
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

			# if its an open tableau, move king to it:
		for col_index in range(7):
			column_cards = self.t.flipped[col_index]
			if len(column_cards)==0:
				#Check if we can move from any Tableau to Foundation
				for col_index2 in range(7): 
					if col_index != col_index2:
						column_cards2 = self.t.flipped[col_index2]
						if len(column_cards2) > 0 and len(self.t.unflipped[col_index2])>0 and column_cards2[0].value == 13:
							command = f"tt{col_index2+1}{col_index+1}"
							if self.takeTurn(command):
								if verbose:
									print(command)
								return True


				#Check if we can move any king from waste to tableau
				if self.takeTurn(f"wt{col_index+1}"):
					if verbose:
						print(f"wt{col_index+1}")	
					return True 


		# Add Waste Cards to Tableau
		for col_index in range(7):
			column_cards = self.t.flipped[col_index]			
			if len(column_cards)>0:
				# Check if I can add any Waste to Tableau
				if self.takeTurn(f"wt{col_index+1}"):
					if verbose:
						print(f"wt{col_index+1}")
					return True

		# Move Cards Across Tableaus	
		for p1_index in range(7):
			pile1_flipped_cards = self.t.flipped[p1_index]
			pile1_unflipped_cards = self.t.unflipped[p1_index]
			
			
			if len(self.t.flipped[p1_index])>0:
				for p2_index in range(7):

					if p1_index != p2_index and len(self.t.flipped[p2_index])>0:

						if self.t.flipped[p2_index][-1].canAttach(self.t.flipped[p1_index][0]):
							command = f"tt{p1_index+1}{p2_index+1}"
							if self.takeTurn(command):
									if verbose:
										print(command)	
									return True
							# else:
							# 	print("Pile 1")
							# 	for card in self.t.flipped[p1_index]:
							# 		print(f"{card.suit}{card.value}")
							# 	print("Pile 2")
							# 	for card in self.t.flipped[p2_index]:
							# 		print(f"{card.suit}{card.value}")	
										# p1_length_flipped = len(self.t.flipped[p1_index])
							# p1_length_unflipped = len(self.t.unflipped[p1_index])
							# p1_length_total = p1_length_flipped+p1_length_unflipped

							
							# if p1_length_flipped ==  p1_length_total:
							# 	command = f"tt{p2_index+1}{p1_index+1}"
							# 	if self.takeTurn(command):
							# 		if verbose:
							# 			print(command)
							# 		return True

							# elif p1_length_total-p1_length_flipped == p1_length_unflipped:
							# 	command = f"tt{p2_index+1}{p1_index+1}"
							# 	if self.takeTurn(command):
							# 		if verbose:
							# 			print(command)	
							# 		return True
    
							# else: 
							# 	print(p1_length_total)
							# 	print(p1_length_flipped)
							# 	print(p1_length_unflipped)       
							# 	print("Pile 1")
							# 	for card in self.t.flipped[p1_index]:
							# 		print(f"{card.suit}{card.value}")
							# 	print("Pile 2")
							# 	for card in self.t.flipped[p2_index]:
							# 		print(f"{card.suit}{card.value}")	
							# 	raise('stp')

						# command = f"tt{p2_index+1}{p1_index+1}"
						# if self.takeTurn(command):
						# 	if verbose:
						# 		print(command)
						# 	raise('stp')

						# 	return True	
						# for transfer_cards_size in range(1,len(self.t.flipped[p1_index])+1):
						# 	cards_to_transfer = self.t.flipped[p1_index][:transfer_cards_size]

						# 	if self.checkCardOrder(pile2_flipped_cards[-1],cards_to_transfer[0]):
								# print(pile1_downcard_count)
								# print(pile2_downcard_count)
								# if len(pile2_flipped_cards)>1:
								# 	print("Pile 1")
								# 	for card in pile1_flipped_cards:
								# 		print(f"{card.suit}{card.value}")
								# 	print("Pile 2")
								# 	for card in pile2_flipped_cards:
								# 		print(f"{card.suit}{card.value}")
								# 	print("Card To Transfer")
								# 	for card in cards_to_transfer:
								# 		print(f"{card.suit}{card.value}")
								# 	self.printTable()
								# 	raise('stp')  

								# if len(cards_to_transfer)==len(pile1_flipped_cards):

									
								# # pile1_downcard_count = len(self.t.unflipped[p1_index])
								# # pile2_downcard_count = len(self.t.unflipped[p2_index])
								# # if pile2_downcard_count < pile1_downcard_count:
								# # 	if len(cards_to_transfer)> 2:
								# # 		print(pile1_downcard_count)
								# # 		print(pile2_downcard_count)
								# # 		print("Pile 1")
								# # 		for card in pile1_flipped_cards:
								# # 			print(f"{card.suit}{card.value}")
								# # 		print("Pile 2")
								# # 		for card in pile2_flipped_cards:
								# # 			print(f"{card.suit}{card.value}")
								# # 		print("Card To Transfer")
								# # 		for card in cards_to_transfer:
								# # 			print(f"{card.suit}{card.value}")
								# # 		self.printTable()
								# # 		raise('stp')  
            
								# 	#Transfer Pile 1 to Pile 2
								# 	self.t.flipped[p2_index]
								# 	# [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
								# 	# pile1.cards = pile1.cards[transfer_cards_size:]
								# 	command = f"tt{p2_index+1}{p1_index+1}"
								# 	if self.takeTurn(command):
								# 		if verbose:
								# 			print(command)
								# 		return True									
            
								# 	# for card in pile1_flipped_cards:
								# 	# 	print(f"{card.suit}{card.value}")
								# 	# for card in pile2_flipped_cards:
								# 	# 	print(f"{card.suit}{card.value}")
								# 	# for card in cards_to_transfer:
								# 	# 	print(f"{card.suit}{card.value}")
								# 	# self.printTable()
								# 	# raise('stp')  
            
								# elif pile1_downcard_count==0 and len(cards_to_transfer) == (len(self.t.unflipped[p1_index])+len(self.t.flipped[p1_index])):
								# 	# [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
								# 	# pile1.cards = []
								# 	# if verbose:
								# 	# 	print("Moved {0} cards between piles: {1}".format(
								# 	# 		transfer_cards_size,
								# 	# 		", ".join([str(card) for card in cards_to_transfer])
								# 	# 													 ))

								# 	command = f"tt{p2_index+1}{p1_index+1}"
								# 	if self.takeTurn(command):
								# 		if verbose:
								# 			print(command)
								# 		return True	


		

		# # Play the Ace or Two (#7)
		# ## Check if there is an Ace in the Waste Pile and Play it
		# if self.sw.getWaste().value == 1:
		# 	if self.takeTurn("wf"):
		# 		if verbose:
		# 			print("wf")
		# 		return True

		# ## Check if there is a Two in the Waste Pile and Play it		
		# if self.sw.getWaste().value == 2:
		# 	suits = ["club", "heart", "spade", "diam"]
		# 	for i in suits:
		# 		if self.f.getTopCard(i)==self.sw.getWaste().suit == i:
		# 			if self.takeTurn("wf"):
		# 				if verbose:
		# 					print("wf")
		# 				return True

		# # Add Tableau to Foundation
		# for col_index in range(7):	

		# 	column_cards = self.t.flipped[col_index]

		# 	# if its an open tableau, move king to it:
		# 	if len(column_cards)==0:
		# 		#Check if we can move from any Tableau to Foundation
		# 		for col_index2 in range(7): 
		# 			if col_index != col_index2:
		# 				column_cards2 = self.t.flipped[col_index2]
		# 				if len(column_cards2) > 0 and column_cards2[0].value == "K":
		# 					command = f"tt{col_index2+1}{col_index+1}"
		# 					if self.takeTurn(command):
		# 						if verbose:
		# 							print(command)
		# 						return True

		# 		#Check if we can move any king from waste to tableau
		# 		if self.takeTurn(f"wt{col_index+1}"):
		# 			if verbose:
		# 				print(f"wt{col_index+1}")	
		# 			return True

		# # if its not an empty pile
		# for col_index in range(7):
		# 	column_cards = self.t.flipped[col_index]			
		# 	if len(column_cards)>0:
		# 		last_card = column_cards[-1]
		# 		first_card = column_cards[0]

		# 		# Check if there is an Ace in the Tableau Piles and Play it    
		# 		if last_card.value == 1:
		# 			command = f"tf{col_index+1}"
		# 			if self.takeTurn(command):
		# 				if verbose:
		# 					print(command)
		# 				return True

		# # if its not an empty pile
		# for col_index in range(7):
		# 	column_cards = self.t.flipped[col_index]			
		# 	if len(column_cards)>0:
		# 		# Check if there is a Two in the Tableau Piles and Play it    				
		# 		if last_card.value == 2:
		# 			suits = ["club", "heart", "spade", "diam"]
		# 			for card_suit in suits:
		# 				if self.f.getTopCard(card_suit)==last_card.suit == card_suit: 
		
		# 					command = f"tf{col_index+1}"
		# 					if self.TakeTurn(command):
		# 						print(command)
		# 					return True

		# for col_index in range(7):
		# 	column_cards = self.t.flipped[col_index]			
		# 	if len(column_cards)>0:
		# 		# Check if I can move any Tableau to Foundation
		# 		command = f"tf{col_index+1}"
		# 		if self.takeTurn(command):
		# 			if verbose:
		# 				print(command)
		# 			return True





		# for col_index in range(7):
		# 	column_cards = self.t.flipped[col_index]			
		# 	if len(column_cards)>0:
		# 		# Move around Cards in Play Piles
		# 		for col_index2 in range(7): 
		# 			if col_index != col_index2:
		# 				column_cards2 = self.t.flipped[col_index2]
		# 				if len(column_cards2) > 0:
		# 					command = f"tt{col_index2+1}{col_index+1}"
		# 					if self.takeTurn(command):
		# 						if verbose:
		# 							print(command)
		# 						return True

		return False


	def runAuto(self, verbose = False):

		turnResult = self.simulateTurn(verbose=verbose)
		self.printTable()

		if turnResult:
			self.runAuto(verbose=verbose)


		else: 
			# raise('stp')
			#End draw from deck 
			if self.sw.getStock()!="empty":

				self.takeTurn("mv")
				return self.runAuto(verbose=verbose)
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
			game.takeTurn(command)
		else:
			print("Sorry, that is not a valid command.")

	if game.gameWon():
		print("Congratulations! You've won!")

	score,num_moves, game_duration = game.getFinalMetrics()

	print(f"Final Score: {score} \nNum Moves: {num_moves} \nGame Duration: {game_duration} seconds ")
	new_line = f"{score},{num_moves},{game_duration}"
	with open("runs.log","a") as a_file:
		a_file.write("\n")
		a_file.write(new_line)






def gameAuto():
	game = Game()
	game.printValidCommands()
	game.printTable()

	game.runAuto()
	# while not game.gameWon():
	# 	if !game.simulateTurn(verbose=True):
	# 		game.takeTurn("mv")
	# 		print("mv")	
	
	# 	game.printTable()

	# print("\n".join(game.successful_moves))


if __name__ == "__main__":

	# gameManual()
	gameAuto()
