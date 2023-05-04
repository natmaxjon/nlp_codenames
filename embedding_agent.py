import spacy

class EmbeddingAgent():
    def __init__(self, spacy_model):
        self.model = spacy.load(spacy_model)
        self.word_embeddings = {}
    
    def guess(self, clue, n):
        """
        Get the top n words from words that are most similar to clue using embeddings
        :param words: list of words to guess from
        :param clue: clue to guess from
        :param n: number of words to return
        :return: list of n words most similar to clue (in descending order)
        """
        # Get the clue embedding
        clue = self.model(clue)

        # Calculate similarity between clue and each word
        similarity = {}
        for word in self.word_embeddings:
            similarity[word.text] = clue[0].similarity(word)

        # Sort similarity scores in descending order
        sorted_similarity = sorted(similarity.items(), key=lambda x: x[1], reverse=True)

        # Return top n words
        return [word[0] for word in sorted_similarity[:n]]
    
    def load_words(self, words):
        """
        Update the list of words to guess from, calculating a new list of embeddings
        :param words: new list of words to guess from
        """
        self.word_embeddings = self.model(" ".join(words))

