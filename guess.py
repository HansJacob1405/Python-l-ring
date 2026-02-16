import random


def generate_secret(low,high):
    return random.randint(low, high)


def get_guess(low,high):

    guess_given = False

    while not guess_given:

        guess_str = input("Gæt et tal: ").strip()

        try:  
            guess = int(guess_str)
            
            if not (low <= guess <= high):
             print("Tallet skal være mellem {low} og {high}.")
             continue
            else: 
             guess_given = True
             return int(guess_str)
        except ValueError:
            print("Skriv et helt tal mellem {low} og {high}")
            continue

def play_game(low,high,max_attempts):

    attempts = 0

    secret = generate_secret(low,high)

    print(f"Det rigtige tal var {secret}.")

    print("Jeg tænker på et tal mellem {low} og {high}.")

    while attempts < max_attempts:

        guess = get_guess(low,high)
         
        attempts += 1

        if guess < secret:
            print("For lavt!")
        elif guess > secret:
            print("For højt!")
        else:
            print(f"Korrekt! Du brugte {attempts} forsøg.")
            break
    else:
        print(f"Du har haft {max_attempts} forsøg, så du får ikke flere. Det rigtige tal var {secret}.")


if __name__ == "__main__":

    low=1
    high = 20
    max_attempts =6

    play_game(low, high, max_attempts)



