"""Prioritise unseen questions and less recently sampled topics."""
from collections import Counter

def rotated_pool(pool, previous_quizzes, weeks=6):
    past = [q for quiz in previous_quizzes[-weeks:] for q in quiz]
    ids = {q['id'] for q in past}
    fresh = [q for q in pool if q['id'] not in ids]
    candidates = fresh or pool
    topic_uses = Counter(q['kk'] for q in past)
    fewest = min(topic_uses[q['kk']] for q in candidates)
    return [q for q in candidates if topic_uses[q['kk']] == fewest]
