from pynput import mouse
import time
import threading

CAP = 6
LETTERVALUES = {'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4, 'g':2, 'h':4, 'i': 1, 'j':8, 'k':5, 'l':1, 'm':3,
                'n':1, 'o':1, 'p':3, 'q':10, 'r':1, 's':1, 't':1, 'u':1, 'v':4, 'w':4, 'x':8, 'y':4, 'z':10}
TOPRIGHT = []
BOTLEFT = []
QUEUE = []

def game(words, gameLetters):
    # start with priority letters first
    for i in range(4):
        for j in range(4):
            if gameLetters[i][j][2]:
                generateStrings([[i,j]], gameLetters, words)
    for i in range(4):
        for j in range(4):
            if not(gameLetters[i][j][2]):
                generateStrings([[i,j]], gameLetters, words)

def generateStrings(current, gameLetters, words):
    # add current word if valid
    word = []
    for coord in current:
        word.append(gameLetters[coord[0]][coord[1]])

    # checks if word exists and adds to priotrity queue
    checkWord(words, word, current)

    if len(current) == CAP:
        return

    # recursively create new strings
    x = current[-1][0]
    y = current[-1][1]
    if (x - 1 >= 0) and ([x-1,y] not in current):
        generateStrings(current + [[x-1,y]], gameLetters, words)
    if (x - 1 >= 0) and (y + 1 < 4) and ([x-1,y+1] not in current):
        generateStrings(current + [[x-1,y+1]], gameLetters, words)
    if (y + 1 < 4) and ([x,y+1] not in current):
        generateStrings(current + [[x,y+1]], gameLetters, words)
    if (x + 1 < 4) and (y + 1 < 4) and ([x+1,y+1] not in current):
        generateStrings(current + [[x+1,y+1]], gameLetters, words)
    if (x + 1 < 4) and ([x+1,y] not in current):
        generateStrings(current + [[x+1,y]], gameLetters, words)
    if (x + 1 < 4) and (y - 1 >= 0) and ([x+1,y-1] not in current):
        generateStrings(current + [[x+1,y-1]], gameLetters, words)
    if (y - 1 >= 0) and ([x,y-1] not in current):
        generateStrings(current + [[x,y-1]], gameLetters, words)
    if (x - 1 >= 0) and (y - 1 >= 0) and ([x-1,y-1] not in current):
        generateStrings(current + [[x-1,y-1]], gameLetters, words)

def checkWord(words, word, current):
    string = ""
    value = 0
    double = False
    for x in word:
        string += x[0]
        value += x[1]
        if x[2]:
            double = True
    if string in words:
        if double:
            value *= 2
        addWord(current, value)

def addWord(word, value):
    global QUEUE
    i = 0
    while i < len(QUEUE):
        if value <= QUEUE[i][1]:
            QUEUE.insert(i, (word, value))
            return
        i += 1
    QUEUE.insert(i, (word, value))

def getWords():
    file = open("dictionary.txt", 'r')
    words = file.read().split('\n')
    return words

def getLetters():
    letters = input("Enter game letters: ")
    gameLetters = [['']*4, ['']*4, ['']*4, ['']*4]
    i = 0
    count = 0
    while i < len(letters):
        char = letters[i]
        i += 1
        # calculate value and priority of letter
        value = LETTERVALUES[char]
        priority = False
        if i >= len(letters):
            pass
        elif letters[i].isdigit():
            value *= int(letters[i])
            i += 1
        elif letters[i] == '.':
            priority = True
            i += 1
        gameLetters[count//4][count%4] = (char, value, priority)
        count += 1
    return gameLetters

def on_click(x, y, button, pressed):
    global TOPRIGHT, BOTLEFT
    if pressed: 
        TOPRIGHT = [x,y]
    else:
        BOTLEFT = [x,y]
        return False

def getGridLocation():
    print("Click and drag from top right to bottom left of playing grid")
    with mouse.Listener(on_click = on_click) as listener:
        listener.join()
    y = TOPRIGHT[1]
    xGap = (BOTLEFT[0] - TOPRIGHT[0])/3
    yGap = (BOTLEFT[1] - TOPRIGHT[1])/3
    coords = []
    for i in range(4):
        row = []
        x = TOPRIGHT[0]
        for j in range(4):
            row.append((x,y))
            x += xGap
        coords.append(row)
        y += yGap
    return coords

def dragMouse(cont, start, finish):
    xDiff = finish[0] - start[0]
    yDiff = finish[1] - start[1]
    startTime = time.time()
    for i in range(10):
        cont.move(xDiff/10,yDiff/10)
    # ensure 0.05s has passed before continuing word
    while time.time() < startTime + 0.05:
        pass

def drawWord(word, coords):
    cont = mouse.Controller()
    start = coords[word[0][0]][word[0][1]]
    cont.position = start
    cont.press(mouse.Button.left)
    for letter in word[1:]:
        coord = coords[letter[0]][letter[1]]
        dragMouse(cont, cont.position, coord)
    cont.release(mouse.Button.left)

def drawWords(coords):
    try:
        while True:
            global QUEUE
            if len(QUEUE) > 0:
                word = QUEUE.pop()
                drawWord(word[0], coords)
    except KeyboardInterrupt:
        print("Program Finished")

def main():
    words = getWords()
    coords = getGridLocation()
    gameLetters = getLetters()
    # start new thread to draw words
    bot = threading.Thread(target=drawWords, args=(coords,))
    bot.start()
    # find words
    game(words, gameLetters)

main()
