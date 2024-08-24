import pytest

def test_from_series():

    # Ensure id nd name are all mandatory arguments
    a = {'name':'a'}
    with pytest.raises(ValueError) as e_info:
        ...

    