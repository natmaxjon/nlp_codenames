from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic
# from nltk.corpus import treebank # treebank, gutenberg, reuters

import spacy

import random


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

# Load the Codenames game words
with open("game_words.txt", "r") as f:
    game_words = f.read().splitlines()

# Load the CluBERT lexemes distributions (see https://github.com/SapienzaNLP/clubert)
with open("lexemes_distributions.wnkey.txt", "r") as f:
    lexeme_dist_data = f.read().splitlines()

# Load the WordNet information content files
semcor_ic = wn_ic.ic('ic-semcor.dat')
brown_ic = wn_ic.ic('ic-brown.dat')
# treebank_ic = wn.ic(treebank, False, 0.0)
# gutenberg_ic = wn.ic(gutenberg, False, 0.0)
# reuters_ic = wn.ic(reuters, False, 0.0)

# Set the random seed
# random.seed(11)

# Constants
THRESHOLD = 0.3

# ---------------------------------- SETUP ---------------------------------- #

# Randomly sample 25 words
words = random.sample(game_words, 25)

# Print the sample as a 5x5 grid
for i in range(5):
    print(words[i * 5 : (i + 1) * 5])
print()

# Get the filtered distribution of each word
word_senses = {}
for word in words:
    # Get the distribution of the word
    lemma_dist = get_lemma_dist(word, lexeme_dist_data)
    # Filter the distribution by a threshold
    filtered_syns = filter_dist(lemma_dist, THRESHOLD)
    # Add the filtered distribution to the dictionary
    word_senses[word] = filtered_syns

# Receive the clue from the spymaster
clue = input("Enter the clue: ")

# Receive the number of words the clue applies to
num_words = int(input("Enter the number of words: "))

# Get the filtered distribution of the clue
clue_dist = get_lemma_dist(clue, lexeme_dist_data)
clue_senses = filter_dist(clue_dist, THRESHOLD)

# Find the similarity between all combinations of senses in the clue and the words
scores = []
for clue_syn in clue_senses:
    for word, word_syns in word_senses.items():
        for word_syn in word_syns:
            # Compare only if synsets are from the same POS
            if clue_syn.pos() != word_syn.pos():
                continue

            scores.append(
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
sorted_scores = sorted(scores, key=lambda x: x["similarity"], reverse=True)

# ---- OUTPUT OPTIONS ---- #

# 1.

# # List before processing
# print()
# print("COMPLETE RANKING:")
# print()
# for result in sorted_scores:
#     print(f"Word: {result['word']} ({result['similarity']})")
#     print(f"Word sense: {result['sense']} - {result['sense'].definition()}")
#     print(f"Clue sense: {result['clue_sense']} - {result['clue_sense'].definition()}")
#     print()

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

# Simplified version of above
results1 = {}
for result in sorted_scores:
    if result["word"] not in results1:
        results1[result["word"]] = result["similarity"]

        if len(results1) == num_words:
            break

results1 = sorted(results1.items(), key=lambda x: x[1], reverse=True)

print()
print("WordNet Similarity:")
print()
for idx, result in enumerate(results1[:num_words]):
    print(f"{idx + 1}. {result[0]} ({result[1]})")

# --------------------------------------------------------------------------- #

# Repeat but using embeddings
model = spacy.load("en_core_web_lg")

words_combined = " ".join(words)

doc_words = model(words_combined)
doc_clue = model(clue)

results2 = {}
for token in doc_words:
    sim = doc_clue[0].similarity(token)
    results2[token.text] = sim

# Sort results by similarity
results2_copy = results2.copy()
results2 = sorted(results2.items(), key=lambda x: x[1], reverse=True)

print()
print("Embedding Similarity:")
print()
for idx, result in enumerate(results2[:num_words]):
    print(f"{idx + 1}. {result[0]} ({result[1]})")

# --------------------------------------------------------------------------- #

# lemma = "olympus"

# print(20 * "-")
# print()
# print("BEFORE FILTERING")
# for syn in wn.synsets(lemma):
#     print(f"{syn.name()}: {syn.definition()}")

# lemma_dist = get_lemma_dist(lemma, lexeme_dist_data)

# print()
# print("DISTRIBUTION")
# for pos, syn_scores in lemma_dist.items():
#     print(pos)
#     for syn, score in syn_scores:
#         print(f"{syn.name()}: {score} - {syn.definition()}")
#     print()

# filtered_lemma_dist = filter_dist(lemma_dist, THRESHOLD)

# print()
# print("AFTER FILTERING")
# for syn in filtered_lemma_dist:
#     print(f"{syn.name()}: {syn.definition()}")
# print()
