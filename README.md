# Mastermind
Delo

## Overview

Program which processes Mastermind games, with a pre-decided Codebreaker, Codemaster and guesses.

### Human-mode

Takes complete Mastermind games as input text files, processes these, validates them and produces an appropriate output file. The output file could contain an error message if the input file is not valid (i.e. length of Codebreaker's code is smaller than the set code length), or a thorough evaluation of each guess in the game, providing feedback and comparing against the true code.


### Computer-mode

Computer acts as the codebreaker, attempt to find the true code with minimal number of guesses. In order to produce the guesses, used a genetic algorithm approach described below.

#### Genetic Algorithm for Automated Guesses

Found a partially optimal solution for the NP-complete problem of finding the correct Mastermind code. Referenced the following paper for guidance: https://studenttheses.uu.nl/bitstream/handle/20.500.12932/30147/bachelorthesis_vivianvanoijen.pdf?sequence=2.
