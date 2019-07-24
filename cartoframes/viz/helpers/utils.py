
def serialize_palette(palette):
    if isinstance(palette, list):
        return '[{}]'.format(','.join(palette))
    return palette
