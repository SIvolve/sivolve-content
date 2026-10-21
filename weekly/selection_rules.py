"""SIvolve Weekly target types by topic group."""
from collections import Counter
TYPES = {'F':'Foundation','A':'Application','S':'Stimulus','C':'SAC-style'}
EXPECTED_TYPES = Counter({'Foundation':3,'Application':4,'Stimulus':2,'SAC-style':1})

def question_plan(n):
    if n < 1: raise ValueError('No released topics')
    rows = (['FFFAAAASSC'] if n == 1 else
            ['FASC','FFAAAS'] if n == 2 else
            ['FAS','FAC','FAAS'])
    plan = [[TYPES[c] for c in row] for row in rows]
    assert Counter(k for group in plan for k in group) == EXPECTED_TYPES
    return plan
