"""Read and validate the six most recent immutable published snapshots."""
import json
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent / 'archive'
def load_previous(week_key, folder=None, limit=6):
    folder = Path(folder) if folder is not None else ARCHIVE
    previous = []
    for path in folder.glob('*.json'):
        data = json.loads(path.read_text())
        wk = data.get('week')
        if data.get('status') != 'published' or not isinstance(wk,str):
            continue
        if wk >= week_key: continue
        qs = data.get('questions')
        if len(qs) != 10 or len({q['id'] for q in qs}) != 10:
            raise ValueError(f'Invalid archive: {path}')
        previous.append((wk, qs))
    previous.sort(key=lambda x:x[0])
    return [qs for _,qs in previous[-limit:]]
