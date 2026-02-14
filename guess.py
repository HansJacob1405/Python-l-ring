import random


def generate_secret():
    return random.randint(1, 20)


def get_guess():

    guess_given = False

    while not guess_given:
    
        guess_str = input("Gæt et tal: ").strip()

        if guess_str.isdigit():
           guess_given = True
           return int(guess_str) 
        
        else: print("Skriv et helt tal mellem 1 og 20, fx 7.")
        continue

    
def play_game():

    attempts = 0

    max_attempts = 6

    secret = generate_secret()

    print(f"Det rigtige tal var {secret}.")

    print("Jeg tænker på et tal mellem 1 og 20.")

   

    while attempts < max_attempts:

        guess = get_guess()
         
        if not (1 <= guess <= 20):
            print("Tallet skal være mellem 1 og 20.")
            continue

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


play_game()
