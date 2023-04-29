import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic

import spacy

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

# -----------------------------------------------------------------------------

clue = "animal"
# num_words = 25

print(f"Clue: {clue}\n")

# -----------------------------------------------------------------------------


results1 = []
for word in words:
    for game_syn in wn.synsets(word, pos=wn.NOUN):
        for clue_syn in wn.synsets(clue, pos=wn.NOUN):
            results1.append(
                {
                    "word": word,
                    "syn": game_syn,
                    "clue_syn": clue_syn,
                    # "similarity": clue_syn.path_similarity(game_syn),
                    # "similarity": clue_syn.lch_similarity(game_syn),
                    "similarity": clue_syn.wup_similarity(game_syn),
                    # "similarity": clue_syn.res_similarity(game_syn, semcor_ic),
                }
            )

# Sort results by similarity
results1 = sorted(results1, key=lambda x: x["similarity"], reverse=True)

# List before processing
for result in results1[:5]:
    print(f"Similarity: {result['similarity']}")
    print(f"Game word: {result['word']}")
    print(f"Game syn: {result['syn']}:")
    print(result["syn"].definition())
    print(f"Clue syn: {result['clue_syn']}:")
    print(result["clue_syn"].definition())
    print()

# print("...")

# for result in results1[-10:]:
#     print(f"Similarity: {result[metric]}")
#     print(f"Game word: {result['word']}")
#     print(f"Game syn: {result['syn']}:")
#     print(result["syn"].definition())
#     print(f"Clue syn: {result['clue_syn']}:")
#     print(result["clue_syn"].definition())
#     print()

# Extract top num_words words
print("Ordered guesses:")
guesses = []
for result in results1:
    if result["word"] in guesses:
        continue
    
    guesses.append(result['word'])

    # if len(guesses) == num_words:
    #     break

# Print the guesses
for idx, guess in enumerate(guesses):
    print(f"{idx+1}: {guess}")


# -----------------------------------------------------------------------------

# # Repeat but using embeddings
# model = spacy.load("en_core_web_lg")

# words_combined = " ".join(words)

# doc_words = model(words_combined)
# doc_clue = model(clue)

# results2 = {}
# for token in doc_words:
#     sim = doc_clue[0].similarity(token)
#     results2[token.text] = sim

# # Sort results by similarity
# results2_copy = results2.copy()
# results2 = sorted(results2.items(), key=lambda x: x[1], reverse=True)

# for idx, result in enumerate(results2):
#     print(f"{idx + 1}. {result[0]} ({result[1]})")

# -----------------------------------------------------------------------------