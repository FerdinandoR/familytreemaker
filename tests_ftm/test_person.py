import pytest
import pandas as pd
from ..person import Person

ettore = pd.Series({'id': '1906EMajorana',
                    'name': 'Ettore',
                    'surname': 'Majorana',
                    'sex': 'M',
                    'birthplace': 'Catania',
                    'birthday': '1906-08-05',
                    'deathplace': 'Mazara del Vallo',
                    'deathday': '1938-03-27',
                    'spouse': '',
                    'mother': 'DCorso',
                    'father': 'FMajorana',
                    'notes': 'Great theoretical physicist.'})

def test_from_series():
    '''
    Test the constructor from Series and dict-like objects.
    '''

    # Sanity check arguments
    err_dicts = {
        "Unknown argument": (
            {'favourite football team': 'Italy'}, # Catches unknown arguments
        ),
        "Missing mandatory argument": (
            {'name': 'a'}, # missing mandatory argument 'id'
            {'id': 'a'}, # missing mandatory argument 'name'
        )
    }
    for message_piece,args in err_dicts.items():
        for arg in args:
            with pytest.raises(ValueError) as e:
                Person(arg)
            assert message_piece in str(e)

    # Correctly populates the members and attributes
    p = Person(ettore)
    members = ('id', 'name')
    for m in members:
        assert p.__dict__[m] == ettore[m], (
            f'Wrong member {m}: {p.__dict__[m]} was assigned, should '
            f'have been {ettore[m]}')
    for k,v in ettore.items():
        if k not in members:
            assert p.attr[k] == ettore[k], (f'Wrong attribute {k}: {p.attr[k]} '
                                        f'was assigned, should have been {v}')

# Move the 'args' series to the namespace, call it ettore, and also use it to
# build the test functions for str, dump, graphviz functions.
def test_str():
    '''
    Test the __str__ method.
    '''
    assert str(Person(ettore)) == ettore['name']

def test_dump():
    '''
    Test the dump method.
    '''
    p = Person(ettore)
    dump = f'Person: {p.name} ({p.attr})\n' + \
                f' {len(p.households)} households'
    assert p.dump() == dump

def test_graphviz():
    '''
    Test the graphviz method.
    '''

    # Here ettore['name'] must be used rather than ettore.name as that
    # is a reserved member of a Series. See 
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.name.html

    # Complete label
    sex_color = {'M': "azure2", 'F': 'bisque', 'O': 'green'}
    label = [f'{ettore.id}',
             f'[label="{ettore['name']}',
             f'\\n {ettore.surname}',
             f'\\n * {ettore.birthday}',
             f'\\n † {ettore.deathday}',
             f'\\n{ettore.notes}',
             '",style=filled,',
             f'fillcolor={sex_color.get(ettore.sex, 'white')}]']
    assert ''.join(label) == Person(ettore).graphviz()
    # TODO: keep working on these tests to cover more cases - boring, but 
    # you'll be glad you did that later. Of course you should also implemented
    # birthplaces and deathplaces.
    # Lines skipped
    labels_lines = {2: 'surname',
                    3: ['birthplace','birthday'],
                    4: ['deathplace','deathday'],
                    5: 'notes'}
    for i, labels in labels_lines.items():
        this_label = [s for j,s in enumerate(label) if j != i]
        dropped_s = ettore.drop(labels=labels)
        assert ''.join(this_label) == Person(dropped_s).graphviz(),(i,labels)