'''
Travis Halleck
6/29/2018
CS 424-01
Python version 3.6.5

The program is a simple lexical analyzer which takes an input file of lexemes
and displays to the screen the token type. The analyzer looks for var names
starting with a letter, integers, semi-colons, assignment symbols (ie += -= *= /=)
and operators (ie + - * /).  Once the lexemes are identified, the token type is
displayed to the screen.  If a symbol is not recognizer an error will be printed
to the screen and the analyzer moves on to the next line

The second part of the program identifies the variables from input file and which
lines they were found.  The results are sent to a file called output.txt
'''

import re
import copy

'''
Starting point of program, enter text file you would like to analyze
'''
nameOfFile = input("type the name of the file you wish to parse \n")
#nameOfFile = "testFile1.txt"

'''
#Regex that locates all operators, either single or += *= -= type of operators
#ident regex looks for variables starting with a letter, or _ followed by numbers
#but is optional, with no spaces
#int_regex looks for integers only in a string, 45Ab71 would fail, 4490 would pass
#only letters regex checks for only english letters, this regex is used to detect 
'''

operators_regex = re.compile(r"([+=|\-=|\/=|*=]{2})|([+-/*=;]{1})")
ident_regex = re.compile(r"\b[\_]?([A-Za-z][^\W]{0,})")
int_regex = re.compile(r"(?<!\S)[0-9]{0,}[0-9]{1,}(?!\S)")
only_letters_regex = re.compile(r"(?<!\S)[a-zA-Z]{1,}[a-zA-Z]{0,}(?!\S)")

'''
readStoreFilterFunc 
#Takes in a text file, reads it line by line, strips the ending backslash n
#Finds spaces, collapses the spaces so there is none to ensure content
#in lines are bunched up and consistent, then adds space before and after an operator
#is found, and lastly trims space on both ends and saves to an array (list)
'''

def readStoreFilterFunc(fileName):
    arr = []
    with open(fileName) as file:
        line = file.readline()
        while line:
            line = line.rstrip('\n')
            line = line.replace(" ", "")
            line = re.sub(operators_regex, r' \1 \2 ', line)
            line = line.strip()
            arr.append(line)
            line = file.readline()

    arr = list(filter(None, arr))
    return arr

fileArry = readStoreFilterFunc(nameOfFile)

'''
#make copy of the fileArry so I can do print to screen with the identifiers on list
#while the other list i can do the symbol table
'''
fileArryCopy = []
fileArryCopy = copy.deepcopy(fileArry)

'''
getIdentifiersArrForScreen
This function has a dual purpose.  Using the regular expressions it searches out the 
appropriate pattern and replaces the arr text from lexemes to tokens.  The last part is
combs through each substring to see if any symbols are unrecognized and overwrites the 
arr elem to store an error message.  The other part of the function stores an additional
arry with all of the tokens, which is used later to check for the word ERROR so the
eventual output file doesn't get that data
'''
def getIdentifiersArrForScreen(arr):
    idArrForScreen = []
    for i in range(0, len(arr)):
        arr[i] = re.sub(ident_regex, "IDENT", arr[i])
        arr[i] = arr[i].replace("+=", "ASSIGNOP").replace("-=", "ASSIGNOP").replace("*=", "ASSIGNOP").replace("/=",
                                                                                                          "ASSIGNOP")
        arr[i] = arr[i].replace(";", "TERM")
        arr[i] = arr[i].replace("+", "ADDOP").replace("-", "ADDOP").replace("*", "MULTIOP").replace("/", "MULTIOP")
        arr[i] = arr[i].replace("=", "ASSIGNOP")
        arr[i] = re.sub(int_regex, "INT", arr[i])

        m = arr[i].split(" ")
        for x in m:
            if not re.match(only_letters_regex, x) and x != '':
                arr[i] = "ERROR"
                break;

            if re.match("ASSIGNOPASSIGNOP", x):
                arr[i] = "ERROR"
                break;

        arr[i] = str(i+1) + ": " + arr[i]
        print(arr[i])
        idArrForScreen.append(arr[i])
    return idArrForScreen

idArryForScreen = getIdentifiersArrForScreen(fileArryCopy)

'''
getLargeVar
The only purpose of this function is to return which variable has the longest
string length, which is used later for left and right align formating later
for the output file
'''
def getLargeVar(arr):
    largestVar = 0
    for i in range(0, len(arr)):
        if len(str(arr[i])) > largestVar:
            largestVar = len(arr[i])
    return largestVar

'''
This function takes the variables found in the original file and stores in an arr, checks
for uniqueness.
'''
def createUniqueVarsArr(arr):
    myVarsArr = []
    for i in range(0, len(arr)):
        arrSplit = arr[i].split(" ")
        for x in range(0, len(arrSplit)):
            if re.search(ident_regex, arrSplit[x]):
                tempName = arrSplit[x]
                if tempName in myVarsArr:
                    continue
                else:
                    myVarsArr.append(tempName)
    return myVarsArr

varsArr = createUniqueVarsArr(fileArry)
largestVar = getLargeVar(varsArr)


'''
Constructs the symbol table for output file.  Using the unique variable arr from
earlier, this function checks that against the the file array, every line. If that
variable was found on that line, the lineNumber is appended to the line array.  In
addition to checking every line of the fileArr, if an ERROR is found, the line is 
skipped all together. 
'''
def constructSymbolTable(idArr, theFileArr):
    symbolTable = {}
    for i in range(0, len(idArr)):
        lineArr = []
        lineNum = 0
        while lineNum < len(theFileArr):
            if re.search(idArr[i], theFileArr[lineNum]) and not re.search("ERROR", idArryForScreen[lineNum]):
                lineArr.append(lineNum+1)
            lineNum += 1
        if len(lineArr) > 0:
            symbolTable[varsArr[i]] = lineArr
        else:
            continue

    return symbolTable

mySymbolTable = constructSymbolTable(varsArr, fileArry)

'''
Contents of symbol table dictionary is dumped to output file, but first
the dictionary is sorted via the keys (variable names).  Formatting is done
here also.
'''

with open("output.txt", "w") as outputFile:
    outputFile.write('%*s %*s\n\n' % (-(largestVar+1), "id", 2, "lines"))
    for k in sorted(mySymbolTable.keys()):
        line = '%*s %*s' % (-(largestVar+1), str(k), 2, str(mySymbolTable[k]))
        outputFile.write(line + '\n')


'''
SPECIAL NOTE
Please note, if an error was at all discovered previously, the
entire line is skipped and that variable will not be recorded on the lines.
For example if A3 is found in lines 1, 3, 4, and 7, but an ERROR occured
in line 3, then A3 will display A3 [1, 4, 7] even though A3 was on line 3

The instructions wasn't clear on whether or not to keep the variable up to the
point of the error, or if an error is discovered at all, negate that entire line.
So I choose the later.
'''