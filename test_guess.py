import pytest

from guess import generate_secret, get_guess, play_game


def test_generate_secret_within_range():
    low, high = 1, 10
    for _ in range(200):
        secret = generate_secret(low, high)
        assert low <= secret <= high


def test_get_guess_valid_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "5")
    guess = get_guess(1, 10)
    assert guess == 5


def test_get_guess_reprompts_then_accepts(monkeypatch):
    inputs = iter(["hej", "25", "7"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    guess = get_guess(1, 20)
    assert guess == 7


def test_play_game_rejects_invalid_range():
    with pytest.raises(ValueError):
        play_game(low=10, high=1)


def test_play_game_rejects_nonpositive_attempts():
    with pytest.raises(ValueError):
        play_game(max_attempts=0)


def test_play_game_prints_success_message(monkeypatch, capsys):
    # Gør spillet deterministisk ved at fastlåse hemmeligt tal
    monkeypatch.setattr("guess.generate_secret", lambda low, high, rng=None: 7)

    # Simulér brugerinput: korrekt gæt med det samme
    monkeypatch.setattr("builtins.input", lambda _: "7")

    play_game(low=1, high=20, max_attempts=6)

    out = capsys.readouterr().out
    assert "Korrekt!" in out
