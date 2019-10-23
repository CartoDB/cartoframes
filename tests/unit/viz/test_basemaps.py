from cartoframes.viz import basemaps


class TestBasemaps(object):
    def test_is_defined(self):
        "basemaps"
        assert basemaps is not None

    def test_has_defined_basemaps(self):
        "basemaps content"
        assert basemaps.positron == 'Positron'
        assert basemaps.darkmatter == 'DarkMatter'
        assert basemaps.voyager == 'Voyager'
