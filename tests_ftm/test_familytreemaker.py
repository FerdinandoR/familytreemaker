# -*- coding: utf-8 -*-
from subprocess import call, check_output
import filecmp

# The source must be surrounded by double quotes (") if it's made of two 
# characters. Single quotes (') WON'T WORK
source_name = '"Louis XIV"'
family_txt = 'LouisXIVfamily.txt'
family_csv = 'LouisXIVfamily.csv'
test_out = 'LouisXIVfamily_a.dot'
ground_truth_file = 'old_LouisXIVfamily_a.dot'
def test_radici_txt():
    '''
    Test the whole familytree script.

    '''

    # Ensure the output stays consistent with the saved one
    check_output(f"python radici.py -a {source_name} {family_txt}")
    gtf = open(ground_truth_file,'r')
    out_f = open(test_out,'r')
    for i, (g,o) in enumerate(zip(gtf.readlines(),out_f.readlines())):
        assert g==o, (f'At line {i+1}:{g=}, while {o=}')


def test_radici_csv():
    '''
    Test the whole familytree script.

    '''

    # Ensure the output stays consistent with the saved one
    check_output(f"python radici.py -a {source_name} {family_csv}")
    gtf = open(ground_truth_file,'r')
    out_f = open(test_out,'r')
    for i, (g,o) in enumerate(zip(gtf.readlines(),out_f.readlines())):
        assert g==o, (f'At line {i+1}:{g=}, while {o=}')
