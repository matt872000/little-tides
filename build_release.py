"""Build and smoke-test a native release on Windows or macOS."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
VERSION_PATTERN=r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',required=True)
    args=parser.parse_args()
    if not re.fullmatch(VERSION_PATTERN,args.version):parser.error('Use a version such as v0.1.0 or v0.2.0-beta.1')
    if sys.platform not in ('win32','darwin'):parser.error('Build on native Windows or macOS')
    arch={'amd64':'x64','x86_64':'x64','arm64':'arm64','aarch64':'arm64'}.get(platform.machine().lower())
    if arch is None:parser.error('Unsupported processor architecture')
    target=('windows-' if sys.platform=='win32' else 'macos-')+arch
    name=f'Little Tides {args.version} {target}'
    dist=ROOT/'dist';work=ROOT/'build'/'pyinstaller'
    command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir',
             '--exclude-module','numpy','--exclude-module','pygame.examples','--exclude-module','pygame.tests',
             '--name','Little Tides','--distpath',str(dist),'--workpath',str(work),'--specpath',str(ROOT/'build')]
    if sys.platform=='darwin':
        command+=['--osx-bundle-identifier','com.matt872000.littletides','--target-architecture',platform.machine().lower()]
    command+=[str(ROOT/'main.py')]
    subprocess.run(command,cwd=ROOT,check=True)
    executable=dist/'Little Tides'/'Little Tides.exe' if sys.platform=='win32' else dist/'Little Tides.app'/'Contents'/'MacOS'/'Little Tides'
    smoke=ROOT/'build'/f'smoke-{target}.png'
    subprocess.run([str(executable),'--smoke-test',str(smoke),'--native-display'],cwd=ROOT,check=True,timeout=90)
    if not smoke.is_file() or smoke.stat().st_size<1000:raise RuntimeError('Packaged game did not render a smoke-test frame')
    stage=ROOT/'build'/'release-stage'/name
    if stage.exists():
        # Only remove this tool-owned staging directory after checking its boundary.
        resolved=stage.resolve();boundary=(ROOT/'build'/'release-stage').resolve()
        if boundary not in resolved.parents:raise RuntimeError('Invalid staging path')
        shutil.rmtree(resolved)
    stage.mkdir(parents=True)
    if sys.platform=='win32':
        shutil.copytree(dist/'Little Tides',stage/'Little Tides')
    else:
        subprocess.run(['ditto',str(dist/'Little Tides.app'),str(stage/'Little Tides.app')],check=True)
        subprocess.run(['codesign','--verify','--deep','--strict',str(stage/'Little Tides.app')],check=True)
    shutil.copytree(ROOT/'licenses',stage/'licenses')
    for filename in ('THIRD-PARTY.txt','README.md'):
        shutil.copy2(ROOT/filename,stage/filename)
    shutil.copy2(ROOT/'docs'/'GAME_DESIGN.md',stage/'GAME_DESIGN.md')
    shutil.copy2(ROOT/'docs'/'SOURCES.md',stage/'SOURCES.md')
    (stage/'VERSION.txt').write_text(args.version+'\n'+target+'\n',encoding='utf-8')
    (stage/'START-HERE.txt').write_text(
        'Little Tides '+args.version+'\n\n'+
        ('Extract the whole ZIP, then open Little Tides/Little Tides.exe.\nKeep the _internal folder beside the executable.\n' if sys.platform=='win32' else
         'Extract the ZIP, then move Little Tides.app to Applications and open it.\nThis first Mac build is ad-hoc signed, not Apple Developer ID signed or notarized.\nmacOS may require you to approve the app in Privacy & Security before opening it.\n')+
        '\nHold/release left click: cast. Tap left click on a nibble: hook.\nHold Space/right click: gather by hand. J: journal. Esc: pause.\nF11: fullscreen. F1: hints. On some Macs, use Fn with function keys.\n'+
        ('\nSaves: beside Little Tides.exe.\n' if sys.platform=='win32' else '\nSaves: ~/Library/Application Support/Little Tides/\n'),encoding='utf-8')
    release=ROOT/'release';release.mkdir(exist_ok=True)
    archive=release/f'Little-Tides-{args.version}-{target}.zip'
    if sys.platform=='darwin':
        subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent',str(stage),str(archive)],check=True)
    else:
        shutil.make_archive(str(archive.with_suffix('')),'zip',stage.parent,stage.name)
    manifest={'version':args.version,'target':target,'commit':os.environ.get('GITHUB_SHA','local'),
              'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
              'packaged_smoke_test':'passed','native_display_smoke_test':'passed',
              'apple_notarized':False if sys.platform=='darwin' else None}
    (release/f'manifest-{target}.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
