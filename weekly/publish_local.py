"""Atomic, create-only local snapshot publication."""
import json
import os
import tempfile
from pathlib import Path
from .publication_guard import check_publication

def publish(preview, archive):
    folder = Path(archive)
    folder.mkdir(parents=True,exist_ok=True)
    target = check_publication(preview,folder)
    data = json.loads(Path(preview).read_text())
    data['status'] = 'published'
    fd, name = tempfile.mkstemp(dir=folder,prefix='.weekly-')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.link(name,target)   # fails if destination exists; never overwrites
    finally:
        if os.path.exists(name): os.unlink(name)
    return target
