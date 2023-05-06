from enum import Enum

from gameboard import CardType

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

    def update_agent(self):
        """
        Update the agent's knowledge of the board.
        """
        self.agent.load_words(self.board.unrevealed_words())

    def valid_clue_input(self, user_text):
        """
        Check if the user's input for the clue is valid.
        :param user_text: user's input for the clue
        :return: True if the input is valid, False otherwise
        """
        # Preprocess the user's input
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

    def valid_red_reveal_input(self, user_text):
        """
        Check if the input is a valid red card to reveal.
        :param word: word to check
        :return: True if the word is a valid red card to reveal, False otherwise
        """
        # Preprocess the user's input
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

    def check_win(self):
        # Blue team wins
        if self.board.all_type_revealed(CardType.BLUE):
            self.game_over = True
            self.game_over_message = (
                f"You win! Your final score is {self.score()}. Play again? (y/n)"
            )

        # Red team wins
        if self.board.all_type_revealed(CardType.RED):
            self.game_over = True
            self.game_over_message = (
                "You lose! Red team revealed all their cards. Play again? (y/n)"
            )

        # Assassin revealed
        if self.board.all_type_revealed(CardType.ASSASSIN):
            self.game_over = True
            self.game_over_message = (
                "You lose! You contacted the assassin. Play again? (y/n)"
            )

    def score(self):
        """
        Calculate the score for the blue team. The score is the number of
        unrevealed red cards plus a bonus for each unrevealed neutral card.
        :return: score for the blue team
        """

        num_unrevealed_red = self.board.num_type_unrevealed(CardType.RED)
        num_unrevealed_neutral = self.board.num_type_unrevealed(CardType.NEUTRAL)

        return num_unrevealed_red + self.neutral_weighting * num_unrevealed_neutral

    def next_phase(self):
        """
        Advance to the next phase of the game.
        """
        if self.phase == Phase.CLUE:
            self.phase = Phase.RED_REVEAL
        elif self.phase == Phase.RED_REVEAL:
            self.phase = Phase.CLUE
