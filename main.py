import pygame

import random

from gameboard import Board, CardType
from embedding_agent import EmbeddingAgent
from wordnet_agent import WordNetAgent
from codenames import Codenames, Phase

# --------------------------------------------------------------------------- #

# Screen
WIDTH = 1200
HEIGHT = 800
MARGIN = 20
BACKGROUND_COLOUR = (221, 182, 156)

# Board
BOARD_WIDTH = WIDTH - 2 * MARGIN
BOARD_HEIGHT = (4 / 5) * (HEIGHT - 2 * MARGIN)

# Cards
CARD_SPACING = MARGIN
CARD_WIDTH = (BOARD_WIDTH - 4 * CARD_SPACING) / 5
CARD_HEIGHT = (BOARD_HEIGHT - 4 * CARD_SPACING) / 5
CARD_FONT_SIZE = 20
CARD_COLOURS = {
    CardType.BLUE: (50, 110, 155),
    CardType.RED: (196, 48, 42),
    CardType.NEUTRAL: (245, 227, 198),
    CardType.ASSASSIN: (100, 100, 100),
}

# Other colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Other
FPS = 20

# Initialize pygame and create window
pygame.init()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Codenames")

# --------------------------------------------------------------------------- #
# --------- Setup --------- #

# Load the Codenames game words
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Randomly sample 25 words
words = random.sample(game_words, 25)

# Initialize the game elements
board = Board(words)
embedding_agent = EmbeddingAgent("en_core_web_lg")
game = Codenames(board, embedding_agent)

# --------- Other --------- #
clock = pygame.time.Clock()

# --------------------------------------------------------------------------- #


def draw_window(user_text):
    WINDOW.fill(BACKGROUND_COLOUR)
    draw_board()
    draw_text(WINDOW, user_text, 30, WIDTH / 2, HEIGHT - 50)
    pygame.display.update()


def draw_board():
    left = MARGIN
    top = MARGIN

    cards = game.board.cards

    for i in range(5):
        for j in range(5):
            # Draw the card
            card = cards[i * 5 + j]
            color = CARD_COLOURS[card.type]
            text = cards[i * 5 + j].word.upper()
            rect = pygame.Rect(left, top, CARD_WIDTH, CARD_HEIGHT)

            pygame.draw.rect(WINDOW, color, rect)

            if not card.revealed:
                draw_text(
                    WINDOW,
                    text,
                    CARD_FONT_SIZE,
                    left + CARD_WIDTH / 2,
                    top + CARD_HEIGHT / 2,
                )

            left += CARD_WIDTH + CARD_SPACING

        left = MARGIN
        top += CARD_HEIGHT + CARD_SPACING


def draw_text(surf, text, size, x, y):
    """
    Draw text on the screen.
    :param surf: surface to draw on
    :param text: text to draw
    :param size: font size
    :param x: x coordinate
    :param y: y coordinate
    :return: None
    """
    font = pygame.font.Font(pygame.font.match_font("arial"), size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


# --------------------------------------------------------------------------- #


def handle_input(event, user_text):
    if event.key == pygame.K_BACKSPACE:
        user_text = user_text[:-1]

    elif event.key == pygame.K_RETURN:
        if valid_input(user_text):
            handle_phase(user_text)
            game.next_phase()
            user_text = ""
    else:
        user_text += event.unicode

    return user_text

def valid_input(user_text):
    if game.phase == Phase.CLUE:
        return game.valid_clue_input(user_text)
    elif game.phase == Phase.RED_REVEAL:
        return game.valid_red_reveal_input(user_text)

def handle_phase(user_text):
    if game.phase == Phase.CLUE:
        handle_clue_phase(user_text)
    elif game.phase == Phase.RED_REVEAL:
        handle_red_reveal_phase(user_text)

def handle_clue_phase(user_text):
    user_text = user_text.strip()
    user_text = user_text.lower()
    split_text = user_text.split()

    clue, num_words  = split_text[0], int(split_text[1])
    guesses = game.agent.guess(clue, num_words)
    print(guesses)
    game.make_contact(guesses)

def handle_red_reveal_phase(user_text):
    user_text = user_text.strip()
    word = user_text.lower()
    game.board.reveal(word)
# --------------------------------------------------------------------------- #
# TODO: TEMP


# --------------------------------------------------------------------------- #


def main():
    # --------- Game Loop --------- #
    user_text = ""
    running = True
    while running:
        # Keep loop running at the right speed
        clock.tick(FPS)

        # Process input (events)
        for event in pygame.event.get():
            # Check for closing the window
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                user_text = handle_input(event, user_text)

        # Update

        # Draw / render
        draw_window(user_text)

    pygame.quit()


if __name__ == "__main__":
    main()
