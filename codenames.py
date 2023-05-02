import random

from gameboard import Board, CardType
from embedding_agent import EmbeddingAgent
from wordnet_agent import WordNetAgent


class Codenames:
    def __init__(self, board, agent):
        self.board = board
        self.agent = agent
        self.agent.load_words(board.unrevealed_words())

        # Bonus weighting for unrevealed neutral cards
        self.neutral_weighting = 0.2

    def play(self):
        """
        The main game loop for Codenames with 2 players. You always play as the
        blue team. See https://czechgames.com/files/rules/codenames-rules-en.pdf
        for details.
        """
        while True:
            self.board.display_in_terminal()
            clue, num_words = self.receive_clue()
            guesses = self.agent.guess(clue, num_words)
            self.make_contact(guesses)
            self.board.display_in_terminal()
            self.choose_red_card()
            self.agent.load_words(self.board.unrevealed_words())

    def receive_clue(self):
        """
        Receive the clue and number of words from the spymaster. The clue must
        be a single word and cannot be a word on the board. The number of words
        must be a positive integer.
        :return: tuple of clue and number of words
        """
        # Receive the clue from the spymaster
        while True:
            clue = input("Enter the clue: ")
            clue = clue.lower().strip()

            # Clue must be a single word
            if " " in clue:
                print("Clue must be a single word.")
                continue

            # Clue must not be a word on the board
            if clue in self.board.unrevealed_words():
                print("Clue cannot be a word on the board.")
                continue

            break

        # Receive the number of words the clue applies to
        while True:
            num_words = input("Enter the number of words: ")

            # Number must be an integer
            try:
                num_words = int(num_words)
            except ValueError:
                print("Please enter a positive integer.")
                continue

            # Number must be positive
            if num_words <= 0:
                print("Please enter a positive integer.")
                continue

            break

        return (clue, num_words)

    def make_contact(self, guesses):
        """
        Iterate through the guesses, revealing cards until the game is over or
        a non-blue card is revealed.
        :param guesses: list of words to guess in (descending order of confidence)
        """
        for guess in guesses:
            type = self.board.reveal(guess)

            self.check_win()

            if type != CardType.BLUE:
                break

    def choose_red_card(self):
        """
        Choose a red card on the board to reveal.
        """
        while True:
            word = input("Enter a red card to reveal: ")
            word = word.lower()

            is_red = self.board.card_type(word) == CardType.RED
            is_unrevealed = word in self.board.unrevealed_words()

            if not (is_red and is_unrevealed):
                print("Invalid word.")
                continue

            self.board.reveal(word)
            self.check_win()
            break

    def check_win(self):
        """
        Check if the game is over and exit if it is. The game is over if all
        blue cards are revealed, all red cards are revealed, or the assassin
        is revealed.
        """
        # Blue team wins
        if self.board.all_type_revealed(CardType.BLUE):
            self.board.display_in_terminal()
            print(f"You win! Your final score is {self.score()}")
            exit(0)

        # Red team wins
        if self.board.all_type_revealed(CardType.RED):
            self.board.display_in_terminal()
            print("You lose! Red team wins.")
            exit(0)

        # Assassin revealed
        if self.board.all_type_revealed(CardType.ASSASSIN):
            self.board.display_in_terminal()
            print("You lose! Assassin revealed.")
            exit(0)

    def score(self):
        """
        Calculate the score for the blue team. The score is the number of
        unrevealed red cards plus a bonus for each unrevealed neutral card.
        :return: score for the blue team
        """

        num_unrevealed_red = self.board.num_type_unrevealed(CardType.RED)
        num_unrevealed_neutral = self.board.num_type_unrevealed(CardType.NEUTRAL)

        return num_unrevealed_red + self.neutral_weighting * num_unrevealed_neutral


# ---------------------------------- MAIN ----------------------------------- #

if __name__ == "__main__":
    # Load the Codenames game words
    with open("game_words.txt", "r") as f:
        game_words = f.read().splitlines()

    # Randomly sample 25 words
    words = random.sample(game_words, 25)

    # Initialize the game elements
    board = Board(words)
    embedding_agent = EmbeddingAgent("en_core_web_lg")
    game = Codenames(board, embedding_agent)

    # Play the game
    game.play()
