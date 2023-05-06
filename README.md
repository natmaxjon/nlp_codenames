# Codenames
### Vrije Universiteit Amsterdam
#### XM_0121 - Natural Language Processing
Nathan Jones (2762057)

## Overview

A simplified version of the game [Codenames](https://codenamesgame.com/) is implemented in Python using [spaCy](https://spacy.io/), [NLTK](https://www.nltk.org/) and [Pygame](https://www.pygame.org/docs/) to explore semantic reasoning tasks using two appraoches: word embeddings and WordNet taxonomies.

## Requirements

This project was implemented using [Python 3](https://www.python.org/downloads/). The list of required packages can be found in 
`requirements.txt`. To install them, run the following command from the root directory of this project (preferably in a virtual environment).

```sh
$ pip3 install -r requirements.txt
```

After this, the [en_core_web_lg](https://spacy.io/models/en#en_core_web_lg) spaCy model and the [WordNet](https://wordnet.princeton.edu/) 
NLTK corpus can be downloaded as follows:

```sh
$ python3 -m spacy download en_core_web_lg
```

```sh
$ python3
>>> import nltk
>>> nltk.download('wordnet')
>>> exit()
```

> If you encounter the error [SSL: CERTIFICATE_VERIFY_FAILED] when using `nltk.download()`, see [here](https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed).

## Running the Code

To play the main game:

```sh
$ python3 main.py
```

By default, the `embedding` agent is used, but you can specify the model using the additional command-line argument as follows:

```sh
$ python3 main.py --model <model_choice>
```

> The other model option is `wordnet`. Run `python3 main.py --help` for details. 

To explore the model outputs in more detail run:

```sh
$ python3 dev.py
```

## Key Source Files
> **main.py**
> Implements the game loop, rendering and user input functionality in [Pygame](https://www.pygame.org/docs/).

> **codenames.py**
> Implements the rule set and coordinates the core game elements of Codenames.

> **gameboard.py**
> Contains the `Board` class used to manage the state of the game board.

> **embedding_agent.py**
> Contains the `EmbeddingAgent` class which receives a clue and makes guesses using the cosine similarity of word embeddings.

> **wordnet_agent.py**
> Contains the `WordNetAgent` class which receives a clue and makes guesses using Wu-Palmer Similarity in the WordNet taxonomy.

> **dev.py**
> Used for testing and debugging the agents.

## Game Rules

The rules are a simplified version of the original Codenames rules found [here](https://czechgames.com/files/rules/codenames-rules-en.pdf). This game implements the two-player version of the game, where the player is always the spymaster and the computer agent is the field operative. Your goal is to reveal all the blue cards before all the red cards are revealed without ever revealing the grey card (the assassin). See the original [rules](https://czechgames.com/files/rules/codenames-rules-en.pdf) for more details.

Each turn consists of two phases: the **Clue Phase** and the **Red Reveal Phase**.

### Clue Phase

<img width="1312" alt="clue" src="https://user-images.githubusercontent.com/68292593/236468225-a0281672-1e0c-421b-98d7-f07d3437b3ca.png">

During the Clue Phase, your goal is to provide a clue that groups together as many of the blue cards as possible, while excluding the others. The clue must be entered as a single word, a space, and a number specifiying how many words the clue applies to. For example, in this case we may want to try and target `RULER`, `CHARGE` and `AZTEC` with the clue of 'king'. As seen in the next phase, the agent correctly identified `RULER` as its first guess, but calculated a higher similarity for `GRACE` for its second guess. As soon as a non-blue card is revealed, the phase ends regardless of the number you gave.

### Red Reveal Phase

<img width="1312" alt="red_reveal" src="https://user-images.githubusercontent.com/68292593/236468389-23563a62-56ed-440d-a7dc-dbfbbf664528.png">

In the next phase, you will simulate your opponent by choosing a red card to reveal (you may want to be strategic about your choice). To do this, simply type in the word of an unrevealed red word on the board. We may want to target `TAP` in the next round, so it might be reasonable to remove `WATER` from the board.

### Ending the Game

The game can end in one of three ways. 

1. **You reveal the assassin** (LOSE).
2. **All the red cards get revealed** (LOSE).
3. **All the blue cards get revealed** (WIN).

In the case that you win, your score is calculated as follows:

**score = (number of unrevealed red cards) + 0.2 (number of unrevealed neutral cards)**


