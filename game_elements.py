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