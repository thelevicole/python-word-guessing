import time
import random
import argparse
import collections

# Get commandline arguments
parser = argparse.ArgumentParser(description = 'Guess a word or have the computer guess yours.')
parser.add_argument('--debug', dest='debug', action='store_true')
parser.set_defaults(debug = False)
args = parser.parse_args()

def check(question):
	response = input('%s [Yes/no] ' % question)
	return response.lower() in ['y', 'yes', '1', 'true']

def integer(question):
	try:
		return int( input('%s ' % question) )
	except ValueError:
		print('Please enter a valid number.')
		return False

def debug(to_print):
	if args.debug:
		print(to_print)

def loading(length = 3, timeout = 0.1, symbol = '.'):
	if not args.debug:
		string = ''
		for i in range(0, length):
			string += symbol
			time.sleep(timeout)
			print(string)

# ----------------------------------------------------
# REPLIER MODE (Computer guesses player's word)
# ----------------------------------------------------
def play_as_replier(all_words):
	words = list(all_words)
	alphabet = list('abcdefghijklmnopqrstuvwxyz')
	example = random.choice(words)
	success = None
	wrong = []
	correct = {}
	guesses = 0

	minimum = len(min(words, key = len))
	maximum = len(max(words, key = len))

	def filter_words():
		filtered = []
		for word in words:
			check_correct = all(word.count(char) == count for char, count in correct.items())
			check_wrong = any(char in word for char in wrong)
			if check_correct and not check_wrong:
				filtered.append(word)
		return filtered

	def order_alphabet():
		nonlocal alphabet
		combined = ''.join(words)
		common_2d = collections.Counter(combined).most_common()
		common_list = [char[0] for char in common_2d]
		ordered = [char for char in alphabet if char in common_list]
		ordered.extend([char for char in alphabet if char not in ordered])
		alphabet = ordered

	def filter_alphabet():
		nonlocal alphabet, wrong
		for char in list(alphabet):
			in_word = any(char in word for word in words)
			if not in_word:
				alphabet.remove(char)
				if char not in wrong:
					wrong.append(char)
		order_alphabet()

	def ask_for_length(confirm = True):
		word_length = False
		while word_length is False or word_length > maximum or word_length < minimum:
			if word_length is not False:
				print('Your word should have a length between %d and %d' % (minimum, maximum))
			word_length = integer('Enter your word length here:')

		if confirm:
			confirmed = False
			while not confirmed:
				confirmed = check('You entered "%d", is that correct?' % word_length)
				if not confirmed:
					word_length = ask_for_length(False)
		return word_length

	print('''\nI will attempt to guess your word!
Think of a word with a length between %d and %d.
Example: %s (length: %d)''' % (minimum, maximum, example, len(example)))

	word_length = ask_for_length()
	print('Great! Lets get started.')
	loading()

	words = [w for w in words if len(w) == word_length]
	order_alphabet()

	while success is None:
		total_chars = sum(correct.values())
		if total_chars == word_length:
			wrong.extend(alphabet)
			alphabet = []

		if alphabet:
			guesses += 1
			next_char = alphabet[0]
			count = integer('How many times does "%s" occur in your word?' % next_char)
			if count is False:
				continue

			if count > 0:
				correct[next_char] = count
			else:
				wrong.append(next_char)
			alphabet.remove(next_char)

		words = filter_words()
		filter_alphabet()
		loading()

		if len(words) == 1 or not alphabet:
			if words:
				success = check('Is your word "%s"?' % words[0])
				if success:
					print('Woohoo! I guessed it in %d questions.' % guesses)
				else:
					print('Oh no! You outsmarted me!')
			else:
				success = False
				print('I ran out of words, you win!')

# ----------------------------------------------------
# ASKER MODE (Custom Guesses, Shorthand & Hint System)
# ----------------------------------------------------
ACTION_MAPPING = {
    'l': 'letter', 'letter': 'letter', '1': 'letter',
    'w': 'word', 'word': 'word', '2': 'word',
    'h': 'hint', 'hint': 'hint', '3': 'hint'
}

def configure_max_guesses():
	"""Prompts user to select guess limit: 0 (Sudden Death), 1-10, or U (Unlimited)."""
	while True:
		user_input = input('Set maximum allowed wrong guesses [0 = Sudden Death, 1-10, or U = Unlimited]: ').strip().lower()
		
		if user_input in ['u', 'unlimited', 'none']:
			print('Difficulty Mode: UNLIMITED GUESSES (Sandbox)')
			return None  # None indicates unlimited mode
		
		if user_input.isdigit():
			val = int(user_input)
			if val == 0:
				print('Difficulty Mode: SUDDEN DEATH (1 wrong guess allowed)')
				return 1
			elif 1 <= val <= 10:
				print(f'Difficulty Mode: {val} WRONG GUESSES ALLOWED')
				return val
		
		print('Invalid selection. Please enter 0 for Sudden Death, a number between 1 and 10, or U for Unlimited.')

def play_as_asker(all_words):
	secret_word = random.choice(all_words)
	guessed_letters = set()
	wrong_guesses = 0
	
	print('\n--- You are guessing my word! ---')
	max_wrong = configure_max_guesses()
	print('My secret word is %d letters long.' % len(secret_word))

	while True:
		display = "".join([char if char in guessed_letters else "_" for char in secret_word])
		print('\nWord: %s' % display)

		if "_" not in display:
			print('🎉 Congratulations! You guessed the word: "%s"' % secret_word)
			break

		if max_wrong is not None and wrong_guesses >= max_wrong:
			print('❌ Out of guesses! The word was: "%s"' % secret_word)
			break

		action_input = input('Action: (L)etter, Full (W)ord, or (H)int? [L/w/h]: ').strip().lower()
		action = ACTION_MAPPING.get(action_input, 'letter') if action_input else 'letter'

		if action == 'hint':
			unrevealed = [c for c in secret_word if c not in guessed_letters]
			if not unrevealed:
				print('All letters are already revealed!')
				continue
			
			vowels = [c for c in unrevealed if c in 'aeiou']
			hint_char = random.choice(vowels) if vowels else random.choice(unrevealed)
			
			guessed_letters.add(hint_char)
			if max_wrong is not None:
				wrong_guesses += 1
				print('💡 HINT: The letter "%s" is in the word! (Cost: 1 Strike)' % hint_char)
				print(f'Current Strikes: {wrong_guesses}/{max_wrong}')
			else:
				print('💡 HINT: The letter "%s" is in the word! (Unlimited Mode - No Penalty)' % hint_char)

		elif action == 'word':
			full_guess = input('Enter your full word guess: ').strip().lower()
			if full_guess == secret_word:
				print('🎉 Spot on! You guessed the full word correctly: "%s"' % secret_word)
				break
			else:
				if max_wrong is not None:
					wrong_guesses += 1
					print(f'Incorrect word guess! Strikes: {wrong_guesses}/{max_wrong}')
				else:
					print('Incorrect word guess!')
		else:
			guess = input('Guess a letter: ').strip().lower()

			if len(guess) != 1 or not guess.isalpha():
				print('Please enter a single letter.')
				continue

			if guess in guessed_letters:
				print('You already guessed "%s". Try again.' % guess)
				continue

			guessed_letters.add(guess)

			if guess in secret_word:
				print('Good choice! "%s" is in the word.' % guess)
			else:
				if max_wrong is not None:
					wrong_guesses += 1
					print(f'Incorrect! Strikes: {wrong_guesses}/{max_wrong}')
				else:
					print('Incorrect letter guess!')

# ----------------------------------------------------
# MAIN MENU (Shorthand Supported)
# ----------------------------------------------------
MENU_MAPPING = {
    '1': 'asker', 'a': 'asker', 'asker': 'asker',
    '2': 'replier', 'r': 'replier', 'replier': 'replier',
    '3': 'quit', 'q': 'quit', 'quit': 'quit', 'exit': 'quit'
}

def main():
	try:
		with open('dictionary.txt', 'r') as f:
			all_words = f.read().lower().splitlines()
	except FileNotFoundError:
		print("Error: 'dictionary.txt' file not found.")
		return

	if args.debug:
		print('--- Playing in debug mode ---')

	while True:
		print('\n=== WORD GUESSING GAME ===')
		print('(1/A)sker   - You guess the computer\'s word')
		print('(2/R)eplier - Computer guesses your word')
		print('(3/Q)uit    - Exit game')
		
		raw_choice = input('Select game mode [1/2/3 or A/R/Q]: ').strip().lower()
		choice = MENU_MAPPING.get(raw_choice)

		if choice == 'asker':
			play_as_asker(all_words)
		elif choice == 'replier':
			play_as_replier(all_words)
		elif choice == 'quit':
			print('Thanks for playing!')
			break
		else:
			print('Invalid selection. Please enter 1/A, 2/R, or 3/Q.')

if __name__ == "__main__":
	main()