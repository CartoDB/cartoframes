from cartoframes.viz.style import Style


class TestStyle(object):
    def test_is_style_defined(self):
        """Style"""
        assert Style is not None

    def test_style_default_point(self):
        """Style.compute_viz should return the default viz for point"""
        style = Style()
        viz = style.compute_viz()

        assert viz is None

    def test_style_default_line(self):
        """Style.compute_viz should return the default viz for line"""
        style = Style()
        viz = style.compute_viz()

        assert viz is None

    def test_style_default_polygon(self):
        """Style.compute_viz should return the default viz for polygon"""
        style = Style()
        viz = style.compute_viz()

        assert viz is None
