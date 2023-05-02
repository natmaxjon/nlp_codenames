import random

from gameboard import Board, CardType
from embedding_agent import EmbeddingAgent
from wordnet_agent import WordNetAgent

# ---------------------------------- SETUP ---------------------------------- #

# Load the Codenames game words
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Randomly sample 25 words
words = random.sample(game_words, 25)

# Initialize the game board
board = Board(words)

# Initialize the agents
embedding_agent = EmbeddingAgent("en_core_web_lg")
embedding_agent.load_words(words)

wordnet_agent = WordNetAgent("lexemes_distributions.wnkey.txt")
wordnet_agent.load_words(words)

# -------------------------------- GAME LOOP -------------------------------- #

while True:
    # Print the board
    board.display_in_terminal()

    # Receive the clue from the spymaster
    clue = input("Enter the clue: ")

    # Receive the number of words the clue applies to
    num_words = int(input("Enter the number of words: "))

    # Make a guess
    guesses = embedding_agent.guess(clue, num_words)
    print("Embedding:", guesses)
    print()

    # Apply guesses to the board
    for guess in guesses:
        type = board.reveal(guess)

        if type == CardType.BLUE:
            if board.is_all_revealed(CardType.BLUE):
                board.display_in_terminal()
                print("You win!")
                exit(0)
            continue
        elif type == CardType.RED:
            if board.is_all_revealed(CardType.RED):
                board.display_in_terminal()
                print("You lose!")
                exit(0)
            break
        elif type == CardType.NEUTRAL:
            break
        elif type == CardType.ASSASSIN:
            board.display_in_terminal()
            print("You lose!")
            exit(0)

    # Print the board
    board.display_in_terminal()
    
    # If there is only one red card left, the game is over
    if board.num_unrevealed(CardType.RED) == 1:
        board.display_in_terminal()
        print("You lose!")
        exit(0)

    # Choose a red card to reveal
    while True:
        word = input("Enter a red card to reveal: ")

        if board.card_type(word) == CardType.RED and word in board.unrevealed_words():
            board.reveal(word)
            break

    # Update the words considered by the agents
    embedding_agent.load_words(board.unrevealed_words())
    



# --------------------------------------------------------------------------- #







# for i in range(3):
#     # Receive the clue from the spymaster
#     clue = input("Enter the clue: ")

#     # Receive the number of words the clue applies to
#     num_words = int(input("Enter the number of words: "))

#     # Make a guess
#     guesses = embedding_agent.guess(clue, num_words)

#     # TODO: Temp
#     print("Embedding:", guesses)
#     print()

#     # Make a guess
#     guesses = wordnet_agent.guess(clue, num_words)

#     # TODO: Temp
#     print("WordNet:", guesses)
#     print()