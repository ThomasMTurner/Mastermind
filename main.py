import sys
import os

## Set global variables for the input file, output file, code to guess, and whether in human or computer mode.
IN = None
OUT = None
CODE = None
PLAYER = None

## Set default values for number of guesses allowed, length of code, and available colours.
MAX_GUESSES = 12
CODE_LENGTH = 3
AVAILABLE_COLOURS = ["red", "blue", "yellow", "green", "orange"]


## Obtain feedback (in terms of black and white pegs) - black if correct guess in place - white if correct guess not in place.
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

    return ' '.join(feedback)
        

## Write guesses to output - including feedback information, whether the guess was valid, and whether the player won.
def validate_guesses(guesses):
    print("Guesses to be parsed: ", guesses)
    for i, guess in enumerate(guesses):
        guess = guess.split()

        print("Checking guess: ", guess)

        if len(guess) != CODE_LENGTH:
            print("Guess was not valid")
            line = f"Guess {i + 1}: ill-formed guess provided"
            write_output(OUT, line)

        else:
            print("Guess was valid but not complete")
            line = f"Guess {i + 1}: {get_feedback(guess)}"
            write_output(OUT, line)

        if guess == CODE: 
            print("Guess was complete")
            line = f"You won in {i + 1} guesses. Congratulations!"
            write_output(OUT, line)
            if i < len(guesses) - 2:
                print("Current guess: ", i)
                print("Next guess omitted at index ", (len(guesses) - 1))
                line = "The game was completed. Further lines were ignored."
                write_output(OUT, line)
            

            return 0

        if i == MAX_GUESSES - 1:
            print("Guesses exceed max number")
            line = f"You can only have {MAX_GUESSES} guesses"
            write_output(OUT, line)
            break
        

    ## If valid guess not found - 
    line = "You lost. Please try again."
    write_output(OUT, line)
    
## Determines the current play mode - return exit code 5 if not well-formed.
def validate_player(player):
    if player[0] != "player":
        return 5         
    
    if player[1] == "human" or player[1] == "computer":
        global PLAYER
        PLAYER = player[1].strip()

    else:
        print("Returned an invalid player")
        return 5


## Determines the global variable of code - return exit code 4 if not well-formed.
def validate_code(code):
    if code[0] != "code":
        return 4
            
    temp = code[1:]

    if len(temp) != len(set(temp)):
        return 4

    if set(temp).difference(set(AVAILABLE_COLOURS)):
        return 4

    if len(temp) != CODE_LENGTH:
        return 4
    
    global CODE
    CODE = temp


## Computer game specific utilities

def generate_computer_game_file(code):
    with open("computerGame.txt", 'a') as f:
        f.write(' '.join(code) + "\n")
        f.write("player human" + "\n")


def make_computer_guesses():
    pass
        
        


## Reads input file fully - determining if well-formed and also the outcome of the game.
def read_input(input_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            print("Obtained the following lines: ", lines) 
            ## First line should be "code" followed by the code colours
            code = lines[0].split()
            print(code)
            result = validate_code(code)
            if result is not None:
                print(result)
                return result

            print("Obtained code: ", CODE)
            
            ## Second line is "player" followed by "human" or "computer"
            player = lines[1].split()
            result = validate_player(player)
            if result is not None:
                return result
            
            print("Now looking at player mode: ", PLAYER)

            match PLAYER:

                case "human":
                    guesses = lines[2:]
                    result = validate_guesses(guesses)
                    if result is not None:
                        return result

                case "computer":
                    print("Computer mode case")
                    generate_computer_game_file(code)
                    ## guesses = make_computer_guesses()
                    ## write_output(OUT, guesses, single_line=False)
                    return 0

                    '''
                    SYSTEM -> 

                    1. Generate new file - computerGame.txt - which contains the code followed by "player human".
                    2. Generate guesses until (a) finds solution or (b) meets maximum guesses.
                    3. Write guesses to (computerGame.txt).
                    4. (For testing): feed computerGame.txt to read_input(computerGame.txt).

                    ALGORITHM -> 

                    Basic outline:

                    1. 
                    2.



                    Implementation:



                    '''


    except FileNotFoundError:
        print("Invalid input file path provided, exiting...")
        return 2
    
    except PermissionError:
        print("You do not have the privileges to access this file, exiting...")
        return 2

    except TypeError:
        return 2


## Writes a line to output file.
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
    

    


## Sets programme arguments to variables (if validated) - returns exit code if ill-formed and finally reads out the input file to 
## Validate it and determine the outcome of the game.
def main():
    ## Obtain arguments to call to script.
    cmd_arguments = sys.argv
 
    ## Handling incorrect number of arguments - minimum 3 (script, input, output), maximum 6.
    ## Exit code 1 now recognises both too few and too many provided arguments.
    if len(cmd_arguments) < 3 or len(cmd_arguments) > 6:
        return 1

    else:
        for i, argument in enumerate(cmd_arguments):

            ## Skip optional parameters specified by empty string
            if len(argument) == 0:
                continue

            match i:
                case 0:
                    print("Obtained the script name, ignoring...", argument)
                case 5:
                    try:
                        global AVAILABLE_COLOURS
                        AVAILABLE_COLOURS = argument[1: -1].split(",")
                    except ValueError:
                        return 1
                case 4:
                    try:
                        global MAX_GUESSES
                        MAX_GUESSES = int(argument)
                        if MAX_GUESSES < 1:
                            return 1
                    except ValueError:
                        return 1

                case 3:
                    try:
                        global CODE_LENGTH
                        CODE_LENGTH = int(argument)
                        if CODE_LENGTH < 1:
                            return 1
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


        
        result = read_input(IN)
        return result

       
        

if __name__ == "__main__":
    result = main()
    match result:
        ## Match main call to all exit codes - write to output based on case.
        case 0:
            print("Programme completed successfully")
        case 1:
            print("Not enough programme arguments")
        case 2:
            line = "Issue with input file"
            write_output(OUT, line)
        case 3:
            print("Issue with output file")
        case 4:
            line = "No or ill-formed code provided"
            write_output(OUT, line)
        case 5:
            line = "No or ill-formed player provided"
            write_output(OUT, line)
