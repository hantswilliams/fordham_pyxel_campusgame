"""Text helpers. Pure Python (no Pyxel)."""

CHAR_W = 4  # Pyxel's built-in font is 4px wide per character
LINE_H = 8


def wrap(text: str, max_chars: int) -> list[str]:
    """Greedy word wrap. Respects explicit newlines; hard-splits long words."""
    out: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            while len(word) > max_chars:
                if line:
                    out.append(line)
                    line = ""
                out.append(word[:max_chars])
                word = word[max_chars:]
            candidate = f"{line} {word}" if line else word
            if len(candidate) <= max_chars:
                line = candidate
            else:
                out.append(line)
                line = word
        out.append(line)
    return out
