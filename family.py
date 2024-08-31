import pandas as pd
from person import Person
from household import Household

class Family:
    """
    Represents the whole family.

    'everybody' contains all persons, indexed by their unique id
    'households' is the list of all unions (with or without children)

    """

    everybody = {}
    households = []

    invisible = '[shape=circle,label="",height=0.01,width=0.01]'

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
        # If not found, raise an error
        raise ValueError(f'Person {name} not found.')

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

    def prev_generation(self, gen):
        '''
        Takes a generation and returns the previous one as a list of people.
        '''

        prev_gen = []

        for p in gen:
            prev_gen += [self.everybody[p.attr[k]] 
                         for k in ('father', 'mother') if p.attr[k] != '']

        return prev_gen

    def get_spouse(household, person):
        """
        Returns the spouse or husband of a person in a union.

        """
        return    household.parents[0] == person \
                and household.parents[1] or household.parents[0]

    def display_generation(self, gen):
        """
        Outputs an entire generation in DOT format.

        """

        ## Display people in a generation, side by side
        dot_lines = ['\t{ rank=same;']

        prev = None
        for i,p in enumerate(gen):
            # Do not draw someone if you have already drawn them as someone's
            # spouse
            if i > 0 and p.id in [pp.attr['spouse'] for pp in gen[:i]]:
                continue
            p.draw = True
            l = len(p.households)

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
                spouse.draw = True
                dot_lines += [f'\t\t{spouse.id} -> h{h.id} -> {p.id};',
				]
    # TODO                            f'\t\th{h.id}{Family.invisible};']

            # Display those on the right (at least one)
            for i in range(int(l/2), l):
                h = p.households[i]
                spouse = Family.get_spouse(h, p)
                spouse.draw = True
                dot_lines += [f'\t\t{p.id} -> h{h.id} -> {spouse.id};',]
                                #f'\t\th{h.id}{Family.invisible};']
                prev = spouse.id
            # TODO:if ascending, add the linking lines properly connecting the
            # brothers and sisters, like you would do above normally.
            # Too tired to do this reliably now.
            ascending = True
            if ascending:
                print(p.id)
                if p.attr['father'] != '':
                    f = self.everybody[p.attr['father']]
                else: continue
                if p.attr['mother'] != '':
                    m = self.everybody[p.attr['mother']]
                else: continue
                h = next((x for x in self.households if x.parents == [f,m]), None)
                siblings = [c.id for c in h.children if c.id != p.id]
                print(p.id, siblings)
                for s in siblings:
                    dot_lines += [f'\t\t{prev} -> {s} [style=invis];']
                    prev = s

            # blablabla 

        dot_lines += ['\t}']

        # Display lines below households
        dot_lines += ['\t{ rank=same;']
        prev = None
        for i, p in enumerate(gen):
            # Do not draw someone if you have already drawn them as someone's
            # spouse
            if i > 0 and p.id in [pp.attr['spouse'] for pp in gen[:i]]:
                continue
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
                    #TODO: dot_lines += [f'\t\th{h.id}_{i}{Family.invisible};']
                    # TODO: this line is never reached in the example, so
                    # can't currently be replaced without risking of messing
                    # everything up
                    # prev = f'h{h.id}_{i}'
                    prev = 'h%d_%d' % (h.id, i)
        dot_lines += ['\t}']

        ## Draw the children and connect them to the lines below the household
        for i, p in enumerate(gen):
            # Do not draw someone if you have already drawn them as someone's
            # spouse
            if i > 0 and p.id in [pp.attr['spouse'] for pp in gen[:i]]:
                continue
            for h in p.households:
                if len(h.children) > 0:
                    dot_lines += [f'\t\th{h.id} -> h{h.id}_'
                                  f'{int(len(h.children)/2)};']
                    i = 0
                    for c in h.children:
                        c.draw = True
                        dot_lines += [f'\t\th{h.id}_{i} -> {c.id};']
                        i += 1
                        if i == len(h.children)/2:
                            i += 1
        return dot_lines

    
    def output_tree(self, ancestors, descendants):
        '''
        Output the family tree as a list of lines.
        '''

        dot_lines = []
        if ancestors != []:
            dot_lines += self.output_descending_tree(ancestors)

        if descendants != []:
            dot_lines += self.output_ascending_tree(descendants)

        header_lines = self.output_header()

        return header_lines + dot_lines

    def output_header(self):
        '''
        Outputs the header, detailing the graph type and the description of
        every box.
    
        '''

        # Print the .dot file header
        dot_lines = ['digraph {',
              '\tnode [shape=box];',
              '\tedge [dir=none];\n']

        # Print the description of everyone's box
        for p in self.everybody.values():
            if p.draw:
                dot_lines += ['\t' + p.graphviz() + ';']
        dot_lines += [f'\tnode{self.invisible}',
                      '']

        return dot_lines

    def output_descending_tree(self, ancestor):
        """
        Outputs the whole descending family tree from a given ancestor,
        in DOT format.

        """
        # Find the first households
        gen = [ancestor]

        # Print each generation
        dot_lines = []
        while gen:
            dot_lines += self.display_generation(gen)
            gen = self.next_generation(gen)

        dot_lines += ['}']
        return dot_lines


    def output_ascending_tree(self, descendant):
        """
        Outputs the whole ascending family tree from a given descendant,
        in DOT format.

        """
        comment = False
        # Find the first households
        try:
            descendant[0]
            gen = descendant
        except:
            gen = [descendant]

        # Print each generation
        dot_lines = []
        print('AAAAAAAAAAAAAAAA')
        if comment:
            dot_lines += ['//Starting descending tree']
        while gen:
            if comment:
                dot_lines += [f'//Generation {[g.id for g in gen]}']
            dot_lines += self.display_generation(gen)
            gen = self.prev_generation(gen)

        dot_lines += ['}']
        return dot_lines
