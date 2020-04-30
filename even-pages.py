#!/usr/bin/env python3

import subprocess, sys, os, os.path, time

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} INPUT.pdf OUTPUT.pdf')
    print('\tMake number of pages even by possibly adding a blank last page.')
    sys.exit()

assert sys.argv[1].endswith('.pdf')
assert sys.argv[2].endswith('.pdf')

numPagesProcess = subprocess.Popen(['pdftk', sys.argv[1], 'data_dump'], stdout=subprocess.PIPE)
pdfData = numPagesProcess.stdout.read().decode('utf-8').split('\n')
numPages = [int(x.split(' ')[-1]) for x in pdfData if x.startswith('NumberOfPages:')][0]
dimentionsOfLastPage = [x.split(' ')[-2:] for x in pdfData if x.startswith('PageMediaDimensions:')][-1]

if numPages % 2 == 0:
    subprocess.Popen(['cp', sys.argv[1], sys.argv[2]])
    sys.exit()

subprocess.Popen(['convert', 'xc:none', '-page', 'x'.join(dimentionsOfLastPage), 'blank.pdf'])
subprocess.Popen(['pdftk', sys.argv[1], 'blank.pdf', 'cat', 'output', sys.argv[2]])
time.sleep(0.5)
os.remove('blank.pdf')

