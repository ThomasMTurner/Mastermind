import sys
import os
import random
import itertools

'''

COMMENTING STRUCTURE:

1. Concise comments expand on variable usage and certain parts of functions. These use the standard '#' notation.
2. Full descriptions of functions, their purpose and underlying process is described in full detail with docstrings above
them.

'''


## Set global variables for the input file, output file, code to guess, and whether in human or computer mode.

IN      = None
OUT     = None
CODE    = None
PLAYER  = None

## Set default values for number of guesses allowed, length of code, and available colours.

MAX_GUESSES       = 12
CODE_LENGTH       = 4
AVAILABLE_COLOURS = ["red", "blue", "yellow", "green", "orange"]

'''

Purpose: Obtains feedback for a guess by comparing against the true code:

How it works:

1) For every colour in the guess
2) If the colour is in the correct position, return black peg feedback (denoted by string "black").
3) If the colour is in the code but not in the correct position, return white peg feedback (denoted by string "white").
4) If neither, then we return no feedback.

Furthermore - we maintain that we haven't already checked a duplicate colour, since we only return one white feedback per
unique colour which appears in the guess.


'''

def get_feedback(guess):
    feedback = []
    checked_colours = set()
    for i, colour in enumerate(guess):
        if CODE:
            if CODE[i] == colour:
                checked_colours.add(colour)
                feedback.append("black")
            elif colour in CODE and colour not in checked_colours:
                checked_colours.add(colour)
                feedback.append("white")
    
    
    return feedback



'''

Purpose: Writes correct output for a guess, and validates whether it is a success outcome, close guess, or invalid guess.

How it works:

1) Check every guess.
2) Split guess, originally consisting of colours delimited by spaces, to a list of colours which can be checked through iteration.
3) If the the guess is a different length to the code, or includes colours that are not available, return as invalid.
4) If the guess is valid, always output guess i with the correct feedback.
5) If we meet a guess which is the true code, present this in the output. Additionally, specify whether there were leftover guesses
which were omitted from the output file.
6) If maximum guesses have been reached, write this to the output and immediately return as successful completion.
7) If we have checked all guesses and the correct code is not found, output appropriate string and return success state.


'''

def validate_guesses(guesses):
    for i, guess in enumerate(guesses):
        guess = guess.split()

        if len(guess) != CODE_LENGTH or any(colour not in AVAILABLE_COLOURS for colour in guess):
            line = f"Guess {i + 1}: ill-formed guess provided"
            write_output(OUT, line)

        else:
            line = f"Guess {i + 1}: {' '.join(get_feedback(guess))}"
            write_output(OUT, line)

        if guess == CODE: 
            line = f"You won in {i + 1} guesses. Congratulations!"
            write_output(OUT, line)
            if i < len(guesses) - 2:
                line = "The game was completed. Further lines were ignored."
                write_output(OUT, line)
            

            return 0

        if i == MAX_GUESSES - 1:
            line = f"You can only have {MAX_GUESSES} guesses"
            write_output(OUT, line)
            return 0
        

    line = "You lost. Please try again."
    write_output(OUT, line)
    return 0


'''

Purpose: Validates whether a player is either ill-formed, computer or human.

How it works:

1) If the "player" placeholder is not included in the input file line, return error code (ill-formed player provided).
2) If the the second word is either "human" or "computer", set this as the global PLAYER variable.
3) Else, not a valid mode, and return error code.

'''
    
def validate_player(player):
    if player[0] != "player":
        return 5         
    
    elif player[1] == "human" or player[1] == "computer":
        global PLAYER
        PLAYER = player[1].strip()

    else:
        return 5


'''

Purpose: Validates whether the code provided as a programme argument is well-formed - if so assigns as global CODE.

How it works:

1) If the placeholder "code" not in the input file line, return error code (ill-formed code provided).
2) If code contains any duplicates - return error code. 
3) If any of the colours in the code are not in available colours - return error code.
4) If the code is the incorrect length - return error code.
5) Else - code is valid - set as global CODE.

'''


def validate_code(code):
    if code[0] != "code":
        return 4
            
    temp = code[1:]
    
    ## Converting to set immediately removes duplicates - comparing length to original list hence determines whether there exists
    ## any duplicates efficiently.
    if len(temp) != len(set(temp)):
        return 4
    
    if any(colour not in AVAILABLE_COLOURS for colour in temp):
        return 4

    if len(temp) != CODE_LENGTH:
        return 4
    
    global CODE
    CODE = temp


def generate_computer_game_file(code):
    ## Creates new computer game file if doesn't already exists, or opens new.
    with open("computerGame.txt", 'a') as f:
        ## Writes the code i.e. "code red blue yellow", new line, and then "player human" as is correct for a
        ## Human mode file before guesses added in.
        f.write(' '.join(code) + "\n")
        f.write("player human" + "\n")



'''

Solution for computer player:  genetic algorithm.

Motivation:

Since the problem of finding Mastermind code is NP-complete - I searched for a closest optimal solution - including constraint satisfaction.
Settled on an implementation of a genetic algorithm referenced partially from the following paper: 
https://studenttheses.uu.nl/bitstream/handle/20.500.12932/30147/bachelorthesis_vivianvanoijen.pdf?sequence=2.

Also used a GA as the representation of the codes is already suitable for the problem - since genetic algorithms
process strings of information, such as binary codes (in our case a set of colours).

Terminology:

Individual - an individual code in the space of possible codes, meeting two constraints (1) no duplicate colours in a code
(2) all colours selected from those available.

Population - a set of codes.

Generation - the nth population at the nth iteration of the GA.

Fitness - distance of a given individual code to the true code set in programme argument.

Tournament - Each round of the tournament selects n codes and returns the one with the highest fitness.

Crossover - Stochastically generate new codes by splicing two parent codes.

Mutation - Randomly modify a colour in a code, at the mutation rate.

Elite - Selects the n codes with the highest fitness, attempting to reduce generations needed to find the correct code.

Parents - The subset of codes selected for crossover.

Children - The set of codes produced by crossover of parents.


'''

## Hyperparameters for the genetic algorithm.

TOURNAMENT_SIZE     = 2     ## The amount of individuals per tournament.
POPULATION_SIZE     = 10    ## Size of the population to be maintained across all generations of the algorithm.
MUTATION_RATE       = 0.01  ## How often to mutate each individual.
WHITE_PEG_REWARD    = 5     ## Fitness reward for receiving white peg feedback.
BLACK_PEG_REWARD    = 10    ## Fitness reward for receiving black peg feedback.


'''

Purpose: Determines fitness of an individual (code) using the fitness rewards for black peg and white peg feedback.

How it works: self-explanatory.

'''

def fitness(code):
    fitness = 0
    feedback = get_feedback(code)
    for peg in feedback:
        match peg:
            case "white":
                fitness += WHITE_PEG_REWARD
            case "black":
                fitness += BLACK_PEG_REWARD

    return fitness


'''

Purpose: Initialise a population of n randomised codes which meet the following constraints (1) no duplicate colours (2) colours selected
only from available colours.

How it works:

1) Continue to generate randomised codes until the population size n is met.
2) Produce a code as a tuple, as a random sample of codes with the set code length. Only sample from available colours. 
3) Ensure all unique codes by creating a new one if the generated already exists in the population.

Structure:

Stores codes as tuples which key into their individual evaluated fitness.


'''
def initialise_population(n):
    population = {}
    while len(population) < n:
        code = tuple(random.sample(AVAILABLE_COLOURS, k=CODE_LENGTH))
        if code not in population:
            population[code] = fitness(code)

    return population

'''
Purpose: Decides a subset of a generation of codes which should be selected for both elitism and crossover.

How it works:

1) Determines the number of rounds to carry out which should select over the entire generation.
2) For each round.
3) Sample n random codes from the generation, and add to the selected population the one with the highest fitness.


'''

def tournament_select(population):
    selected_population = []
    num_of_tournaments = POPULATION_SIZE // TOURNAMENT_SIZE
    for _ in range(num_of_tournaments):
        selected_members = random.sample(list(population.keys()), k=TOURNAMENT_SIZE)
        tournament = {member: population[member] for member in selected_members}
        selected_population.append(max(tournament, key=lambda x: tournament[x]))
    
    return selected_population

'''

Purpose: Implements single-point crossover between two parent codes.

How it works:

1) Determines a crossover point in the code based on a random position from 0 up to the highest index possible.
2) Generates two children codes from two parents, by splicing at the halfway point for both parents.

'''

def crossover(code1, code2):
    crossover_point = random.randint(0, CODE_LENGTH - 1)
    result = [code1[:crossover_point] + code2[crossover_point:], code2[:crossover_point] + code1[crossover_point:]]
    if len(set(result[0])) != len(result[0]) or len(result[1]) != len(set(result[1])):
        return crossover(code1, code2)

    return result

'''

Purpose: Randomly mutates a code - maintains diversity in the solution space.

How it works:

1. As in the main generate_guesses(), if a code has been found within the mutation rate - we then select it for mutation.
2. My mutation method simply modifies a colour in the code at a random position - checking if the new code still satisfies constraints
and does not already exist in the population.


'''

def mutate(code, population):
    temp = code
    change = random.randint(0, CODE_LENGTH - 1)
    code[change] = random.choice(AVAILABLE_COLOURS)
    if code in population or (len(set(code)) != len(code)):
        return mutate(temp, population)
    
    return code 


## Utility function which removes pairs which exist in the list more than once but are in reverse order.

def remove_ordered_duplicates(parents):
    for (a, b) in parents:
        if (b, a) in parents:
            parents.remove((a, b))
    
    return parents

'''

Purpose: Generates the set of guesses used by the computer player.

How it works:

1) If we have exceeded the max number of guesses allowed - return them.
2) If initial generation - initialise population of size 10.
3) Else - fill the new generation to at least meet 10 members if it is smaller than 10.
4) Select subset of generation for crossover using Tournament Selection as described above.
5) Select three codes from this subset as elites (elitism). These are kept without crossover.
6) Generate all possible pairs of codes as parents - excluding ordered duplicates.
7) Add to the new generation the elites and the crossover of all the parents.
8) Mutate new generation.
9) If the correct code is in the population, add it to guesses and return it.
10) Else, select a random code from the population and add it to guesses, repeat for new generation.


'''


def generate_guesses(population=[], guesses=[]):

    if len(guesses) > MAX_GUESSES - 1:
        return guesses

    ## Initialise population - later set size as function of the code length
    if population == []:
        population = initialise_population(n=POPULATION_SIZE)

    else:
        ## Fill to population of 10 to ensure continued generation.
        temp = {}
        for member in population:
            temp[tuple(member)] = fitness(member)

        population = temp

        fill = POPULATION_SIZE - len(list(population.keys()))
        if fill > 0:
            extra = initialise_population(n=fill) 
            population.update(extra)

         

    ## Select subset as parents using Tournament Selection - returns 5 codes.
    population = tournament_select(population)
    elite = population[0:2]

    
    ## Crossover
    parents = remove_ordered_duplicates([(a, b) for a, b in list(itertools.combinations(population, 2)) if a != b])
    population = []
    for pair in parents:
        population.extend(crossover(pair[0], pair[1]))
    
    
    population = list(set(population))
    ## Mutate a subset of parents:
    for i, member in enumerate(population):
        if random.random() < MUTATION_RATE:
            population[i] = mutate(list(member), population)


    population.extend(elite)

    
    for member in population:
        if list(member) == CODE:
            guesses.append(CODE)
            return guesses
     
    
    ## Replace population and make call back to generate_guesses()
    guesses.append(random.choice(population))
    return generate_guesses(population)

    
        
'''

Purpose: Wraps logic for playing the game. Including reading and validating input file.

How it works:

1) Checks if the file first has enough lines to be valid in either mode - returns exit code if not.
2) Gets the code from the first line and validates it - will either return the code or an exit code which terminates the program.
3) Gets the player from the second line and validates it - again will either return the player or an exit code.
4) Matches against whether PLAYER is set to human or computer mode.
5) If in human mode - get guesses from the input file and validate them - as described above in the validate_guesses() comment.
6) If in computer mode:
    6a) Generate the computer game file as described above.
    6b) Generate guesses from genetic algorithm.
    6c) Process guesses back into a single string.
    6d) Write guesses to output file.

7) If any problem with the file - including lacking permissions and invalid file path - terminate the program with appropriate exit code.


'''

def read_input(input_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                print("Invalid input file, exiting...")
                return 2


            ## First line should be "code" followed by the code colours
            code = lines[0].split()
            result = validate_code(code)
            if result is not None:
                return result

            
            ## Second line is "player" followed by "human" or "computer"
            player = lines[1].split()
            result = validate_player(player)
            if result is not None:
                return result
            

            match PLAYER:
                case "human":
                    guesses = lines[3:]
                    if len(guesses) == 0:
                        return 2
                    result = validate_guesses(guesses)
                    if result is not None:
                        return result

                case "computer":
                    generate_computer_game_file(code)
                    pre_processed_guesses = generate_guesses()
                    guesses = None
                    if pre_processed_guesses is not None:
                        guesses = [' '.join(guess) for guess in pre_processed_guesses]
                    write_output("computerGame.txt", guesses, single_line=False)
                    return 0





    except FileNotFoundError:
        print("Invalid input file path provided, exiting...")
        return 2
    
    except PermissionError:
        print("You do not have the privileges to access this file, exiting...")
        return 2

    except TypeError:
        return 2


## Writes a single line or multiple lines to output file - specified by optional parameter.
## Creates the output file if it doesn't exist.
## Returns exit code if user does not have write permissions for the current working directory.

def write_output(output_file, lines, single_line=True):
    try:
        with open(output_file, "a") as f:
            if single_line:
                f.write(lines + '\n')
            else:
                for line in lines:
                    f.write(line + '\n')
    
    except PermissionError:
        print("You do not have privileges to write to this file / create new output file, exiting...")
        return 3
    

    
'''
Purpose: 



How it works:



'''

def main():
    ## Obtain arguments to call to script.
    cmd_arguments = sys.argv
    
    adding_colours = False
 
    ## Handling incorrect number of arguments - minimum 3 (script, input, output), maximum 6.
    ## Exit code 1 now recognises both too few and too many provided arguments.
    if len(cmd_arguments) < 3:
        return 1

    else:
        for i, argument in enumerate(cmd_arguments):

            ## Skip optional parameters specified by empty string
            if len(argument) == 0:
                continue

            if i < 5:
                match i:
                    case 4:
                        try:
                            global MAX_GUESSES
                            MAX_GUESSES = int(argument)
                            if MAX_GUESSES < 1:
                                return 1
                            print("Set maximum guesses to ", MAX_GUESSES)
                        except ValueError:
                            return 1

                    case 3:
                        try:
                            global CODE_LENGTH
                            CODE_LENGTH = int(argument)
                            if CODE_LENGTH < 1:
                                return 1
                            print("Set code length to: ", CODE_LENGTH)
                        except ValueError:
                            return 1
                
                    case 2:
                        if not os.path.exists(argument):
                            print("Output file path is invalid, exiting...")
                            return 3
                        else:
                            global OUT
                            OUT = argument

                    case 1:
                        global IN
                        IN = argument
            
            else:
                global AVAILABLE_COLOURS
                if not adding_colours:
                    AVAILABLE_COLOURS = []
                    adding_colours = True
                if argument.isalpha():
                    AVAILABLE_COLOURS.append(argument)
                else:
                    return 1


                    


        
        result = read_input(IN)
        return result

       
## Below executes the root of the program and returns the appropriate exit code to the terminal, as well as writing error messages
## To the output file.

if __name__ == "__main__":
    result = main()
    match result:
        case 0:
            print("Programme completed successfully.")
        case 1:
            print("Not enough programme arguments provided.")
        case 2:
            line = "Issue with input file."
            write_output(OUT, line)
        case 3:
            print("Issue with output file.")
        case 4:
            line = "No or ill-formed code provided."
            write_output(OUT, line)
            
        case 5:
            line = "No or ill-formed player provided."
            write_output(OUT, line)

        case _:
            print("Unknown exit code encountered.")

    print("Returned exit code: ", result)

            

