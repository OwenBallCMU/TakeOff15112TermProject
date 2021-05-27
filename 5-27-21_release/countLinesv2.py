#Not specifically related to the Term Project
#Just counts the number of lines of code within all Python files in a folder
#Excludes empty lines, multiline comments, and single line comments

import os
import time

#listFiles function from:
#https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#listFiles
def listFiles(path):
    if os.path.isfile(path):
        return [ path ]
    else:
        files = [ ]
        for filename in os.listdir(path):
            files += listFiles(path + '/' + filename)
        return files

#readFile function from:
#https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def countLines(path):
    count = 0
    text = readFile(path)
    inMultiLine = False
    for line in text.splitlines():
        temp = line.lower()
        if '"""' in temp:
            inMultiLine = not inMultiLine
        else:
            #.islower() just checks if there are any letters in the line since 
            #temp.lower() was already called
            if temp.islower() and not "#" in line and not inMultiLine:
                count += 1
                #print(line)
    return count

def countAllLines(path):
    total = 0

    for filePath in listFiles(path):
        #excludes certain files and ensures the file is a .py file
        if filePath.endswith("py") and not (filePath.endswith("cmu_112_graphics_modified.py") or 
                                            filePath.endswith("countLinesv2.py")):
            lines = countLines(filePath)
            print(f"{filePath[len(path)+1:]}: {lines}")
            total += lines
    return total

startTime = time.time()
#os.getcwd gets the directory to the current path
print(countAllLines(os.getcwd()))
#print(1000 * (time.time() - startTime))
