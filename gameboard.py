from enum import Enum
import random

CardType = Enum("CardType", ["RED", "BLUE", "NEUTRAL", "ASSASSIN"])


class Card:
    def __init__(self, word, type):
        self.word = word
        self.type = type
        self.revealed = False

    def reveal(self):
        self.revealed = True


class Board:
    def __init__(self, words):
        assert len(words) == 25

        # Randomly assign card types (9 blue, 8 red, 7 neutral, 1 assassin)
        # Assumes blue team goes first
        types = (
            [CardType.BLUE] * 9
            + [CardType.RED] * 8
            + [CardType.NEUTRAL] * 7
            + [CardType.ASSASSIN]
        )
        random.shuffle(types)

        self.cards = [Card(word, type) for word, type in zip(words, types)]

    def reveal(self, word):
        """
        Reveal the card with the given word. Return the type of the card.
        """
        for card in self.cards:
            if card.word == word:
                card.reveal()
                return card.type

    def card_type(self, word):
        """
        Return the type of the card with the given word.
        """
        for card in self.cards:
            if card.word == word:
                return card.type

    def unrevealed_words(self):
        """
        Return a list of all unrevealed words on the board.
        """
        return [card.word for card in self.cards if not card.revealed]

    def all_type_revealed(self, card_type):
        """
        Return True if all cards of the given type are revealed, False otherwise.
        """
        return all(card.revealed for card in self.cards if card.type == card_type)

    def num_type_unrevealed(self, card_type):
        """
        Return the number of unrevealed cards of the given type.
        """
        return sum(
            1 for card in self.cards if card.type == card_type and not card.revealed
        )

    def get_display_string(self):
        """
        Return a string representation of the board.
        """
        string = "BLUE = () ; RED = [] ; NEUTRAL = {} ; ASSASSIN = <>\n"
        for idx, card in enumerate(self.cards):
            if idx % 5 == 0:
                string += "\n"

            card_str = "     " if card.revealed else card.word.upper()

            if card.type == CardType.BLUE:
                card_str = f"({card_str})"
            elif card.type == CardType.RED:
                card_str = f"[{card_str}]"
            elif card.type == CardType.NEUTRAL:
                card_str = f"{{{card_str}}}"
            elif card.type == CardType.ASSASSIN:
                card_str = f"<{card_str}>"

            string += f"{card_str: ^12}"

        return string
