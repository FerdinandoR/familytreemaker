from subprocess import check_output
import filecmp

# The source must be surrounded by double quotes (") if it's made of two characters. Single quotes (') WON'T WORK
source_name = '"Louis XIV"'
family_file = 'LouisXIVfamily.txt'
test_file = 'test.dot'
ground_truth_file = 'LouisXIVfamily_a.dot'
def test_familytree():
    '''
    Test the whole familytree script.

    '''

    # Ensure the output stays consistent with the saved one
    with open(test_file,'wb') as fp:
        lines = check_output(f"python familytreemaker.py -a {source_name} {family_file}")
        print(lines)
        fp.write(lines)
    assert filecmp.cmp(test_file, ground_truth_file)

