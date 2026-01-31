import re

TECH_COLORS = {
    "python": "3776AB", "javascript": "F7DF1E", "typescript": "3178C6",
    "django": "092E20", "flask": "000000", "react": "61DAFB",
    "sql": "4479A1", "postgresql": "4169E1", "sqlite": "003B57",
    "docker": "2496ED", "node.js": "339933", "git": "F05032",
    "github": "181717", "gitlab": "FC6D26"
}

def tech_badge_preprocessor(text):
    """Heuristic: Find technology keywords and replace with badges if they belong to a skill list."""
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        # If line looks like a tech category (starts with - **Category**)
        if re.match(r'^\s*-\s+\*\*(.+)\*\*:', line):
            header, content = line.split(':', 1)
            techs = [t.strip() for t in content.replace(',', ' ').split()]
            badges = []
            for t in techs:
                clean_t = t.lower().strip('.,')
                if clean_t in TECH_COLORS:
                    color = TECH_COLORS[clean_t]
                    badges.append(f'![{t}](https://img.shields.io/badge/{t}-{color}?style=flat-square&logo={clean_t}&logoColor=white)')
                else:
                    badges.append(f'`{t}`')
            processed_lines.append(f"{header}: {' '.join(badges)}")
        else:
            processed_lines.append(line)
            
    return '\n'.join(processed_lines)
