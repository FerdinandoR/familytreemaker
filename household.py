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
        return    ('Household:\n'
                f'\tparents  = {", ".join(map(str, self.parents))}\n'
                f'\tchildren = {", ".join(map(str, self.children))}')

    def isempty(self):
        if len(self.parents) == 0 and len(self.children) == 0:
            return True
        return False
