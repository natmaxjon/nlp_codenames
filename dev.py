from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic
# from nltk.corpus import reuters # treebank, gutenberg, reuters
import spacy

import random

from gameboard import Board

# -------------------------------- FUNCTIONS -------------------------------- #

# Helper functions for the WordNet method

def get_lemma_dist(lemma, dist_data):
    """
    Get the distribution of a lemma from the CluBERT lexemes distribution data
    :param lemma: The lemma to get the distribution of
    :param dist_data: The CluBERT lexemes distribution data
    :return: A dictionary of part-of-speech tags, which maps to a list of (synset, score) tuples
    """
    lemma_dist = {}
    for row in dist_data:
        # Find the row that starts with the lemma
        if row.startswith(f"{lemma}#"):
            # Split the row into columns
            cols = row.split("\t")
            # The first column is the lemma and part-of-speech tag
            lemma, pos = cols[0].split("#")

            # Create a list of (synset, score) tuples
            syn_scores = []
            for col in cols[1:]:
                wnkey, score = col.split("#")
                synset = wn.synset_from_sense_key(wnkey)
                score = float(score)
                syn_scores.append((synset, score))

            # Add this list to the dictionary under the corresponding POS tag
            lemma_dist[pos] = syn_scores

    return lemma_dist


def filter_dist(lemma_dist, threshold):
    """
    Filter a lemma sense distribution by a threshold
    :param lemma_dist: The lemma distribution to filter
    :param threshold: The threshold to filter by (0 to 1)
    :return: The list of synsets above the threshold
    """
    filtered_dist = []
    for pos_dist in lemma_dist.values():
        for syn, score in pos_dist:
            if score >= threshold:
                filtered_dist.append(syn)

    return filtered_dist


# ---------------------------------- SETUP ---------------------------------- #

# Set the random seed for reproducibility
# random.seed(11)

# Load the CluBERT lexemes distributions (see https://github.com/SapienzaNLP/clubert)
with open("lexemes_distributions.wnkey.txt", "r") as f:
    lexeme_dist_data = f.read().splitlines()

# Load the WordNet information content files
semcor_ic = wn_ic.ic('ic-semcor.dat')
brown_ic = wn_ic.ic('ic-brown.dat')
# treebank_ic = wn.ic(treebank, False, 0.0)
# gutenberg_ic = wn.ic(gutenberg, False, 0.0)
# reuters_ic = wn.ic(reuters, False, 0.0)

# Set the threshold for filtering the distribution of word senses (0 to 1)
THRESHOLD = 0.1

# Load the Codenames game words
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Initialize and print the game board
words = random.sample(game_words, 25)
board = Board(words)
print(f"{board.get_display_string()}\n\n")

# ---------------------------------- INPUT ---------------------------------- #

clue = input("Clue: ")

# ----------------------------- WordNet Method ------------------------------ #

# Get the filtered distribution of each word
word_senses = {}
for word in words:
    # Get the distribution of the word
    lemma_dist = get_lemma_dist(word, lexeme_dist_data)
    # Filter the distribution by a threshold
    filtered_syns = filter_dist(lemma_dist, THRESHOLD)
    # Add the filtered distribution to the dictionary
    word_senses[word] = filtered_syns

# Get the filtered distribution of the clue
clue_dist = get_lemma_dist(clue, lexeme_dist_data)
clue_senses = filter_dist(clue_dist, THRESHOLD)

# Find the similarity between all combinations of senses in the clue and the words
similarity = []
for clue_syn in clue_senses:
    for word, word_syns in word_senses.items():
        for word_syn in word_syns:
            # Compare only if synsets are from the same POS
            # if clue_syn.pos() != word_syn.pos():
            #     continue

            similarity.append(
                {
                    "word": word,
                    "sense": word_syn,
                    "clue_sense": clue_syn,
                    # "similarity": clue_syn.path_similarity(word_syn),
                    # "similarity": clue_syn.lch_similarity(word_syn),
                    "similarity": clue_syn.wup_similarity(word_syn),
                    # "similarity": clue_syn.res_similarity(word_syn, treebank_ic),
                    # "similarity": clue_syn.jcn_similarity(word_syn, reuters_ic),
                    # "similarity": clue_syn.lin_similarity(word_syn, brown_ic),
                }
            )

# Sort the similarity scores in descending order
sorted_similarity = sorted(similarity, key=lambda x: x["similarity"], reverse=True)

# ---- OUTPUT OPTIONS ---- #

# 1. 

# Print the top 25 similarities (there may be multiple senses for each word)
print(f"{40 * '-'}\n")
print("Wordnet Similarity Ranking:\n")
for result in sorted_similarity[:25]:
    print(f"Word: {result['word']} ({result['similarity']})")
    print(f"Word sense: {result['sense']} - {result['sense'].definition()}")
    print(f"Clue sense: {result['clue_sense']} - {result['clue_sense'].definition()}")
    print()

# 2.

# # Print the top num_words unique words
# print()
# print("Wordnet Similarity:")
# print()
# seen_words = []
# for result in sorted_scores:
#     if result["word"] not in seen_words:
#         seen_words.append(result["word"])
#         print(f"Word: {result['word']} ({result['similarity']})")
#         print(f"Word sense: {result['sense']} - {result['sense'].definition()}")
#         print(f"Clue sense: {result['clue_sense']} - {result['clue_sense'].definition()}")
#         print()

#         if len(seen_words) == num_words:
#             break

# 3.

# results1 = {}
# for result in sorted_scores:
#     if result["word"] not in results1:
#         results1[result["word"]] = result["similarity"]

#         if len(results1) == num_words:
#             break

# results1 = sorted(results1.items(), key=lambda x: x[1], reverse=True)

# print()
# print("WordNet Similarity:")
# print()
# for idx, result in enumerate(results1[:num_words]):
#     print(f"{idx + 1}. {result[0]} ({result[1]})")

# ---------------------------- Embedding Method ----------------------------- #

# Load the spaCy model
model = spacy.load("en_core_web_lg")

# Get the embeddings for the clue and the words
words_combined = " ".join(words)
doc_words = model(words_combined)
doc_clue = model(clue)

# Find the similarity between the clue and the words
similarity = {}
for token in doc_words:
    sim = doc_clue[0].similarity(token)
    similarity[token.text] = sim

# Sort results by similarity
sorted_similarity = sorted(similarity.items(), key=lambda x: x[1], reverse=True)

# Display results
print(f"{40 * '-'}\n")
print("Embedding Similarity Ranking:\n")
for idx, result in enumerate(sorted_similarity):
    print(f"{idx + 1}. {result[0]} ({result[1]})")
