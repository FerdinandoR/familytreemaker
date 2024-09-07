import random
import re
import pandas as pd

class Person:
    """
    This class represents a person.

    Characteristics:
    - name            real name of the person
    - id              unique ID to be distinguished in a dictionnary
    - attr            attributes (e.g. gender, birth date...)
    - households      list of households this person belongs to
    - follow_children boolean to tell the algorithm to display this person's
                    descendent or not
    - draw            boolean to determine if the person should be drawn or not

    """

    def __init__(self, arg):
        self.attr = {}
        self.parents = []
        self.households = []
        self.drawn = False

        if isinstance(arg, str):
            self.from_str(arg)

        else:
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

        # Set the id by reading it from the attributes, or generate a new one
        if 'id' in self.attr:
            self.id = self.attr['id']
        else:
            self.id = re.sub('[^0-9A-Za-z]', '', self.name)
            if 'unique' in self.attr:
                self.id += str(random.randint(100, 999))

        # Required to ensure compatibility in tests
        self.attr['spouse'] = ''

        self.follow_children = True

    def from_series(self, row):
        d = dict(row)
        mandatory_args = ('id','name')
        opt_args = ('surname',
                    'sex',
                    'birthplace',
                    'birthday',
                    'deathplace',
                    'deathday',
                    'spouse',
                    'mother',
                    'father',
                    'notes')

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
        return    f'Person: {self.name} ({self.attr})\n' + \
                f' {len(self.households)} households'

    def graphviz(self):
        # If the notes require less than this many characters, write them down,
        # otherwise write a symbol detailing that such notes are present
        # TODO: when we end up building a family tome, this symbol will be
        # replaced by the relevant page number in said tome
        max_notes = 60

        label = 'label="' + self.name
        if 'surname' in self.attr and self.attr['surname'] != '':
            label += f'\\n {self.attr['surname']}'
        if 'birthday' in self.attr and self.attr['birthday'] != '':
            label += f'\\n * {self.attr['birthday']}'
        if 'deathday' in self.attr and self.attr['deathday'] != '':
            label += f'\\n † {self.attr['deathday']}'
        if 'notes' in self.attr and self.attr['notes'] != '':
            if len(self.attr['notes']) <= max_notes:
                label += f'\\n{self.attr['notes']}'
            else:
                label += f'\\n...'
        label += '"'

        sex_color = {'M': "azure2", 'F': 'bisque', 'O': 'green'}
        opts = [label, 
                'style=filled',
                f'fillcolor={sex_color.get(self.attr['sex'], 'white')}']
        return self.id + '[' + ','.join(opts) + ']'
