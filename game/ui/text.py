"""Text helpers. Pure Python (no Pyxel)."""

CHAR_W = 4  # Pyxel's built-in font: small labels (map legend, hints)
LINE_H = 8

# Main reading font (decisions/0018, resized in 0036 for the 384 x 288 screen):
# DotGothic16 drawn at 15 px, monospace 8 px wide for ASCII. Used for
# dialogue, captions, cards, menus and banners.
BIG_CHAR_W = 8
BIG_LINE_H = 17
TEXT_H = 14          # one line of it, capitals to descenders (PixelMplus 12 was 12)
GROW = TEXT_H - 12   # how much taller a one-line label box is than with the old font


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
