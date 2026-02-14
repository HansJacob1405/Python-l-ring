import random


def generate_secret():
    return random.randint(1, 20)


def get_guess():

    attempts = 0

    max_attempts = 6

    secret = generate_secret()

    print(f"Det hemmelige tal er {secret}")

    print("Jeg tænker på et tal mellem 1 og 20.")

    while attempts < max_attempts:
        guess_str = input("Gæt et tal: ").strip()

        if not guess_str.isdigit():
            print("Skriv et helt tal mellem 1 og 20, fx 7.")
            continue

        guess = int(guess_str)

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


def play_game():
    get_guess()


play_game()



