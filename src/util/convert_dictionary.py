
words = []
with open('words.txt', 'r') as wordfile:
    for line in wordfile:
        word = line[0:23].strip()
        if  len(word) > 2 and len(word) < 6 and \
            not word[0].isupper() and \
            "'" not in word and \
            "_" not in word and `
            "-" not in word:
            words.append(word.replace('^', ''))

with open('converted_words.txt', 'w') as output:
    for word in words:
        print word
        output.write(word + '\n');
