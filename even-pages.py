#!/usr/bin/env python3
import os
import sys
import time
import os.path
import subprocess
'''
NEEDS: pdftk, convert
'''

def defaultOutputName(inputName):
    assert inputName.endswith('.pdf')
    return inputName[:-4] + '_even.pdf'

def processOneFile(inputName, outputName):
    assert inputName.endswith('.pdf')
    assert outputName.endswith('.pdf')

    numPagesProcess = subprocess.Popen(['pdftk', inputName, 'data_dump'], stdout=subprocess.PIPE)
    pdfData = numPagesProcess.stdout.read().decode('utf-8').split('\n')
    numPages = [int(x.split(' ')[-1]) for x in pdfData if x.startswith('NumberOfPages:')][0]
    dimentionsOfLastPage = [x.split(' ')[-2:] for x in pdfData if x.startswith('PageMediaDimensions:')][-1]

    if numPages % 2 == 0:
        subprocess.Popen(['cp', inputName, outputName])
        sys.exit()

    subprocess.Popen(['convert', 'xc:none', '-page', 'x'.join(dimentionsOfLastPage), 'blank.pdf'])
    subprocess.Popen(['pdftk', inputName, 'blank.pdf', 'cat', 'output', outputName])
    time.sleep(0.5)
    os.remove('blank.pdf')

###############

if __name__ == '__main__':
    argumentsInvalid = False
    while True:
        if len(sys.argv) < 2:
            argumentsInvalid = True
            break
        if sys.argv[1] == 'all':
            if len(sys.argv) == 2: argumentsInvalid = True
        else:
            if len(sys.argv) not in {2,3}: argumentsInvalid = True
        break

    if argumentsInvalid:
        print(f'Usage: {sys.argv[0]} INPUT.pdf OUTPUT.pdf')
        print(f'       {sys.argv[0]} INPUT.pdf # INPUT_even.pdf')
        print(f'       {sys.argv[0]} all INPUT.pdf...')
        print('    Make number of pages even by possibly adding a blank last page.')
        sys.exit()

    filesToProcess = []
    if sys.argv[1] == 'all':
        filesToProcess = [[x, defaultOutputName(x)] for x in sys.argv[2:]]
    else:
        filesToProcess = [[sys.argv[1] , sys.argv[2] if len(sys.argv) == 3 else defaultOutputName(sys.argv[1])]]

    for [inputName, outputName] in filesToProcess:
        processOneFile(inputName, outputName)

