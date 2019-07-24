
def serialize_palette(palette):
    if isinstance(palette, (list, tuple)):
        return '[{}]'.format(','.join(palette))
    return palette
