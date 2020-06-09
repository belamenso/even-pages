#!/usr/bin/env python3
import os
import sys
import time
import os.path
import subprocess
from pprint import pprint
import os.path
from math import ceil
from termcolor import colored
'''
NEEDS: pdftk, convert
'''


def defaultOutputName(inputName):
    assert inputName.endswith('.pdf')
    return inputName[:-4] + '_even.pdf'


def isFile(fname):
    return os.path.isfile(fname)


def removeLastPage(inputName, outputName):
    assert inputName.endswith('.pdf')
    assert outputName.endswith('.pdf')
    subprocess.Popen(['pdftk', inputName, 'cat', '1-r2', 'output', outputName])


def processOneFile(inputName, outputName, pdfPagesPerPhysicalPage=1):
    assert inputName.endswith('.pdf')
    assert outputName.endswith('.pdf')
    assert isFile(inputName)
    assert not isFile(outputName)
    assert type(1) == type(pdfPagesPerPhysicalPage) and pdfPagesPerPhysicalPage >= 1
    ppp = pdfPagesPerPhysicalPage

    numPagesProcess = subprocess.Popen(['pdftk', inputName, 'data_dump'], stdout=subprocess.PIPE)
    pdfData = numPagesProcess.stdout.read().decode('utf-8').split('\n')
    numPages = [int(x.split(' ')[-1]) for x in pdfData if x.startswith('NumberOfPages:')][0]
    dimentionsOfLastPage = [x.split(' ')[-2:] for x in pdfData if x.startswith('PageMediaDimensions:')][-1]
    rotation = [int(x.split(' ')[-1]) for x in pdfData if x.startswith('PageMediaRotation:')][-1]
    assert rotation in {0, 90}

    physicalPagesProduced = int(ceil(numPages / ppp))
    if physicalPagesProduced % 2 == 0:
        subprocess.Popen(['cp', inputName, outputName])
        return

    subprocess.Popen(['convert', 'xc:none', '-page', 'x'.join(dimentionsOfLastPage if rotation == 0 else dimentionsOfLastPage[::-1]), 'blank.pdf'])
    subprocess.Popen(['pdftk', inputName] + (['blank.pdf'] * ppp) + ['cat', 'output', outputName])
    time.sleep(0.5)
    os.remove('blank.pdf')


###############


def validFileNames(fnames): # AssertionError(str) | None
    for fname in fnames:
        if not fname.endswith('.pdf'):
            raise ValueError(f'File "{fname}" doesn\'t end with ".pdf"')
        if not isFile(fname):
            raise ValueError(f'File "{fname}" doesn\'t exist')
        if isFile(defaultOutputName(fname)):
            raise ValueError(f'File "{defaultOutputName(fname)}" already exists')


def parseArgs(): # -> AssertionError(str) | (int|None, [str])
    if len(sys.argv) <= 1: raise ValueError('Too few args')
    assert len(sys.argv) >= 2

    if sys.argv[1] == 'remove_last':
        if len(sys.argv) == 2: raise ValueError('Too few args')
        args = sys.argv[2:]
        validFileNames(args)
        return None, args

    elif sys.argv[1].startswith('ppp') and sys.argv[1][3:].isdigit():
        ppp = int(sys.argv[1][3:])
        if not (ppp >= 1): raise ValueError('ppp must be >= 1')
        if len(sys.argv) == 2: raise ValueError('Too few args')
        args = sys.argv[2:]
        validFileNames(args)
        return ppp, args

    else:
        args = sys.argv[1:]
        validFileNames(args)
        return None, args


if __name__ == '__main__':
    try:
        ppp, fnames = parseArgs()
        if ppp is None: ppp = 1
    except ValueError as e:
        print(f'Usage: {sys.argv[0]} IN.pdf ...')
        print(f'       {sys.argv[0]} ppp2 IN.pdf ...')
        print(f'       {sys.argv[0]} remove_last IN.pdf ...')
        print(f'    Make number of pages even by possibly adding (removing) a blank last page, ppp pages per physical page.')
        print()
        print('Reason for rejection of parameters:', colored(str(e.args[0]), 'red'))
        print()
        raise

    # XXX still ugly, why is parsing arguments in two places at once? This remove last is weird

    if sys.argv[1] == 'remove_last':
        for fname in fnames:
            removeLastPage(fname, defaultOutputName(fname))
    else:
        for fname in fnames:
            processOneFile(fname, defaultOutputName(fname), ppp)

