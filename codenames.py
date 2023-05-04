import random
from enum import Enum

from gameboard import Board, CardType
from embedding_agent import EmbeddingAgent
from wordnet_agent import WordNetAgent

Phase = Enum("Phase", ["CLUE", "RED_REVEAL"])

class Codenames:
    def __init__(self, board, agent):
        self.board = board
        self.agent = agent
        self.update_agent()
        self.phase = Phase.CLUE
        self.game_over = False
        self.game_over_message = None

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
            self.update_agent()
    
    def update_agent(self):
        """
        Update the agent's knowledge of the board.
        """
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
    
    def valid_clue_input(self, user_text):
        user_text = user_text.strip()
        user_text = user_text.lower()
        split_text = user_text.split()

        # Check if the user entered two words
        if len(split_text) != 2:
            return False

        clue = split_text[0]
        num_words = split_text[1]

        # Check if the clue is a word
        if not clue.isalpha():
            return False
        
        # Check if the clue is a word on the board
        if clue in self.board.unrevealed_words():
            return False

        # Check if the number is an integer
        try:
            num_words = int(num_words)
        except ValueError:
            return False
        
        # Check if the number is positive
        if num_words <= 0:
            return False
    
        return True
    

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

    def valid_red_reveal_input(self, user_text):
        """
        Check if the input is a valid red card to reveal.
        :param word: word to check
        :return: True if the word is a valid red card to reveal, False otherwise
        """
        user_text = user_text.strip()
        user_text = user_text.lower()

        # Check if the user entered a single word
        if len(user_text.split()) != 1:
            return False

        # Check if the user entered a word
        if not user_text.isalpha():
            return False
        
        is_red = self.board.card_type(user_text) == CardType.RED
        is_unrevealed = user_text in self.board.unrevealed_words()

        # Check if the word is a valid red card to reveal
        if not (is_red and is_unrevealed):
            return False
        
        return True

    def next_phase(self):
        """
        Advance to the next phase of the game.
        """
        if self.phase == Phase.CLUE:
            self.phase = Phase.RED_REVEAL
        elif self.phase == Phase.RED_REVEAL:
            self.phase = Phase.CLUE

    def check_win(self):

        # Blue team wins
        if self.board.all_type_revealed(CardType.BLUE):
            self.game_over = True
            self.game_over_message = f"You win! Your final score is {self.score()}. Play again? (y/n)"

        # Red team wins
        if self.board.all_type_revealed(CardType.RED):
            self.game_over = True
            self.game_over_message = "You lose! Red team revealed all their cards. Play again? (y/n)"

        # Assassin revealed
        if self.board.all_type_revealed(CardType.ASSASSIN):
            self.game_over = True
            self.game_over_message = "You lose! You contacted the assassin. Play again? (y/n)"

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
