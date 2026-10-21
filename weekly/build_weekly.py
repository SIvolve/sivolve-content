"""Build one complete snapshot against one repository checkout."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from .archive_reader import load_previous
from .generate_weekly import release_groups, REPO
from .selection_rules import question_plan, EXPECTED_TYPES
from .question_picker import pick_questions
from .week_key import current_week_key

def validate_questions(questions):
    ids = []
    for q in questions:
        if any(not isinstance(q.get(k), str) or not q[k].strip()
               for k in ('id','kk','domain','difficulty','q','feedback')):
            raise ValueError('Missing question text or metadata')
        choices = q.get('options')
        if not isinstance(choices,list) or len(choices)<2 or any(
                not isinstance(v,str) or not v.strip() for v in choices):
            raise ValueError('Invalid answer choices')
        if type(q.get('answer')) is not int or not 0 <= q['answer'] < len(choices):
            raise ValueError('Invalid correct answer')
        ids.append(q['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate question ID')

def build(week=None, history=None, config=None, bank=None, curriculum=None):
    week = week or current_week_key()
    if config is None: config = json.loads((REPO/'config.json').read_text())
    if bank is None: bank = json.loads((REPO/'question_bank.json').read_text())
    validate_questions(bank)
    ordered, groups = release_groups(config, curriculum)
    plan = question_plan(len(ordered))
    prev = load_previous(week) if history is None else history
    questions = pick_questions(groups, plan, bank, week, prev)
    validate_questions(questions)
    expected_groups = [len(x) for x in plan]
    actual_groups = [sum(q['kk'] in g for q in questions) for g in groups]
    newest_target = len(plan[-1]) if len(groups[-1]) == 1 else 2
    if (len(questions)!=10 or actual_groups != expected_groups or
        sum(q['kk']==ordered[-1] for q in questions)!=newest_target or
        Counter(q['difficulty'] for q in questions)!=EXPECTED_TYPES or
        any(q['kk'] not in ordered for q in questions)):
        raise ValueError('Weekly quiz selection rules failed')
    return {
        'schema_version': 1,
        'week': week,
        'timezone': 'Australia/Melbourne',
        'status': 'preview_only',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'questions': questions
    }

if __name__ == '__main__':
    quiz = build()
    print('SUCCESS:',quiz['week'],len(quiz['questions']),'questions')
