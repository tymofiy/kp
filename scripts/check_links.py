import os, re, sys
from pathlib import Path
md_link_re = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
broken = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]
    for file in files:
        if file.endswith('.md') and 'fixtures' not in root:
            path = Path(root) / file
            content = path.read_text()
            for match in md_link_re.findall(content):
                if match.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                target = match.split('#')[0]
                if target and not (path.parent / target).exists():
                    print(f'BROKEN LINK in {path}: {match}')
                    broken += 1
sys.exit(1 if broken else 0)
