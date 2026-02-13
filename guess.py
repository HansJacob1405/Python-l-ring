import random

secret = random.randint(1, 20)
attempts = 0

print("Jeg tænker på et tal mellem 1 og 20.")

while True:
    guess_str = input("Gæt et tal: ")

    if not guess_str.isdigit():
        print("Skriv et helt tal, fx 7.")
        continue

    guess = int(guess_str)
    attempts += 1

    if guess < secret:
        print("For lavt!")
    elif guess > secret:
        print("For højt!")
    else:
        print(f"Korrekt! Du brugte {attempts} forsøg.")
        break
    
    if attempts > 5:
       print(f"Du har haft {attempts} forsøg hvorfor du ikke får flere forsøg. Det rigtige tal er {secret}")
       break