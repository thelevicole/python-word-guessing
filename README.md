# Python word guessing game
This "game" will ask you to think of a word, it will then attempt to guess your word by asking you a set of questions. Words are limited to ones listed in `dictionary.txt` but it should be ok there are 25,344 to guess from. ¯\\_(ツ)_/¯

## Playing the game
You can start the "game" in its default mode by running:
```bash
python3 game.py
```
This can also be run in "debug mode" by adding the debug argument:
```bash
python3 game.py --debug
```
## Example dialog
The game/experience will go something like:

> Think of a word with a length between {min} and {max}

*User enters the length of their word (e.g. orchard = `7`)*

> How many times does the letter "r" occur in your word?

*Users answers with an integer (e.g. `2`)*

**Repeats until a word can be guessed**
