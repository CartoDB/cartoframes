from cartoframes.viz import palettes


class TestPalettes(object):
    def test_is_defined(self):
        "palettes"
        assert palettes is not None

    def test_has_defined_palettes(self):
        "palettes content"
        assert palettes.burg == 'BURG'
        assert palettes.burgyl == 'BURGYL'
        assert palettes.cb_set3 == 'CB_SET3'
