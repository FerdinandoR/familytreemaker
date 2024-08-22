#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Adrien Vergé, 2024 Ferdinando Randisi

"""
familytreemaker

This program creates family tree graphs from simple text files.

The input file format is very simple, you describe persons of your family line
by line, children just have to follow parents in the file. Persons can be
repeated as long as they keep the same name or id. An example is given in the
file LouisXIVfamily.txt.

This script outputs a graph descriptor in DOT format. To make the image
containing the graph, you will need a graph drawer such as GraphViz.

For instance:

$ ./familytreemaker.py -a 'Louis XIV' LouisXIVfamily.txt | dot -Tpng -o LouisXIVfamily.png

will generate the tree from the infos in LouisXIVfamily.txt, starting from
Louis XIV and saving the image in LouisXIVfamily.png.

"""

__author__ = "Adrien Vergé, Ferdinando Randisi"
__copyright__ = "Copyright 2013, Adrien Vergé, 2024, Ferdinando Randisi"
__license__ = "GPL"
__version__ = "1.0"

import argparse
import random
import re
import pandas as pd
from pathlib import Path
import codecs


class Person:
	"""
	This class represents a person.

	Characteristics:
	- name			real name of the person
	- id			unique ID to be distinguished in a dictionnary
	- attr			attributes (e.g. gender, birth date...)
	- households	list of households this person belongs to
	- follow_children	boolean to tell the algorithm to display this person's
					descendent or not

	"""

	def __init__(self, arg):
		self.attr = {}
		self.parents = []
		self.households = []

		if isinstance(arg, str):
			self.from_str(arg)

		if isinstance(arg, pd.Series):
			self.from_series(arg)

	def from_str(self, desc):
		desc = desc.strip()
		if '(' in desc and ')' in desc:
			self.name, attr = desc[0:-1].split('(')
			self.name = self.name.strip()
			attr = map(lambda x: x.strip(), attr.split(','))
			for a in attr:
				if '=' in a:
					k, v = a.split('=')
					self.attr[k] = v
				else:
					self.attr['sex'] = a
		else:
			self.name = desc

		if 'id' in self.attr:
			self.id = self.attr['id']
		else:
			self.id = re.sub('[^0-9A-Za-z]', '', self.name)
			if 'unique' in self.attr:
				self.id += str(random.randint(100, 999))

		self.follow_children = True

	def from_series(self, row):
		d = dict(row)
		mandatory_args = ('id',)
		opt_args = ('name',
					'surname',
					'sex',
					'birthplace',
					'birthday',
					'deathplace',
					'deathday',
					'spouse',
					'mother',
					'father')

		# Ensure there are no unknown arguments
		unknown_args = set(d.keys()) - set(mandatory_args + opt_args)
		for arg in unknown_args:
			raise ValueError(f'Unknown argument {arg} when creating person '
					f'from {row}')
		# Ensure all mandatory arguments are present
		for arg in [a for a in mandatory_args if a not in d.keys()]:
			raise ValueError(f'Missing mandatory argument {arg} when creating '
					f' person from {row}')
		
		# populate the arguments
		self.id = d['id']
		self.name = d['name']
		del d['id'], d['name']
		self.attr = d

		# Mark to follow children in family tree
		self.follow_children = True


	def __str__(self):
		return self.name

	def dump(self):
		return	f'Person: {self.name} ({self.attr})\n' + \
				f' {len(self.households)} households'

	def graphviz(self):
		label = self.name
		if 'surname' in self.attr and self.attr['surname'] != '':
			label += '\\n« ' + str(self.attr['surname']) + '»'
		if 'birthday' in self.attr and self.attr['birthday'] != '':
			label += '\\n' + str(self.attr['birthday'])
			if 'deathday' in self.attr and self.attr['deathday'] != '':
				label += ' † ' + str(self.attr['deathday'])
		elif 'deathday' in self.attr and self.attr['deathday'] != '':
			label += '\\n† ' + str(self.attr['deathday'])
		if 'notes' in self.attr and self.attr['notes'] != '':
			label += '\\n' + str(self.attr['notes'])
		opts = ['label="' + label + '"']
		opts.append('style=filled')
		gender_color = {'M': "azure2", 'F': 'bisque', 'O': 'green'}
		opts.append('fillcolor=' + gender_color.get(self.attr['sex'], 'white'))
		return self.id + '[' + ','.join(opts) + ']'

class Household:
	"""
	This class represents a household, i.e. a union of two person.

	Those two persons are listed in 'parents'. If they have children, they are
	listed in 'children'.

	"""

	def __init__(self):
		self.parents = []
		self.children = []
		self.id = 0
	
	def __str__(self):
		return	('Household:\n'
				f'\tparents  = {", ".join(map(str, self.parents))}\n'
				f'\tchildren = {", ".join(map(str, self.children))}')

	def isempty(self):
		if len(self.parents) == 0 and len(self.children) == 0:
			return True
		return False

class Family:
	"""
	Represents the whole family.

	'everybody' contains all persons, indexed by their unique id
	'households' is the list of all unions (with or without children)

	"""

	everybody = {}
	households = []

	invisible = '[shape=circle,label="",height=0.01,width=0.01]';

	def add_person(self, person):
		"""
		Adds a person to self.everybody, or update his/her info if this
		person already exists.

		"""
		key = person.id

		if key in self.everybody:
			self.everybody[key].attr.update(person.attr)
		else:
			self.everybody[key] = person

		return self.everybody[key]

	def add_household(self, h):
		"""
		Adds a union (household) to self.households, and updates the
		family members infos about this union.

		"""
		if len(h.parents) != 2:
			raise ValueError('error: number of parents != 2')

		h.id = len(self.households)
		self.households.append(h)

		for p in h.parents:
			if not h in p.households:
				p.households.append(h)

	def find_person(self, name):
		"""
		Tries to find a person matching the 'name' argument.

		"""
		# First, search in ids
		if name in self.everybody:
			return self.everybody[name]
		# Ancestor not found in 'id', maybe it's in the 'name' field?
		for p in self.everybody.values():
			if p.name == name:
				return p
		return None

	def populate(self, file_name):
		if file_name.split('.')[-1] == 'csv':
			self.populate_csv(file_name)
		else:
			self.populate_txt(file_name)
		
	def populate_txt(self, file_name):
		"""
		Reads the input file line by line, to find persons and unions.

		"""
		with open(file_name, 'r', encoding='utf-8') as f:
			h = Household()
			while True:
				line = f.readline()
				if line == '': # end of file
					if not h.isempty():
						self.add_household(h)
					break
				line = line.rstrip()
				if line == '':
					if not h.isempty():
						self.add_household(h)
					h = Household()
				elif line[0] == '#':
					continue
				else:
					if line[0] == '\t':
						p = self.add_person(Person(line[1:]))
						p.parents = h.parents
						h.children.append(p)
					else:
						p = self.add_person(Person(line))
						h.parents.append(p)

	def populate_csv(self,file_name):
		"""
		Reads a family from a .csv file, populating people and 
		households.
		
		"""
		# Load the .csv into a dataframe
		df = pd.read_csv(file_name, encoding='utf8', keep_default_na=False)

		# Perform some sanity check for the input
		self.check_df(df)
		
		# Read the file line by line
		for i, row in df.iterrows():
			# Add the person to the list of people
			p = Person(row)
			self.add_person(p)
			# Add the households, if the corresponding spouse has already been 
			# inserted
			spouses = ((row.spouse,) if isinstance(row.spouse,str) 
			  else row.spouse)
			if spouses != '':
				for s in spouses:
					if s in self.everybody.keys():
						h = Household()
						h.parents.append(self.everybody[s])
						h.parents.append(p)
						self.add_household(h)

			# Update the households for which one is a child
			if '' not in row[['father','mother']]:
				#TODO: this might be slow. Could be faster if households were a
				# dictionary mapping mother-father tuples to households rather
				# than a list of Household, maybe
				for h in self.households:
					sparents = set(p.id for p in h.parents)
					if (sparents == set(row[['father','mother']]) or 
						sparents == set(row[['mother','father']])):
						h.children.append(p)
						print(f'{h}')

	def check_df(self, df):
		...
			# Check that each identifier is unique
			# Check that if one person lists a second one as their spouse,
			# the second person reciprocates
			# Check that everyone who has a father also has a mother
			# Check that no one is married with themselves
			# Check that no one is introduced before their parents are
			# Check that only genders are F (Female), M (Male), O (Other)

	def find_first_ancestor(self):
		"""Returns the first ancestor found.

		A person is considered an ancestor if he/she has no parents.

		This function is not very good, because we can have many persons with
		no parents, it will always return the first found. A better practice
		would be to return the one with the highest number of descendant.
		
		"""
		for p in self.everybody.values():
			if len(p.parents) == 0:
				return p

	def next_generation(self, gen):
		"""Takes the generation N in argument, returns the generation N+1.

		Generations are represented as a list of persons.

		"""
		next_gen = []

		for p in gen:
			if not p.follow_children:
				continue
			for h in p.households:
				next_gen.extend(h.children)
				# append mari/femme

		return next_gen

	def get_spouse(household, person):
		"""
		Returns the spouse or husband of a person in a union.

		"""
		return	household.parents[0] == person \
				and household.parents[1] or household.parents[0]

	def display_generation(self, gen):
		"""
		Outputs an entire generation in DOT format.

		"""
		# Display persons
		dot_lines = ['\t{ rank=same;']

		prev = None
		for p in gen:
			l = len(p.households)
			print('___gen___')
			print(f'{l=}, {p.name=}')
			for h in p.households:
				print(h)

			if prev:
				if l <= 1:
					dot_lines += [f'\t\t{prev} -> {p.id} [style=invis];']
				else:
					# TODO: this line is never reached when building the
					# default French royal family tree so is not checked.
					# Build a test that checks it.
					dot_lines +=['\t\t%s -> %s [style=invis];'
						  % (prev, Family.get_spouse(p.households[0], p).id)]

			if l == 0:
				prev = p.id
				continue
			elif len(p.households) > 2:
				raise Exception(f'Person "{p.name}" has {len(p.households)} '
								'spouses: drawing more than 2 spouses is not '
								'implemented')

			# Display those on the left (if any)
			for i in range(0, int(l/2)):
				h = p.households[i]
				spouse = Family.get_spouse(h, p)
				dot_lines += [f'\t\t{spouse.id} -> h{h.id} -> {p.id};',
								f'\t\th{h.id}{Family.invisible};']

			# Display those on the right (at least one)
			for i in range(int(l/2), l):
				h = p.households[i]
				spouse = Family.get_spouse(h, p)
				dot_lines += [f'\t\t{p.id} -> h{h.id} -> {spouse.id};',
								f'\t\th{h.id}{Family.invisible};']
				prev = spouse.id
		dot_lines += ['\t}']

		# Display lines below households
		dot_lines += ['\t{ rank=same;']
		prev = None
		for p in gen:
			for h in p.households:
				if len(h.children) == 0:
					continue
				if prev:
					dot_lines += [f'\t\t{prev} -> h{h.id}_0 [style=invis];']
				l = len(h.children)
				if l % 2 == 0:
					# We need to add a node to keep symmetry
					l += 1
				dot_lines += ['\t\t' + 
					' -> '.join(map(lambda x: f'h{h.id}_{x}', range(l))) + 
					';']
				for i in range(l):
					dot_lines += [f'\t\th{h.id}_{i}{Family.invisible};']
					prev = 'h%d_%d' % (h.id, i)
		dot_lines += ['\t}']

		for p in gen:
			for h in p.households:
				if len(h.children) > 0:
					dot_lines += [f'\t\th{h.id} -> h{h.id}_{int(len(h.children)/2)};']
					i = 0
					for c in h.children:
						dot_lines += [f'\t\th{h.id}_{i} -> {c.id};']
						i += 1
						if i == len(h.children)/2:
							i += 1
		return dot_lines

	def output_descending_tree(self, ancestor):
		"""
		Outputs the whole descending family tree from a given ancestor,
		in DOT format.

		"""
		# Find the first households
		gen = [ancestor]

		# Print the .dot file header
		dot_lines = ['digraph {',
		      '\tnode [shape=box];',
		      '\tedge [dir=none];\n']

		# Print the description of everyone's box
		for p in self.everybody.values():
			dot_lines += ['\t' + p.graphviz() + ';']
		dot_lines += ['']

		# Print each generation
		while gen:
			dot_lines += self.display_generation(gen)
			gen = self.next_generation(gen)

		dot_lines += ['}']
		return dot_lines

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
	parser.add_argument('input', metavar='INPUTFILE',
						help='the formatted text file representing the family')
	args = parser.parse_args()

	# Create the family
	family = Family()

	# Populate the family
	family.populate(args.input)

	# Find the ancestor from whom the tree is built
	if args.ancestor:
		ancestor = family.find_person(args.ancestor)
		if not ancestor:
			raise Exception(f'Cannot find person "{args.ancestor}"')
	else:
		ancestor = family.find_first_ancestor()

	# Output the graph descriptor, in DOT format
	# TODO: the "_a" is added to mark that the family tree was build from an
	# ancestor, as opposed to both ancestor and descendents
	dot_out = str(Path(args.input).with_suffix('')) + '_a.dot'
	#dot_out = Path(args.input).with_suffix('_a.dot')
	with codecs.open(dot_out, 'w', 'utf-8') as f:
		f.writelines([l + '\n' for l in 
				family.output_descending_tree(ancestor)])

if __name__ == '__main__':
	main()
