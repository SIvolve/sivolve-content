"""GitHub Actions entrypoint; one immutable archive snapshot per Melbourne week."""
import json
import tempfile
from pathlib import Path
from .week_key import current_week_key, melbourne_monday
from .build_weekly import build
from .publish_local import publish
from .archive_reader import ARCHIVE

def main(manual=False):
    if not manual and not melbourne_monday():
        print('SKIP: It is not Monday in Melbourne.')
        return False
    week = current_week_key()
    archive = ARCHIVE / (week+'.json')
    if archive.exists():
        data = json.loads(archive.read_text())
        if data.get('week') != week or data.get('status') != 'published' or len(data.get('questions',[]))!=10:
            raise ValueError('Existing Weekly archive is invalid')
        print('SKIP: Weekly quiz already published:',week)
        return False
    quiz = build(week)
    with tempfile.TemporaryDirectory() as d:
        preview = Path(d) / (week+'.preview.json')
        preview.write_text(json.dumps(quiz,ensure_ascii=False))
        output = publish(preview,ARCHIVE)
    print('PUBLISHED LOCALLY:',output,'with',len(quiz['questions']),'questions')
    return True

if __name__ == '__main__':
    import sys
    main(manual='--manual' in sys.argv)
