from enum import Enum

CardType = Enum('CardType', ['RED', 'BLUE', 'NEUTRAL', 'ASSASSIN'])

class Card():
    def __init__(self, word, type):
        self.word = word
        self.type = type
        self.revealed = False
    
    def reveal(self):
        self.revealed = True

class Board():
    def __init__(self, words, types):
        self.cards = [Card(word, type) for word, type in zip(words, types)]
        self.active_player = CardType.BLUE
    
    def guess(self, word):
        for card in self.cards:
            if card.word == word:
                card.reveal()
                break
    
    def unrevealed_words(self):
        return [card.word for card in self.cards if not card.revealed]
    
    def check_winner(self):
        # If all red cards have been revealed, red wins
        if all(card.revealed for card in self.cards if card.type == CardType.RED):
            return CardType.RED
        
        # If all blue cards have been revealed, blue wins
        if all(card.revealed for card in self.cards if card.type == CardType.BLUE):
            return CardType.BLUE
        
        # If the assassin has been revealed, the other team wins
        if any(card.revealed for card in self.cards if card.type == CardType.ASSASSIN):
            if self.active_player == CardType.BLUE:
                return CardType.RED
            else:
                return CardType.BLUE
        
        return None

    def display(self):
        for idx, card in enumerate(self.cards):
            if idx % 5 == 0:
                print()
            
            if card.revealed:
                reveal_str = f"[ {card.type.name[0]} ]"
                print(f"{reveal_str : ^8}", end="")
            else:
                print(f"{card.word.upper() : ^8} ", end="")

        print("\n")
    
