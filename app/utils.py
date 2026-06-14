# utils.py
import re

def parse_internal_links(text):
    if not text: return ""
    return re.sub(r'\[\[(.*?)\]\]', r'<a href="/note/\1" class="internal-link">\1</a>', text)