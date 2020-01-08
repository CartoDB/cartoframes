import pytest

from cartoframes.viz import Layer, Layout, Map
from cartoframes.viz.source import Source

from .utils import build_geodataframe

SOURCE = build_geodataframe([-10, 0], [-10, 0])


class TestLayout(object):
    def test_is_defined(self):
        """Layout"""
        assert Layout is not None


class TestLayoutInitialization(object):
    def test__init(self):
        """Layout should init properly"""
        layout = Layout([])
        assert layout._layout is not None
        assert layout._n_size == 0
        assert layout._m_size == 1
        assert layout._viewport is None
        assert layout._is_static is True

    def test__init_maps(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(SOURCE))),
                         Map(Layer(Source(SOURCE)))])
        assert layout._n_size == 2
        assert layout._m_size == 1

    def test__init_maps_valid(self):
        """Layout should raise an error if any element in the map list is not a Map"""

        msg = 'All the elements in the Layout should be an instance of Map.'
        with pytest.raises(Exception) as e:
            Layout([Layer(Source(SOURCE))])
        assert str(e.value) == msg

    def test__init_maps_size(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(SOURCE))),
                         Map(Layer(Source(SOURCE)))], 1, 2)
        assert layout._n_size == 1
        assert layout._m_size == 2


class TestLayoutSettings(object):
    def test_global_viewport(self):
        """Layout should return the same viewport for every map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('viewport') == {'zoom': 5}
        assert layout._layout[1].get('viewport') == {'zoom': 5}

    def test_custom_viewport(self):
        """Layout should return a different viewport for every map"""
        layout = Layout([
            Map(Layer(Source(SOURCE)), viewport={'zoom': 2}),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('viewport') == {'zoom': 2}
        assert layout._layout[1].get('viewport') == {'zoom': 5}

    def test_global_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}
        assert layout._layout[1].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}

    def test_custom_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE)), viewport={'zoom': 2}),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 2}
        assert layout._layout[1].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}

    def test_is_static(self):
        """Layout should set correctly is_static property for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('is_static') is True
        assert layout._layout[1].get('is_static') is True
