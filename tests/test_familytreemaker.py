# -*- coding: utf-8 -*-
from subprocess import check_output
import filecmp

# The source must be surrounded by double quotes (") if it's made of two 
# characters. Single quotes (') WON'T WORK
source_name = '"Louis XIV"'
family_file = 'LouisXIVfamily.txt'
test_out = 'test.dot'
ground_truth_file = 'LouisXIVfamily_a.dot'
def test_familytreemaker():
    '''
    Test the whole familytree script.

    '''

    # Ensure the output stays consistent with the saved one
    with open(test_out,'wb') as fp:
        lines = check_output(f"python familytreemaker.py -a" 
                             f"{source_name} {family_file}")
        print(lines)
        fp.write(lines)
    assert filecmp.cmp(test_out, ground_truth_file), (
        f"Output file {test_out} and {ground_truth_file} differ."
    )

