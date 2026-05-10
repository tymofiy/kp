import os, re
from pathlib import Path
md_link_re = re.compile(r'\[[^\]]+\]\(([^http][^\)]+)\)')
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.md') and not 'fixtures' in root:
            path = Path(root) / file
            content = path.read_text()
            for match in md_link_re.findall(content):
                target = match.split('#')[0]
                if target and not (path.parent / target).exists():
                    print(f'BROKEN LINK in {path}: {match}')
