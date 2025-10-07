#!/usr/bin/env python3
"""Fix BibTeX keys and encoding issues."""

import re
from pathlib import Path

BIB_FILE = Path("submission/references.bib")

# Read the file with error handling
try:
    content = BIB_FILE.read_text(encoding="utf-8")
except UnicodeDecodeError:
    # Try with latin-1 if utf-8 fails
    content = BIB_FILE.read_text(encoding="latin-1")

# Fix citation keys - remove spaces and periods
def fix_key(match):
    entry_type = match.group(1)
    key = match.group(2)
    # Remove spaces, periods, and other problematic characters
    # Keep only alphanumeric
    clean_key = re.sub(r'[^a-zA-Z0-9]', '', key)
    return f"@{entry_type}{{{clean_key},"

content = re.sub(r'@(\w+)\{([^,]+),', fix_key, content)

# Fix common encoding issues
replacements = {
    'ö': r'{\"o}',
    'ü': r'{\"u}',
    'ä': r'{\"a}',
    'Ö': r'{\"O}',
    'Ü': r'{\"U}',
    'Ä': r'{\"A}',
    'ß': r'{\ss}',
    'é': r"{\'e}",
    'è': r'{\`e}',
    'ê': r'{\^e}',
    'á': r"{\'a}",
    'à': r'{\`a}',
    'â': r'{\^a}',
    'í': r"{\'i}",
    'ó': r"{\'o}",
    'ú': r"{\'u}",
    'ñ': r'{\~n}',
    'ç': r'{\c{c}}',
}

for char, replacement in replacements.items():
    content = content.replace(char, replacement)

# Remove any remaining non-ASCII characters that might cause issues
content = content.encode('ascii', 'ignore').decode('ascii')

# Write back
BIB_FILE.write_text(content, encoding="utf-8")
print(f"✅ Fixed BibTeX keys and encoding in {BIB_FILE}")
