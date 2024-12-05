# Look at wordfrequencies.py
# this is some of the ugliest code I've ever written
FREQUENCIES = {'a': 8.930409487581114, 'b': 2.45468784963079, 'c': 3.322891027075409, 'd': 3.871112105616469, 'e': 10.261803535466548, 'f': 1.7699709107182815, 'g': 2.4949653166256436, 'h': 2.7232042962631464, 'i': 5.902886551801298, 'j': 0.41620049228015216, 'k': 2.1503692101141194, 'l': 5.4643096889684495, 'm': 3.0029089281718506, 'n': 4.549116133363169, 'o': 6.681584247035131, 'p': 3.117028417990602, 'q': 0.1767733273663012, 'r': 6.529424927276796, 's': 10.402774669948535, 't': 5.193555605280824, 'u': 3.8017453569031106, 'v': 1.0651152383083462, 'w': 1.5506824793018572, 'x': 0.46990378160662344, 'y': 3.1394047885432985, 'z': 0.5571716267621392}

# ANSI color codes for terminal text formatting
GREEN = '\033[32m'  # ANSI code for green text
YELLOW = '\033[33m'  # ANSI code for yellow text
RESET = '\033[0m'  # ANSI code to reset text color to default
BOLD = '\033[1m'

def getprobability(word, coolwords):
    x = 0.0
    if word in coolwords: # prioritize common words
        x += 10
    for i, j in FREQUENCIES.items():
        if i in word:
            x += j
    return x

def main():
    with open("FiveLetterWords.txt") as f:
        words= [i.strip() for i in f.readlines()]
    with open("wordle-answers-alphabetical.txt") as f:
        commonwords = [i.strip() for i in f.readlines()]
    playing = True
    possibilities = words
    probabilities = {}
    guess = 'crane'
    includes = []
    excludes = []
    pos = {}
    notpos = {}
    iter = 0
    while playing:
        iter += 1
        print(guess)
        info = input().split(',')
        info = [int(i) for i in info]
        if sum(info) == 50:
            print('ez w')
            break
        formatted = ''
        for i in range(5):
            x = info[i]
            y = guess[i]
            if x == 0:
                excludes.append(y)
                formatted += RESET + y
            elif x == 1:
                includes.append(y)
                if notpos.get(i):
                    notpos[i].append(y)
                else:
                    notpos[i] = [y]
                formatted += YELLOW + y
            elif x == 10:
                includes.append(y)
                pos[i] = y
                formatted += GREEN + y
        print(BOLD + formatted + RESET)
        def exclude(var):
            for i in var:
                if i in excludes:
                    return False
                else:
                    continue
            return True

        def include(var):
            for i in includes:
                if i in var:
                    continue
                return False
            return True

        def posinclude(var):
            for i, j, in pos.items():
                if not var[i] == j:
                    return False
            return True
        def posexclude(var):
            if notpos == {}:
                return True
            for i, j, in notpos.items():
                if var[i] in j:
                    return False
            return True

        dogreens = True
        if (len(pos) > 2 and iter < 5) or iter == 2:
            possibilities = words
            dogreens = False

        possibilities = list(filter(exclude, possibilities))
        possibilities = list(filter(include, possibilities))
        if dogreens:
            possibilities = list(filter(posinclude, possibilities))
        possibilities = list(filter(posexclude, possibilities))
        print(f'probs:{len(possibilities)}')

        probabilities = {}
        for possibility in possibilities:
            probabilities[possibility] = getprobability(possibility, commonwords)
        print(f'probs:{probabilities}')
        guess = max(probabilities, key=lambda k: probabilities[k])

if __name__ == '__main__':
    main()