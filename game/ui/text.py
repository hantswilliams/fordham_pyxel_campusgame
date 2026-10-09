"""Text helpers. Pure Python (no Pyxel)."""

CHAR_W = 4  # Pyxel's built-in font: small labels (map legend, hints)
LINE_H = 8

# Main reading font: PixelMplus 12 (assets/fonts), monospace 6x12 for ASCII.
# Used for dialogue, captions, cards and banners (decisions/0018).
BIG_CHAR_W = 6
BIG_LINE_H = 14


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
