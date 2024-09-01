# -*- coding: utf-8 -*-
import pytest
import pandas as pd
from ..family import Family

def test_check_df():
    '''
    Test that all errors are properly caught.
    '''
    a = Family()

    # Check that repeated ids are identified and reported
    df = pd.DataFrame({'id':(7,7,8,9,10,8)})
    with pytest.raises(ValueError) as e:
        a.check_df(df)
    assert 'Indices [7, 8] are repeated at rows [0, 1, 2, 5]' in str(e), e
    
    # Check that wrong spouses are identified and reported
    df = pd.DataFrame({'id':range(6),'spouse':(1,0,'',2,3,4)})
    with pytest.raises(AssertionError) as e:
        a.check_df(df)
    assert '2-th' in str(e) and "[3]" in str(e)

    # Check that self-married people raise an error
    df = pd.DataFrame({'id':['a', 'b'] + list(range(2, 6)),
                       'spouse': ['a', 'b'] + list(range(3, 7))})
    self_married = df.id[df.id == df.spouse]
    with pytest.raises(ValueError) as e:
        a.check_df(df)
    assert "[\'a\', \'b\'] at rows [0, 1] marry themselves" in str(e)

    # Check that people introduced before their parents (if they have any)
    # raise an error
    df = pd.DataFrame({'id': ('a', 'b', 'c'),
                       'spouse': ('', '', ''),
                       'father': ('', 'c', ''),
                       'mother': ('', '', ''),
                       })
    with pytest.raises(ValueError) as e:
        a.check_df(df)
    assert "1-th element with id b introduced before their father c" in str(e)

    df = pd.DataFrame({'id': ('a', 'b', 'c'),
                       'spouse': ('', '', ''),
                       'father': ('', '', ''),
                       'mother': ('', 'c', '')})
    with pytest.raises(ValueError) as e:
        a.check_df(df)
    assert "1-th element with id b introduced before their mother c" in str(e)

    # Check that unknown sexes raise an error
    df = pd.DataFrame({'id': ('a', 'b', 'c', 'd', 'e'),
                       'spouse': ('', '', '', '', ''),
                       'father': ('', '', '', '', ''),
                       'sex' : ('F', 'M', 'O', '', 'U'),
                       'mother': ('', '', '', '', '')
                       })
    with pytest.raises(ValueError) as e:
        a.check_df(df)
    assert "[\'e\'] at rows [4] have unknown sex [\'U\']" in str(e)
