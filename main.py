import pygame

import random
import argparse
from datetime import datetime

from gameboard import Board, CardType
from embedding_agent import EmbeddingAgent
from wordnet_agent import WordNetAgent
from codenames import Codenames, Phase

# -------------------------------- Constants -------------------------------- #

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

# Input area
INPUT_FONT_SIZE = 30
CLUE_INSTRUCTIONS = "Enter a clue and the number of words it applies to:"
RED_REVEAL_INSTRUCTIONS = "Enter the word of a red card to reveal:"
INPUT_HEIGHT = (1 / 5) * (HEIGHT - 2 * MARGIN)
INSTRUCTION_Y_POS = HEIGHT - MARGIN - (2 / 3) * INPUT_HEIGHT
INPUT_Y_POS = HEIGHT - MARGIN - (1 / 3) * INPUT_HEIGHT

# Other
LOG_FILENAME = "log.txt"
BLACK = (0, 0, 0)
FPS = 20

# ---------------------------------- Setup ---------------------------------- #

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-m",
    "--model",
    default="wordnet",
    choices=["embedding", "wordnet"],
    help="The model to use for the agent",
)
args = parser.parse_args()

# Initialize the pygame window and clock
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Codenames")
clock = pygame.time.Clock()

# Load the Codenames game words
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Randomly sample 25 words
words = random.sample(game_words, 25)

# Select the agent
if args.model == "wordnet":
    agent = WordNetAgent("lexemes_distributions.wnkey.txt")
elif args.model == "embedding":
    agent = EmbeddingAgent("en_core_web_lg")
else:
    raise ValueError("Invalid model")

# Initialize the game
agent = EmbeddingAgent("en_core_web_lg")
board = Board(words)
game = Codenames(board, agent)

# Create the log text file if it doesn't exist
with open(LOG_FILENAME, "a") as f:
    f.write(f"{'-' * 25} NEW GAME {'-' * 25}\n\n")
    f.write(f"Model: {args.model}\n")
    f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

# -------------------------------- Functions -------------------------------- #

# ------ Display ------ #


def draw_window(user_text):
    """
    Draw the elements in the game window.
    :param user_text: text entered by the user
    """
    window.fill(BACKGROUND_COLOUR)
    draw_board()
    draw_input_area(user_text)
    pygame.display.update()


def draw_board():
    """
    Draw the board.
    """

    # Starting point defined by the top left corner of the board
    left = MARGIN
    top = MARGIN

    # Get the list of cards
    cards = game.board.cards

    # Draw each card
    for i in range(5):
        for j in range(5):
            # Get the card information
            card = cards[i * 5 + j]
            card_color = CARD_COLOURS[card.type]
            card_text = card.word.upper()
            card_rect = pygame.Rect(left, top, CARD_WIDTH, CARD_HEIGHT)

            # Draw the card rectangle in the appropriate colour
            pygame.draw.rect(window, card_color, card_rect)

            # Draw the card text in the middle of the card if the card is revealed
            if not card.revealed:
                draw_text(
                    window,
                    card_text,
                    CARD_FONT_SIZE,
                    left + CARD_WIDTH / 2,
                    top + CARD_HEIGHT / 2,
                )

            # Update the left coordinate for the next card
            left += CARD_WIDTH + CARD_SPACING

        # Reset the left coordinate and update the top coordinate for the next row
        left = MARGIN
        top += CARD_HEIGHT + CARD_SPACING


def draw_input_area(user_text):
    """
    Draw the input area.
    :param user_text: text entered by the user
    """

    # Get the instructions to display depending on the game state
    if game.game_over:
        instruction = game.game_over_message
    elif game.phase == Phase.CLUE:
        instruction = CLUE_INSTRUCTIONS
    elif game.phase == Phase.RED_REVEAL:
        instruction = RED_REVEAL_INSTRUCTIONS

    # Draw the instructions
    draw_text(window, instruction, INPUT_FONT_SIZE, WIDTH / 2, INSTRUCTION_Y_POS)

    # Draw the user text
    draw_text(window, user_text + "|", INPUT_FONT_SIZE, WIDTH / 2, INPUT_Y_POS)


def draw_text(surf, text, size, x, y):
    """
    Draw text on the screen.
    :param surf: surface to draw on
    :param text: text to draw
    :param size: font size
    :param x: x coordinate (center)
    :param y: y coordinate (center)
    :return: None
    """
    font = pygame.font.Font(pygame.font.match_font("arial"), size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


# ------ Logic ------ #


def handle_input(event, user_text):
    """
    Handle the user input.
    :param event: event to handle
    :param user_text: text entered by the user
    :return: updated user text
    """

    if event.key == pygame.K_BACKSPACE:
        # Remove the last character from the user text
        user_text = user_text[:-1]

    elif event.key == pygame.K_RETURN:
        # Handle the user input depending on the game phase
        if valid_input(user_text):
            handle_phase(user_text)
            game.next_phase()
            user_text = ""
    else:
        # Add the character to the user text
        user_text += event.unicode

    return user_text


def valid_input(user_text):
    """
    Check if the user input is valid for the current game phase.
    :param user_text: text entered by the user
    :return: True if the user input is valid, False otherwise
    """
    if game.phase == Phase.CLUE:
        return game.valid_clue_input(user_text)
    elif game.phase == Phase.RED_REVEAL:
        return game.valid_red_reveal_input(user_text)


def handle_phase(user_text):
    """
    Handle the user input depending on the game phase.
    :param user_text: text entered by the user
    """
    if game.phase == Phase.CLUE:
        handle_clue_phase(user_text)
    elif game.phase == Phase.RED_REVEAL:
        handle_red_reveal_phase(user_text)


def handle_clue_phase(user_text):
    """
    Handle the user input during the clue phase.
    :param user_text: text entered by the user
    """
    # Get the clue and number of words from the user input
    user_text = user_text.strip()
    user_text = user_text.lower()
    split_text = user_text.split()
    clue, num_words = split_text[0], int(split_text[1])

    # Get the guesses from the agent
    guesses = game.agent.guess(clue, num_words)

    # Log the clue and guesses
    log(f"{game.board.get_display_string()}\n\n")
    log(f"Clue: {clue} {num_words}\n\n")
    log(f"Guesses: {guesses}\n\n")

    #  Apply the guesses to the board
    game.make_contact(guesses)


def handle_red_reveal_phase(user_text):
    """
    Handle the user input during the red reveal phase.
    :param user_text: text entered by the user
    """
    # Get the word from the user input
    user_text = user_text.strip()
    word = user_text.lower()

    # Log the chosen word
    log(f"Red reveal: {word}\n\n")

    # Reveal the word on the board
    game.board.reveal(word)

    # Check if the game is over
    game.check_win()

    # Update the agent's knowledge of the board.
    game.update_agent()


def handle_endgame_input(event):
    """
    Handle the user input if the game is over. If the user presses the 'y' key,
    reset the game. If the user presses the 'n' key, quit the game.
    :param event: event to handle
    :return: boolean specifying whether the game should continue or not
    """

    # If the user presses the 'n' key, quit the game
    if event.key == pygame.K_n:
        log(f"{game.game_over_message}\n\n")
        return False

    # If the user presses the 'y' key, reset the game
    if event.key == pygame.K_y:
        log(f"{game.game_over_message}\n\n")
        reset_game(game)

    return True


def reset_game(game):
    """
    Reset the game to the initial state.
    """
    # Randomly sample 25 words
    words = random.sample(game_words, 25)

    # Initialize and reset the game elements
    board = Board(words)
    game.board = board
    game.update_agent()
    game.phase = Phase.CLUE
    game.game_over = False
    game.game_over_message = None

    # Log start of new game
    log(f"{'-' * 25} NEW GAME {'-' * 25}\n\n")
    log(f"Model: {args.model}\n")
    log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")


def log(string):
    """
    Print the string to the terminal and write it to the log file.
    :param string: string to log
    """
    # Print the string to the terminal
    print(string)

    # Write the string to the log file
    with open(LOG_FILENAME, "a") as f:
        f.write(string)


# -------------------------------- Game Loop -------------------------------- #


def main():
    """
    Main game loop.
    """
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

            # Handle input typed by the user
            if event.type == pygame.KEYDOWN:
                # Handle end-game input
                if game.game_over:
                    running = handle_endgame_input(event)
                    user_text = ""
                else:
                    # Handle in-game input
                    user_text = handle_input(event, user_text)

        # Draw the game elements
        draw_window(user_text)

    pygame.quit()


if __name__ == "__main__":
    main()
