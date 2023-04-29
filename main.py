import random

from gameboard import CardType, Board

random.seed(11)

# Read the file game_words.txt
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Initialize the game board
words = random.sample(game_words, 25)

card_types = [CardType.BLUE]*9 + [CardType.RED]*8 + [CardType.NEUTRAL]*7 + [CardType.ASSASSIN]
random.shuffle(card_types)

board = Board(words, card_types)

board.display()

for word in words:
    board.guess(word)
    board.display()

    winner = board.check_winner()
    if winner:
        print(f"{winner.name} wins!")
        break

    if board.active_player == CardType.BLUE:
        board.active_player = CardType.RED
    else:
        board.active_player = CardType.BLUE
