import re
from game_elements import Game
import operator

class Strategy:
	def __init__(self,game,col_order,verbose=False):
		self.game=game
		self.col_order = col_order
		self.verbose=verbose

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
	def __init__(self,output_log,alg='manual',num_runs=100,max_turns=100,verbose=False):
		self.output_log=output_log
		self.runs = num_runs 
		self.max_turns=max_turns
		self.verbose = verbose

		with open(self.output_log,"a") as a_file:
			new_line = "score,num_moves,game_duration,did_win"
			a_file.write(new_line)



		if alg=="basic": 
			for i in range(num_runs):
				self.runAutoBasic()
		else:
			self.runManual()

	def simulateBasic(self):
		self.num_turns +=1

		strategy = Strategy(self.game,col_order=range(7),verbose=self.verbose)

		#Always make sure 1 card from the deck is visible
		if self.game.sw.getWaste() == "empty":
			if self.game.takeTurn("mv"):
				if self.verbose:
					print("mv")
				return True

		if strategy.moveTableauToFoundation():
			return True

		if strategy.moveWasteToFoundation():
			return True

		if strategy.fillOpenWithKings():
			return True

		if strategy.addWasteToTableau():
			return True

		if strategy.moveCardsToExpose():
			return True

		return False

	def basicAuto(self):
		if self.game.gameWon():
			return False

		turnResult =self.simulateBasic()
		if self.verbose:
			self.game.printTable()

		if turnResult:
			self.basicAuto()

		else: 
			if self.num_turns < self.max_turns:
				#End draw from deck 
				self.game.takeTurn("mv")
				return self.basicAuto()




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

	def runAutoBasic(self):
		# Num Turns Needs to Be Reset Each Run
		self.num_turns=0
		self.game = Game(verbose=self.verbose)
		self.basicAuto()
		self.outputToLog()


if __name__ == "__main__":
	#Default is Manual
	# simulation = Simulation('runs_manual.log','manual',verbose=True)

	simulation = Simulation('runs_auto_basic_100_100.log','basic',num_runs=100,max_turns=100,verbose=False)
	simulation = Simulation('runs_auto_basic_300_300.log','basic',num_runs=300,max_turns=300,verbose=False)
	simulation = Simulation('runs_auto_basic_500_500.log','basic',num_runs=500,max_turns=500,verbose=False)