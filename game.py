import time
import random
import argparse

# Get commandline arguments
parser = argparse.ArgumentParser(description = 'Attempt to guess a word you are thinking of.')
parser.add_argument('--debug', dest='debug', action='store_true')
parser.set_defaults(debug = False)
args = parser.parse_args()

# Adhoc variables
words		= open('dictionary.txt').read().lower().splitlines()
alphabet	= list('eariotnslcudpmhgbfywkvxzjq') # Alphabet in order of most used
example		= random.choice(words)	# Choose a random word as an example
success		= None					# False for failed, string for success, None for no guesses
wrong		= []					# Store characters that are NOT in the users word
correct		= {}					# Store characters that are in the word and how many times they occur
guesses		= 0						# Keep track of how many questions are asked

# Get the minimum and maximum word lengths
minimum = len( min(words, key = len) )
maximum = len( max(words, key = len) )

#
# Check if user input is boolean
#
# @param	string	question	Question that will be printed to the user
# @return	boolean
#
def check(question):
	response = input(question + ' [Yes/no] ')
	return response.lower() in ['y', 'yes', '1', 'true']

#
# Debug helper, only prints string if debug argument is passed
#
# @param	mixed	to_print
# @return	void
#
def debug(to_print):
	if args.debug:
		print(to_print)

#
# Spoof loading interface
#
# @param 	int		length	The number of times to repeat symbol
# @param	float	timeout	Timeout between each print
# @param	string	symbol	Symbol to print to screen
# @return	void
#
def loading(length = 3, timeout = 0.1, symbol = '.'):
	if not args.debug:
		string = ''
		for i in range(0, length):
			string += symbol
			time.sleep(timeout)
			print(string)

#
# Filter words that have characters matching correct guesses
# and characters that do not match wrong guesses
#
# @return	list	A filtered list of global variable `words`
#
def filter_words():

	filtered = []

	for index, word in enumerate(words):
		check_correct = True
		check_wrong = False

		for char, count in correct.items():
			if word.count(char) is not count:
				check_correct = False

		for char in wrong:
			if char in word:
				check_wrong = True

		delete = True if not check_correct or check_wrong else False

		debug('[%s] correct=%s wrong=%s delete=%s' % (word, check_correct, check_wrong, delete))

		if not delete:
			filtered.append(word)

	return filtered


#
# Filter alphabet of characters that don't appear in the words list
#
# @return	void
#
def filter_alphabet():
	global alphabet
	global wrong

	for char in alphabet:
		in_word = False
		for word in words:
			if char in word:
				in_word = True

		debug('[%s] %s used' % (char, 'is' if in_word else 'is not'))

		if not in_word:
			alphabet.remove(char)
			if char not in wrong:
				wrong.append(char)

#
# Ask the user for their word length and confirm, repeat if wrong
#
# @param	boolean		confirm		Run confirmation check if True
# @return	integer
#
def ask_for_length(confirm = True):
	word_length = None

	# Loop untile word_lenght is valid
	while word_length is None or word_length > maximum or word_length < minimum:

		# If length is invalid, print helper text
		if word_length is not None:
			print('Your word should have a length between %d and %d' % (minimum, maximum))

		# Store users input
		word_length = int( input('Enter your word length here: ') )

	# Confirm the users input
	if confirm:
		confirmed = False
		while not confirmed:
			confirmed = check('You entered "%d", is that correct?' % word_length)
			if not confirmed:
				word_length = ask_for_length(False)

	return word_length

# Print debug helpers
debug('--- Playing in debug mode ---')

#
# Start game with a nice introducition
#
print('''
I will be attempting to guess a word you are thinking of!
All you have todo is think of a word with a length between %d and %d

For example: %s (length: %d)
''' % (minimum, maximum, example, len(example)))

# Get users word length
word_length = ask_for_length()

#
# Lets get guessing
#
print('Great! Lets get started.')
loading()

# Filter words by length matching users input (`word_length`)
words = [word for word in words if len(word) is word_length]

# Cycle through `alphabet` until we can guess the word
while success is None:

	# Count how many characters we have to work with
	total_chars = 0
	for char, count in correct.items():
		total_chars += count

	# If we have used all available characters, add remaing alphabet to wrong list
	if total_chars is word_length:
		wrong.extend(alphabet)
		alphabet = []

	# Check if we have any letters left in the alphabet
	if alphabet:

		# Incriment guess counter
		guesses += 1

		# Get next character to check
		next_char = alphabet.pop(0)

		# Ask the user if this character is in their word
		if check('Is the letter "%s" in your word? ' % next_char):
			# If so, ask how many times
			count = int( input('Nice! How many times does "%s" occur in your word? ' % next_char) )
			correct[next_char] = count
		else:
			wrong.append(next_char)

	# Update words list now we know what characters are/not in the word
	words = filter_words()

	# Update alphabet to reflect words list
	filter_alphabet()

	# Print loading UI
	loading()

	# Print stats
	debug('-' * 60)
	debug('Words(%d): %s' % (len(words), words))
	debug('Alphabet(%d): %s' % (len(alphabet), alphabet))
	debug('Correct(%d): %s' % (len(correct), correct))
	debug('Wrong(%d): %s' % (len(wrong), wrong))
	debug('-' * 60)

	# Check if we are ready to make a guess
	if len(words) is 1 or not alphabet:

		if words:
			success = check('Is your word "%s"?' % words[0])
			if success:
				print('Woohoo! I had to ask you %d question(s) before I got the correct answer.' % guesses)
			else:
				print('Oh no! You have outsmarted me!')
		else:
			success = False
			print('I ran out of words, you win!')

		continue




