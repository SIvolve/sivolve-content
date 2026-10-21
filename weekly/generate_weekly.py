"""Curriculum sequence and released-topic grouping for SIvolve Weekly."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

def release_groups(config=None, curriculum=None):
    if config is None:
        config = json.loads((REPO / 'config.json').read_text())
    if curriculum is None:
        curriculum = json.loads((ROOT / 'curriculum_order.json').read_text())
    releases = config['released']
    allowed = {x['name'] for x in releases if x['status'] == 'released'}
    if not allowed:
        raise ValueError('No released topics')
    sequences = [x['sequence'] for x in curriculum]
    names = [x['topic'] for x in curriculum]
    if len(names) != len(set(names)) or len(sequences) != len(set(sequences)):
        raise ValueError('Duplicate curriculum topics or sequence numbers')
    ordered = [x['topic'] for x in sorted(curriculum, key=lambda x:x['sequence'])
               if x['topic'] in allowed]
    if set(ordered) != allowed:
        raise ValueError('Released topic missing from curriculum sequence')
    n = len(ordered)
    if n == 1: groups = [ordered]
    elif n == 2: groups = [[ordered[0]],[ordered[1]]]
    else:
        early = (n + 2) // 3
        recent = n // 3
        groups = [ordered[:early], ordered[early:n-recent], ordered[n-recent:]]
    return ordered, groups

if __name__ == '__main__':
    ordered, groups = release_groups()
    print('Released topics:', len(ordered))
    print('Group sizes:', [len(g) for g in groups])
    print('Newest curriculum topic:', ordered[-1])
