"""Publish a version only when all Windows/Mac packages match its commit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from build_release import VERSION_PATTERN

def gh(*args,**kwargs):
    return subprocess.run(['gh',*args],check=True,text=True,capture_output=True,**kwargs).stdout

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',required=True);p.add_argument('--commit',required=True);p.add_argument('--directory',default='release')
    args=p.parse_args()
    if not re.fullmatch(VERSION_PATTERN,args.version):p.error('Invalid release version')
    if not re.fullmatch(r'[0-9a-f]{40}',args.commit):p.error('A full commit SHA is required')
    directory=Path(args.directory);assets=[];checksums=[]
    for target in ('windows-x64','macos-arm64','macos-x64'):
        manifest_path=directory/f'manifest-{target}.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        expected=f'Little-Tides-{args.version}-{target}.zip'
        if manifest['version']!=args.version or manifest['target']!=target or manifest['commit']!=args.commit or manifest['archive']!=expected or manifest['packaged_smoke_test']!='passed' or manifest.get('native_display_smoke_test')!='passed':
            raise RuntimeError('Mismatched or incomplete build: '+target)
        archive=directory/expected;digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest!=manifest['sha256']:raise RuntimeError('Archive checksum mismatch: '+target)
        checksums.append(digest+'  '+expected);assets.extend([str(archive),str(manifest_path)])
    sums=directory/'SHA256SUMS.txt';sums.write_text('\n'.join(checksums)+'\n',encoding='utf-8');assets.append(str(sums))
    notes=directory/'release-notes.md'
    changes=''
    changelog=Path(__file__).with_name('CHANGELOG.md')
    if changelog.exists():
        marker='## '+args.version+'\n'
        history=changelog.read_text(encoding='utf-8')
        if marker in history:changes=history.split(marker,1)[1].split('\n## ',1)[0].strip()+'\n\n'
    notes.write_text(
        'Standalone desktop prototype, built from `'+args.commit+'`.\n\n'+
        changes+
        '- **Windows:** download the `windows-x64.zip`, extract it, and run the executable.\n'+
        '- **Mac with Apple Silicon:** use `macos-arm64.zip`.\n'+
        '- **Mac with Intel:** use `macos-x64.zip`.\n\n'+
        'All three native builds passed gameplay and water-entry checks, native-display fish transparency checks, and a packaged launch/render check using the native window driver. Manual desktop playtesting remains in progress.\n\n'+
        'Mac apps are ad-hoc signed and are not Apple Developer ID signed or notarized. macOS may require approval in Privacy & Security.\n\n'+
        'Start with a stick, tied line, hook and worm on Big Whiteshell Lake. Hold/release left click to cast, tap on a nibble to hook, and hold Space/right click to gather by hand.\n\n'+
        'This is an early prototype. See the repository for the editable source, design notes and research references.\n',encoding='utf-8')
    existing=subprocess.run(['gh','release','view',args.version,'--json','isDraft,url'],text=True,capture_output=True)
    if existing.returncode==0:
        current=json.loads(existing.stdout)
        tag_commit=gh('api','repos/'+os.environ['GITHUB_REPOSITORY']+'/commits/'+args.version,'--jq','.sha').strip()
        if tag_commit!=args.commit:raise RuntimeError('Existing tag points to another commit; use a new version')
        if not current['isDraft']:raise RuntimeError('Published versions are immutable; use a new version')
    else:
        gh('release','create',args.version,'--target',args.commit,'--title','Little Tides '+args.version,'--draft','--notes-file',str(notes))
    gh('release','upload',args.version,*assets,'--clobber')
    gh('release','edit',args.version,'--draft=false')
    print(gh('release','view',args.version,'--json','url','--jq','.url').strip())

if __name__=='__main__':main()
