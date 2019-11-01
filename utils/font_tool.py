from fontTools.fontBuilder import TTFont

fonts = {}


def check(char, font_path):
    if font_path in fonts:
        font = fonts.get(font_path)
    else:
        font = TTFont(font_path)
        fonts[font_path] = font

    utf8_char = char.encode("unicode_escape").decode('utf-8')
    if utf8_char.startswith('\\u'):
        uc = "uni" + utf8_char[2:].upper()
        f = font.getGlyphSet().get(uc)
        if f:
            return True
        else:
            return False
    return True


