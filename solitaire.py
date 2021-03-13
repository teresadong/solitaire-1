import re
from game_elements import Game
import operator
import itertools
from collections import OrderedDict

class Strategy:
	def __init__(self,rule_order,col_order,verbose=False):
		self.col_order = col_order
		self.rule_order = rule_order
		self.verbose=verbose
		self.rule_dict = {1: self.moveTableauToFoundation, 
					2: self.moveWasteToFoundation, 
					3: self.fillOpenWithKings,
					4: self.addWasteToTableau,
					5: self.moveCardsToExpose}

	def setGame(self,game):
		self.game=game

	def orderedRuleDict(self,rule_order):
		ordered_rules = OrderedDict.fromkeys(rule_order)
		for key in ordered_rules:
			ordered_rules[key]=self.rule_dict[key]

		return ordered_rules					

	def moveTableauToFoundation(self):
		#Check if can move any Tableau Cards to Foundation
		for col_index in self.col_order:
			column_cards = self.game.t.flipped[col_index]			
			if len(column_cards)>0:
				command = f"tf{col_index+1}"
				if self.game.takeTurn(command):
					if self.verbose:
						print(command)
					return True	
		return False

	def moveWasteToFoundation(self):
		# Check if I can move any Waste to Foundation
		if self.game.takeTurn("wf"):
			if self.verbose:
				print("wf")
			return True	
	
		return False

	def fillOpenWithKings(self):
		# If there is an open tableau, move king to it:
		for col_index in self.col_order:
			if len(self.game.t.flipped[col_index])==0:
				#Check if we can move from any Tableau to Foundation
				for col_index2 in self.col_order: 
					if col_index != col_index2:
						# Only move King if its part of a pile with Unexposed cards (Don't want to move king from one blank pile to other)
						if len(self.game.t.flipped[col_index2]) > 0 and len(self.game.t.unflipped[col_index2])>0 and self.game.t.flipped[col_index2][0].value == 13:
							command = f"tt{col_index2+1}{col_index+1}"
							if self.game.takeTurn(command):
								if self.verbose:
									print(command)
								return True


				#Check if we can move any king from waste to tableau
				if self.game.sw.getWaste()!="empty":
					if self.game.takeTurn(f"wt{col_index+1}"):
						if self.verbose:
							print(f"wt{col_index+1}")	
						return True 

		return False

	def addWasteToTableau(self):
		# Add Waste Cards to Tableau
		for col_index in self.col_order:
			column_cards = self.game.t.flipped[col_index]			
			if len(column_cards)>0:
				# Make sure Waste is not Empty
				if self.game.sw.getWaste()!="empty":    
					if self.game.takeTurn(f"wt{col_index+1}"):
						if self.verbose:
							print(f"wt{col_index+1}")
						return True
		return False

	def moveCardsToExpose(self):

		# Only Move Cards from Pile 1 to Pile 2 if Can Expose New Cards
		for p1_index in self.col_order:			
			if len(self.game.t.flipped[p1_index])>0:
				for p2_index in self.col_order:
					if p1_index != p2_index and len(self.game.t.flipped[p2_index])>0:
						# Move only if the last card in Pile 2 Flipped can be attached to first card for Pile 1 Fixed
						if self.game.t.flipped[p2_index][-1].canAttach(self.game.t.flipped[p1_index][0]):
							command = f"tt{p1_index+1}{p2_index+1}"
							if self.game.takeTurn(command):
									if self.verbose:
										print(command)	
									return True
		return False






class Simulation:
	def __init__(self,output_log,num_runs=100,max_turns=100,verbose=False):
		self.output_log=output_log
		self.verbose = verbose
		self.num_runs=num_runs
		self.max_turns=max_turns
		

		with open(self.output_log,"w") as a_file:
			new_line = "score,num_moves,game_duration,did_win"
			a_file.write(new_line)


	def simulateRulePerm(self,strategy):
		self.num_turns +=1

		#Always make sure 1 card from the deck is visible
		if self.game.sw.getWaste() == "empty":
			if self.game.takeTurn("mv"):
				if self.verbose:
					print("mv")
				return True

		rule_dict = strategy.orderedRuleDict(rule_order)
	
		for rule in rule_dict:
			if rule_dict[rule]():
				return True

		return False

	def basicAuto(self, strategy):
		if self.game.gameWon():
			return False

		turnResult = self.simulateRulePerm(strategy)
		if self.verbose:
			self.game.printTable()

		if turnResult:
			self.basicAuto(strategy)

		else: 
			if self.num_turns < self.max_turns:
				#End draw from deck 
				self.game.takeTurn("mv")
				return self.basicAuto(strategy)




	def runManual(self):
		self.game = Game(verbose=self.verbose)
		self.game.printValidCommands()
		self.game.printTable()

		while not self.game.gameWon():
			command = input("Enter a command (type 'h' for help): ")
			command = command.lower().replace(" ", "")
			if command == "h":
				self.game.printValidCommands()
			elif command == "q":
				print("Game exited.")
				break
			elif re.match("|".join(['mv','wf','wt','tf','tt']), command):
				self.game.takeTurn(command)
				self.game.printTable()
			else:
				print("Sorry, that is not a valid command.")


		if self.game.gameWon():
			print("Congratulations! You've won!")

		score,num_moves, game_duration, did_win = self.game.getFinalMetrics()
		print(f"Final Score: {score} \nNum Moves: {num_moves} \nGame Duration: {game_duration} seconds")
		
		self.outputToLog()

	def outputToLog(self):
		score,num_moves, game_duration, did_win = self.game.getFinalMetrics()
		new_line = f"{score},{num_moves},{game_duration},{did_win}"
		with open(self.output_log,"a") as a_file:
			a_file.write("\n")
			a_file.write(new_line)

	def runAuto(self,strategy):
		for i in range(self.num_runs):
			# For Each Run, Create a New Game and Reset Numb Terms
			self.num_turns=0
			self.game = Game(verbose=self.verbose)
			strategy.setGame(self.game)

			self.basicAuto(strategy)
			self.outputToLog()


if __name__ == "__main__":
	# Default is Manual
	# simulation = Simulation('runs_manual.log','manual',verbose=True)

	# Basic
	rule_order=list(range(1,6))
	col_order=list(range(7))

	simulation = Simulation('logs/runs_auto_basic_1000_300_1235.log',num_runs=1000,max_turns=300)

	# Create a Strategy Object that specifies Rule Order and Column Order
	strategy = Strategy(rule_order=rule_order,col_order=col_order,verbose=simulation.verbose)

	simulation.runAuto(strategy)

	# Basic Reverse
	rule_order=range(5,0,-1)
	col_order=range(7)
	simulation = Simulation('logs/runs_auto_basic_1000_300_54321.log',num_runs=1000,max_turns=300)

	# Create a Strategy Object that specifies Rule Order and Column Order
	strategy = Strategy(rule_order=rule_order,col_order=col_order,verbose=simulation.verbose)

	simulation.runAuto(strategy)


	# simulation = Simulation('logs/runs_auto_basic_300_300.log','basic',num_runs=300,max_turns=300,verbose=False)
	# simulation = Simulation('logs/runs_auto_basic_500_500.log','basic',num_runs=500,max_turns=500,verbose=False)