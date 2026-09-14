import random


MORSE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}


WORD_BANK = [
    "KEY",
    "CODE",
    "LOCK",
    "SECRET",
    "SIGNAL",
    "SHADOW",
    "CIPHER",
    "TOWER",
    "ECHO",
    "MOON",
    "VAULT",
    "RIDDLE",
    "LANTERN",
    "ORACLE",
    "NIGHT",
    "HIDDEN",
    "DOOR",
    "PATH",
    "GLASS",
    "CLOCK",
]


CELEBRATION_TITLES = [
    "THE SILENT SIGNAL",
    "THE HIDDEN MESSAGE",
    "THE LOCKED WORD",
    "THE SECRET LINE",
    "THE VEILED ANSWER",
    "THE NEXT KEY",
    "THE BROKEN SIGNAL",
    "THE WHISPERED CODE",
]


def caesar_encode(text, shift):
    result = ""

    for char in text.upper():
        if char.isalpha():
            base = ord("A")
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char

    return result


def to_binary(text):
    return " ".join(format(ord(char), "08b") for char in text.upper())


def to_morse(text):
    groups = []

    for char in text.upper():
        if char in MORSE:
            groups.append(MORSE[char])

    return "   ".join(groups)


class PuzzleGenerator:
    def __init__(self, seed=330033):
        self.master_seed = seed

    def difficulty_for_page(self, page_number):
        """
        Returns the progression level for this puzzle.

        The level increases with every generated puzzle.
        Individual puzzle families use this value to
        determine how difficult their presentation should be.
        """
        return max(1, page_number)

    def generate(self, page_number):
        """
        Creates a reproducible puzzle for a specific page.

        The same page number will always create the same puzzle
        as long as the master seed stays unchanged.
        """

        if page_number < 1:
            raise ValueError("page_number must be 1 or greater")

        rng = random.Random(self.master_seed + page_number)

        difficulty = self.difficulty_for_page(page_number)

        families = [
            self.generate_morse,
            self.generate_caesar,
            self.generate_binary,
        ]

        # Rotate families while still allowing variation.
        family_index = (page_number - 1) % len(families)
        generator = families[family_index]

        return generator(
            rng=rng,
            page_number=page_number,
            difficulty=difficulty,
        )

    def generate_morse(self, rng, page_number, difficulty):
        word = rng.choice(WORD_BANK)

        display = to_morse(word)

        title = rng.choice(CELEBRATION_TITLES)

        if difficulty <= 3:
            instructions = (
                "Decode the Morse signal shown on the opposite page."
            )

            riddle = (
                "I speak in silence,\n"
                "measured only by length.\n\n"
                "Short and long.\n"
                "Dot and dash.\n\n"
                "Find the word hidden in the signal."
            )

        elif difficulty <= 10:
            instructions = (
                "The marks form a message.\n"
                "Translate the signal and reveal the key."
            )

            riddle = (
                "Distance means nothing to me.\n"
                "I cross darkness without moving.\n\n"
                "My language has only two voices:\n"
                "one brief,\n"
                "one long."
            )

        else:
            instructions = (
                "The signal contains the key.\n"
                "Determine what system is being used and decode it."
            )

            riddle = (
                "Two lengths.\n"
                "One alphabet.\n\n"
                "A message survives\n"
                "even when the voice is gone."
            )

        return {
            "id": f"MORSE-{page_number}",
            "family": "morse",
            "type": "MORSE CODE",
            "title": title,
            "riddle": riddle,
            "instructions": instructions,
            "display": display,
            "answers": [word],
            "answer": word,
            "hints": [
                "Treat each separated cluster as a single letter.",
                "Compare each cluster of dots and dashes to the Morse alphabet.",
                f"The first cluster translates to {word[0]}. Decode the remaining letters.",
            ],
            "difficulty": difficulty,
            "interaction": "text",
        }

    def generate_caesar(self, rng, page_number, difficulty):
        word = rng.choice(WORD_BANK)

        if difficulty <= 5:
            shift = rng.randint(1, 5)
        elif difficulty <= 15:
            shift = rng.randint(3, 12)
        else:
            shift = rng.randint(1, 25)

        encoded = caesar_encode(word, shift)

        title = rng.choice(CELEBRATION_TITLES)

        if difficulty <= 3:
            instructions = (
                f"Each letter has been shifted forward by {shift}.\n"
                f"Shift each letter backward by {shift} to recover the key."
            )

            riddle = (
                "The alphabet has moved,\n"
                "but it has not changed.\n\n"
                "Return every letter\n"
                "to the place from which it came."
            )

        elif difficulty <= 10:
            instructions = (
                "A Caesar shift has concealed the word.\n"
                "Recover the original message."
            )

            riddle = (
                "Rome left more than roads.\n\n"
                "The letters have marched together,\n"
                "each keeping the same distance."
            )

        else:
            instructions = (
                "The alphabet has been displaced.\n"
                "Determine the shift and recover the key."
            )

            riddle = (
                "Every symbol is correct.\n"
                "Every position is wrong.\n\n"
                "Move the alphabet,\n"
                "and the truth returns."
            )

        return {
            "id": f"CAESAR-{page_number}",
            "family": "caesar",
            "type": "CAESAR CIPHER",
            "title": title,
            "riddle": riddle,
            "instructions": instructions,
            "display": encoded,
            "answers": [word],
            "answer": word,
            "hints": [
                "Each letter has been shifted by the same amount through the alphabet.",
                "Try moving every letter backward by a consistent number of positions.",
                f"The shift used for this key is {shift}.",
            ],
            "difficulty": difficulty,
            "interaction": "text",
        }

    def generate_binary(self, rng, page_number, difficulty):
        if difficulty <= 5:
            candidates = [
                "KEY",
                "CODE",
                "LOCK",
                "ECHO",
                "MOON",
            ]
        else:
            candidates = WORD_BANK

        word = rng.choice(candidates)

        encoded = to_binary(word)

        title = rng.choice(CELEBRATION_TITLES)

        if difficulty <= 3:
            instructions = (
                "Each group contains eight binary digits.\n"
                "Convert each byte using ASCII."
            )

            riddle = (
                "Only two symbols remain:\n"
                "one and nothing.\n\n"
                "Yet together they carry letters."
            )

        elif difficulty <= 10:
            instructions = (
                "Translate the binary groups into text."
            )

            riddle = (
                "A machine sees two states.\n"
                "From them it builds language.\n\n"
                "Find the word inside the numbers."
            )

        else:
            instructions = (
                "The sequence contains encoded text.\n"
                "Identify the representation and recover the key."
            )

            riddle = (
                "Light or dark.\n"
                "True or false.\n"
                "Present or absent.\n\n"
                "Two choices become an alphabet."
            )

        return {
            "id": f"BINARY-{page_number}",
            "family": "binary",
            "type": "BINARY / ASCII",
            "title": title,
            "riddle": riddle,
            "instructions": instructions,
            "display": encoded,
            "answers": [word],
            "answer": word,
            "hints": [
                "Treat each eight-digit group as one encoded character.",
                "Convert each 8-bit binary group into its decimal value, then match that value to its ASCII character.",
                f"The first binary group translates to {word[0]}. Decode the remaining groups.",
            ],
            "difficulty": difficulty,
            "interaction": "text",
        }


if __name__ == "__main__":
    generator = PuzzleGenerator()

    for page in range(1, 10):
        puzzle = generator.generate(page)

        print("=" * 60)
        print("PAGE:", page)
        print("TYPE:", puzzle["type"])
        print("TITLE:", puzzle["title"])
        print("DISPLAY:", puzzle["display"])
        print("ANSWER:", puzzle["answers"][0])
        print("DIFFICULTY:", puzzle["difficulty"])