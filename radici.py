#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Adrien Vergé, 2024 Ferdinando Randisi

"""
radici

This program creates family tree graphs from simple text files. Based on
familytreemaker by Adrien Vergé.

The input file format is very simple, you describe persons of your family line
by line, children just have to follow parents in the file. Persons can be
repeated as long as they keep the same name or id. An example is given in the
file LouisXIVfamily.txt.

This script outputs a graph descriptor in DOT format. To make the image
containing the graph, you will need a graph drawer such as GraphViz.

For instance:

$ ./radici.py -a 'Louis XIV' LouisXIVfamily.txt | dot -Tpng -o LouisXIVfamily.png

will generate the tree from the infos in LouisXIVfamily.txt, starting from
Louis XIV and saving the image in LouisXIVfamily.png.

"""

__author__ = "Adrien Vergé, Ferdinando Randisi"
__copyright__ = "Copyright 2013, Adrien Vergé, 2024, Ferdinando Randisi"
__license__ = "GPL"
__version__ = "1.0"

import argparse
from pathlib import Path
import codecs
from family import Family


def main():
    """
    Entry point of the program when called as a script.
    """
    # Parse command line options
    parser = argparse.ArgumentParser(description=
             'Generates a family tree graph from a simple text file')
    parser.add_argument('-a', dest='ancestor',
                        help='make the family tree from an ancestor (if ' +
                        'omitted, the program will try to find an ancestor)')
    parser.add_argument('-d', dest='descendant',
                        help='make the family tree from one or more '
                        'descendants, labelled by their ids, separated by a '
                        'space (optional)')
    parser.add_argument('input', metavar='INPUTFILE',
                        help='the formatted text file representing the family')
    args = parser.parse_args()

    # Create the family
    family = Family()

    # Populate the family
    family.populate(args.input)

    # Find the ancestor from whom the tree is built
    ancestor = []
    if args.ancestor:
        ancestor = family.find_person(args.ancestor)
    elif not args.descendant:
        ancestor = family.find_first_ancestor()

    descendants = []
    if args.descendant:
        d_ids_list = args.descendant.split(' ')

        for d_id in d_ids_list:
            descendants += [family.find_person(d_id)]

    # Output the graph descriptor, in DOT format
    # TODO: the "_a" is added to mark that the family tree was build from an
    # ancestor, as opposed to both ancestor and descendents
    if not args.descendant:
        tree_type = 'a'
    elif not args.ancestor:
        tree_type = 'd'
    else:
        tree_type = 'ad'
    
    dot_out = str(Path(args.input).with_suffix('')) + f'_{tree_type}.dot'
    with codecs.open(dot_out, 'w', 'utf-8') as f:
#        f.writelines([l + '\n' for l in 
#                family.output_descending_tree(ancestor)])
        f.writelines([l + '\n' for l in 
                family.output_tree(ancestor, descendants)])

if __name__ == '__main__':
    main()
