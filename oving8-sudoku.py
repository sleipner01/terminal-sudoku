# Import libraries to use in the code
from random import sample
import csv
import os
import sys



# Set default variables
def setVariables():
    global fileName
    fileName = 'sudoku.csv'



# Settings and Globals
def setSudokuVariables():
    global base
    base  = 3
    global symbols
    symbols = " 1234567890"
    global side
    side  = base*base
    global board
    board = createBoard()
    hideNumbersInBoard()



# If board is retrieved from file, set settings and globals from this instead
def setSudokuVariablesFromFile(boardFromFile, baseFromFile):
    global base
    base  = baseFromFile
    global symbols
    symbols = " 1234567890"
    global side
    side  = base*base
    global board
    board = boardFromFile



def start():
    print('Welcome to Sudoku!')

    while True:
        hasFile = input('Do you already have a sudoku-board begun? (Yes, No): ')

        if hasFile.lower() == 'yes' : 
            openFile()
            break

        elif hasFile.lower() == 'no':
            setSudokuVariables()
            break
        else: 
            print('You have propably made a typo, try again.')



def createBoard():

    # Function to create pattern for a baseline valid solution
    def pattern(row, column): 
        return (base * (row % base) + row//base + column)%side

    # Randomize rows, columns and numbers (of valid base pattern)
    def shuffle(s): return sample(s,len(s)) 

    rangeOfBase = range(base) 
    rows  = [ group*base + row for group in shuffle(rangeOfBase) for row in shuffle(rangeOfBase) ] 
    cols  = [ group*base + col for group in shuffle(rangeOfBase) for col in shuffle(rangeOfBase) ]
    numbers  = shuffle(range(1,side+1))

    # Produce board using randomized baseline pattern
    board = [ [numbers[pattern(row,column)] for column in cols] for row in rows ]

    return board



# Removing numbers from a valid sudoku board, so that a user can try and create it again. This also allows for multiple solutions
def hideNumbersInBoard():
    squares = side*side
    empties = squares * 3//4 #How many empty places should there be
    for position in sample(range(squares), empties):
        board[position//side][position%side] = 0



def printBoard():

    def expandLine(line):
        return line[0]+line[5:9].join([line[1:5]*(base-1)]*base)+line[9:13]

    # Print structure lines
    line0  = expandLine("╔═══╤═══╦═══╗")
    line1  = expandLine("║ . │ . ║ . ║")
    line2  = expandLine("╟───┼───╫───╢")
    line3  = expandLine("╠═══╪═══╬═══╣")
    line4  = expandLine("╚═══╧═══╩═══╝")

    numbers   = [ [""]+[symbols[number] for number in row] for row in board ]
    print(line0)
    for row in range(1,side+1):
        print( "".join(number+string for number, string in zip(numbers[row-1],line1.split("."))) )
        print([line2,line3,line4][(row%side==0)+(row%base==0)])



def checkUserInput():
    print('Format: m r c v')
    print(f'(Method, Row(1 - {side}), Column(1 - {side}), Value)')
    print()
    print('Add value: a r c v')
    print()
    print('Remove value: r r c')
    print()
    print('Check if you have solved the board by typing "solved".')
    print()
    print('Stop game by writing "stop".')
    print()
    print('____________________________')



    while True:
        instruction = input('What do you want to do? ')

        if instruction.isalpha():
            if instruction.lower() == 'stop':
                saveBoard()
                break

        if instruction.isalpha():
            if instruction.lower() == 'solved':
                if checkIfSolved():
                    break
                else:
                    print("Seems like it wasn't solved, continue...")
                    continue

        
        command = instruction.split(' ')

        # Reducing user input to match with indexes
        row = int(command[1]) - 1
        column = int(command[2]) - 1
        value = int(command[3])

        if(0 <= row < 9 and 0 <= column < 9):
            if command[0].lower() == 'a':
                if 0 < value <= side:
                    addNumber(row, column, value)
                    printBoard()
                else:
                    print(f'The value has to be between 1 and {side}')
                    continue
            if command[0].lower() == 'r':
                removeNumber(row, column)
                printBoard()
        else:
            print('You put in an invalid coordinate')



def addNumber(row, column, number):

    # Check if number is already in the row, column or group

    rows, columns = getRowsAndColumns()
    groups = getGroups()


    # Finding group index
    groupIndex = 0
    if row > (base*2 - 1):
        groupIndex += (base*2)
    elif row > (base-1):
        groupIndex += base
    if column > (base*2 - 1):
        groupIndex += (base-1)
    elif column > (base-1):
        groupIndex += 1



    if number in rows[row]:
        print('The number is already in the row')
        return
    elif number in columns[column]:
        print('The number is already in the column')
        return
    elif number in groups[groupIndex]:
       print('The number is already in the group')
       return
    
    board[row][column] = number


def removeNumber(row, column):
    board[row][column] = 0



def checkIfSolved():

    rowCounter = 0
    columnCounter = 0
    groupCounter = 0

    rows, columns = getRowsAndColumns()
    groups = getGroups()


    # Putting the checks in a while loop
    # If an error is found, quit searching - completely
    loop = True
    while loop:
        # Checks the rows
        for row in rows:
            if len(set(row)) != side: 
                loop = False
                break
            rowCounter += 1

        # Checks the columns
        for column in columns:
            if len(set(column)) != side:
                loop = False
                break
            columnCounter += 1


        for group in groups:
            if len(set(group)) != side:
                loop = False
                break
            groupCounter += 1
        
        loop = False


    # If the loop runs through the whole board without stopping, "counter" will be the same number as the "side" variable
    # This will trigger the function to return True - I.E the sudoku is solved
    # Same for groupCounter 
    if rowCounter == side and columnCounter == side and groupCounter == side:
        print('Congratulations! You solved the board!')

        return True

    return False



def getRowsAndColumns():
    rows = list()
    columns = list()

    for row in range(len(board)):

        rows.append(board[row])

        columnList = list()
        for column in range(len(board)):
            columnList.append(board[column][row])
        
        columns.append(columnList)

    return rows, columns


def getGroups():

    # Really bad code for checking every group for values

    # Say the board is structured like  below, then;
    #
    #   Board
    # 
    #           rowGroup
    #           ╔═══╤═══╦═══╗
    #groupSet   ╢   ╢   ╢   ╢    
    #           ╟───┼───╫───╢
    #           ╢   ╢   ╢   ╢    
    #           ╠═══╪═══╬═══╣
    #           ╢   ╢   ╢   ╢    
    #           ╚═══╧═══╩═══╝
    #
    #
    #   Group
    #
    #           rowValue
    #           ╔═══╤═══╦═══╗
    #groupCol   ╢ 1 ╢ 2 ╢ 3 ╢    
    #           ╟───┼───╫───╢
    #           ╢ 4 ╢ 5 ╢ 6 ╢    
    #           ╠═══╪═══╬═══╣
    #           ╢ 7 ╢ 8 ╢ 9 ╢    
    #           ╚═══╧═══╩═══╝

    allGroups = list()

    groupSet, rowGroup, groupCol, rowValue = 0, 0, 0, 0
    while groupSet < side:
        while rowGroup < side:
            group = []
            while groupCol < base:
                while rowValue < base:
                    group.append(board[groupCol+groupSet][rowValue+rowGroup])
                    rowValue += 1
                groupCol += 1
                rowValue = 0

            allGroups.append(group)

            groupCol = 0
            rowGroup += base
        rowGroup = 0
        groupSet += base

    return allGroups




def saveBoard():
    while True:
        wish = input('Do you want to save the progress? (Yes, No): ')

        if wish.lower() == 'yes' : 
            saveFile()
            break

        elif wish.lower() == 'no':
            break
        else: 
            print('You have propably made a typo, try again.')



def saveFile():
    print('Saving...')

    with open(os.path.join(sys.path[0], fileName), 'w') as file:
        for row in board:
            for value in row:
                file.write(str(value) + ',')
            file.write('\n')
        file.write(str(base))

    print('Board saved successfully')



# If user wants to open file, open it and set the game variables
def openFile():
    with open(os.path.join(sys.path[0], fileName), newline='') as file:
        reader = csv.reader(file)
        gameSettings = list(reader)

    # Convert array-values to integers
    fileBoard = []
    for i in range(len(gameSettings)-1): # Minus one since last value is the base setting
        fileBoard.append([])
        for j in range(len(gameSettings[i])-1): #Minus one because the csv sends an extra empty value in each array
            fileBoard[i].append(int(gameSettings[i][j]))

    fileBase = int(gameSettings[-1][0])


    setSudokuVariablesFromFile(fileBoard, fileBase)



def main():

    setVariables()

    start()

    printBoard()

    checkUserInput()

    print('Thanks for playing. See you soon')

main()