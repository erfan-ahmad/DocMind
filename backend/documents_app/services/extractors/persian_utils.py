import arabic_reshaper


def fix_persian_text(text: str) -> str:
    if not text:
        return text

    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        if not line.strip():
            fixed_lines.append(line)
            continue

        has_persian = any('\u0600' <= c <= '\u06FF' for c in line)

        if has_persian:
            try:
                reshaped = arabic_reshaper.reshape(line)
                fixed_lines.append(reshaped)
            except Exception:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)