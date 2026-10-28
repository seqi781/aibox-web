#!/usr/bin/env python3
"""Package only committed public files. Does not deploy or touch the main website."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess

PUBLIC_FILES = ('index.html','en/index.html','init/index.html','favicon.svg','assets/site.css','assets/site.js','assets/pricing.js','assets/cast-player.js','init/cast.js')

def package(source, revision, destination):
    source = pathlib.Path(source).resolve()
    if not re.fullmatch(r'[a-f0-9]{40}', revision): raise ValueError('Use a full commit SHA')
    destination = pathlib.Path(destination)
    if destination.exists() or destination.is_symlink(): raise ValueError('Output must be a new directory')
    blobs = {}
    for name in PUBLIC_FILES:
        data = subprocess.check_output(['git','-C',str(source),'show',revision+':'+name])
        if name.endswith('.html'):
            html = data.decode()
            for prefix in ['../assets/','assets/']:
                html = html.replace('"'+prefix, '"/aibox/_assets/'+revision+'/assets/')
            html = re.sub(r'(["\'])(?:\.\./)?favicon.svg', r'\1/aibox/_assets/'+revision+'/favicon.svg', html)
            if name == 'init/index.html': html = html.replace('src="cast.js"','src="/aibox/_assets/'+revision+'/init/cast.js"')
            data = html.encode()
        blobs[name] = data
    destination.mkdir(parents=True)
    for name, data in blobs.items():
        p = destination/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
    manifest = {name:hashlib.sha256(data).hexdigest() for name,data in blobs.items()}
    (destination/'release.json').write_text(json.dumps({'revision':revision,'files':manifest},indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    files=package(pathlib.Path(__file__).resolve().parents[1],args.revision,args.output)
    print(json.dumps({'revision':args.revision,'publicFiles':len(files),'output':args.output}))
