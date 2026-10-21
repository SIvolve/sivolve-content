"""Publication prerequisites; existing snapshots must never be overwritten."""
import json
import re
from pathlib import Path
from .week_key import current_week_key
from .build_weekly import validate_questions

def check_publication(preview, archive, today=None):
    data = json.loads(Path(preview).read_text())
    wk = data.get('week')
    if (wk != (today or current_week_key()) or data.get('status') != 'preview_only'
        or not re.fullmatch(r'\d{4}-W\d{2}',str(wk))):
        raise ValueError('Wrong week or invalid preview status')
    questions = data.get('questions')
    if not isinstance(questions,list) or len(questions)!=10:
        raise ValueError('Weekly quiz requires exactly 10 questions')
    validate_questions(questions)
    target = Path(archive)/(wk+'.json')
    if target.exists():
        raise FileExistsError(f'Already published: {target}')
    return target
