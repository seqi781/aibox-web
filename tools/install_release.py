#!/usr/bin/env python3
"""Install/select a verified static release; never reload Nginx or restart the main app."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import uuid
from package import PUBLIC_FILES

def verify(folder, revision):
    folder=pathlib.Path(folder).absolute()
    if folder!=folder.resolve() or (folder/"release.json").is_symlink(): raise ValueError("Release symlink rejected")
    metadata=json.loads((folder/'release.json').read_text())
    if metadata.get('revision')!=revision or set(metadata.get('files',{}))!=set(PUBLIC_FILES): raise ValueError('Release manifest mismatch')
    for name,digest in metadata['files'].items():
        p=folder/name
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest: raise ValueError('Release file mismatch: '+name)
    return metadata

def install(root, revision, source=None):
    if not re.fullmatch(r'[a-f0-9]{40}',revision): raise ValueError('Full SHA required')
    root=pathlib.Path(root).absolute()
    if root!=root.resolve() or str(root).startswith(('/opt/usehooo','/var/lib/usehooo')): raise ValueError('Unsafe release root')
    if (root/'releases').is_symlink(): raise ValueError('Release root symlink rejected')
    release=root/'releases'/revision
    if source:
        source=pathlib.Path(source).resolve(); verify(source,revision)
        if release.exists(): verify(release,revision)
        else:
            release.mkdir(parents=True)
            root.chmod(0o755); (root/"releases").chmod(0o755); release.chmod(0o755)
            try:
                for name in [*PUBLIC_FILES,'release.json']:
                    target=release/name;target.parent.mkdir(exist_ok=True,parents=True);target.parent.chmod(0o755);shutil.copyfile(source/name,target);target.chmod(0o644)
            except BaseException:
                # Failed candidates are retained for diagnosis and are never selected.
                raise
        verify(release,revision)
    else: verify(release,revision)
    previous=os.readlink(root/'current') if (root/'current').is_symlink() else None
    if (root/'current').exists() and not (root/'current').is_symlink(): raise ValueError('Current path must be a symlink')
    temporary=root/('current-'+uuid.uuid4().hex)
    temporary.symlink_to('releases/'+revision)
    os.replace(temporary,root/'current')
    return {'revision':revision,'previous':previous,'mainAppTouched':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--revision',required=True);p.add_argument('--package')
    a=p.parse_args();print(json.dumps(install(a.root,a.revision,a.package)))
