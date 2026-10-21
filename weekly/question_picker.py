"""Deterministic selection; rotation depends only on shared published quizzes."""
from random import Random
from .rotation import rotated_pool

def pick_questions(groups, plan, bank, week_key, previous_quizzes=None):
    history = previous_quizzes or []
    if len(groups) != len(plan):
        raise ValueError('Topic groups and question plan differ')
    rng = Random('SIvolve-Weekly-' + week_key)
    selected, used = [], set()
    newest = groups[-1][-1]
    for gi, (topics, kinds) in enumerate(zip(groups, plan)):
        for slot, kind in enumerate(kinds):
            options = topics
            # Exactly two newest-topic questions when the recent group has >1 topic.
            if gi == len(groups)-1 and len(topics) > 1:
                options = [newest] if slot < 2 else [t for t in topics if t != newest]
            pool = [q for q in bank if q['kk'] in options and
                    q['difficulty'] == kind and q['id'] not in used]
            if not pool:
                raise ValueError(f'Insufficient {kind} questions in group {gi+1}')
            pool = rotated_pool(pool, history)
            counts = {t:sum(x['kk']==t for x in selected) for t in options}
            least = min(counts[q['kk']] for q in pool)
            pool = [q for q in pool if counts[q['kk']] == least]
            chosen = rng.choice(sorted(pool, key=lambda q:str(q['id'])))
            selected.append(chosen)
            used.add(chosen['id'])
    # Shuffle the order as well as the selection, once per published week.
    rng.shuffle(selected)
    return selected
