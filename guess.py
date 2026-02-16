import random


def generate_secret(low: int, high: int, rng: random.Random | None = None) -> int:
    """Generate a secret number in the inclusive range [low, high]."""
    rng = rng or random
    return rng.randint(low, high)


def get_guess(low: int, high: int) -> int:
    """Prompt until the user enters a valid integer in the inclusive range [low, high]."""
    while True:
        text = input(f"Gæt et tal ({low}-{high}): ").strip()

        try:
            guess = int(text)
        except ValueError:
            print(f"Skriv et helt tal mellem {low} og {high}.")
            continue

        if not (low <= guess <= high):
            print(f"Tallet skal være mellem {low} og {high}.")
            continue

        return guess


def play_game(low: int = 1, high: int = 20, max_attempts: int = 6, debug: bool = False) -> None:
    """Run the guessing game."""
    if low > high:
        raise ValueError("low must be <= high")
    if max_attempts <= 0:
        raise ValueError("max_attempts must be >= 1")

    secret = generate_secret(low, high)
    attempts = 0

    print(f"Jeg tænker på et tal mellem {low} og {high}.")
    if debug:
        print(f"[DEBUG] Secret: {secret}")

    while attempts < max_attempts:
        guess = get_guess(low, high)
        attempts += 1

        if guess < secret:
            print("For lavt!")
        elif guess > secret:
            print("For højt!")
        else:
            print(f"Korrekt! Du brugte {attempts} forsøg.")
            return

        remaining = max_attempts - attempts
        if remaining > 0:
            print(f"Du har {remaining} forsøg tilbage.")

    print(f"Du har brugt {max_attempts} forsøg. Det rigtige tal var {secret}.")


if __name__ == "__main__":
    play_game()




