from nltk.corpus import wordnet as wn

class WordNetAgent():
    def __init__(self, lex_dist_file, threshold=0.1) -> None:
        with open(lex_dist_file, "r") as f:
            self.sense_dist_data = f.read().splitlines()
        
        self.threshold = threshold
        self.word_senses = {}
    
    def guess(self, clue, n):
        """
        Get the top n words from words that are most similar to clue using WordNet
        :param words: list of words to guess from
        :param clue: clue to guess from
        :param n: number of words to return
        :return: list of n words most similar to clue (in descending order)
        """

        # Get the filtered senses of the clue
        clue_senses = self.get_sense_dist(clue)
        clue_senses = self.filter_senses(clue_senses)

        # Find the similarity between all combinations of senses in the clue and the words
        similarity = {}
        for clue_sense in clue_senses:
            for word, word_senses in self.word_senses.items():
                for word_sense in word_senses:
                    similarity[(word, word_sense)] = clue_sense.wup_similarity(word_sense)
        
        # Sort similarity scores in descending order
        sorted_similarity = sorted(similarity.items(), key=lambda x: x[1], reverse=True)

        # Return top n (unique) words
        top_n = []
        for (word, _), _ in sorted_similarity:
            if word not in top_n:
                top_n.append(word)

            if len(top_n) == n:
                break
        
        return top_n
    
    def load_words(self, words):
        """
        Update the list of words to guess from, removing old words and adding new
        words and their filtered senses.
        :param words: new list of words to guess from
        """

        # Add new words
        new_words = list(set(words) - set(self.word_senses))
        for word in new_words:
            sense_dist = self.get_sense_dist(word)
            filtered_senses = self.filter_senses(sense_dist)
            self.word_senses[word] = filtered_senses

        # Remove words that are no longer in the game
        old_words = list(set(self.word_senses) - set(words))
        for word in old_words:
            del self.word_senses[word]

    def get_sense_dist(self, lemma):
        """
        Get the sense distribution of a lemma from the CluBERT lexemes distribution data.
        See https://github.com/SapienzaNLP/clubert for the file format details.
        :param lemma: The lemma to get the distribution of
        :return: A dictionary of part-of-speech tags, which maps to a list of (synset, score) tuples
        """
        sense_dist = {}
        for row in self.sense_dist_data:
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
                sense_dist[pos] = syn_scores

        return sense_dist
    
    def filter_senses(self, sense_dist):
        """
        Filter a lemma sense distribution by a threshold
        :param sense_dist: A dictionary of part-of-speech tags, which maps to a list of (synset, score) tuples
        :return: The list of synsets above the threshold
        """
        synsets = []
        for pos_dist in sense_dist.values():
            for syn, score in pos_dist:
                if score >= self.threshold:
                    synsets.append(syn)

        return synsets
