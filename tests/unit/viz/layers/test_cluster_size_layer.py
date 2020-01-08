import pytest

from carto.exceptions import CartoException

from cartoframes.viz import layers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_cartodataframe


@pytest.mark.skip(reason="This helper will be removed")
class TestClusterSizeLayerHelper(object):
    def setup_method(self):
        self.source = build_cartodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert layers.cluster_size_layer is not None

    def test_cluster_size_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)

        layer = layers.cluster_size_layer(
            source='SELECT * FROM faketable',
            value='name',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['width'] == 'ramp(linear(clusterCount(), ' + \
            'viewportMIN(clusterCount()), viewportMAX(clusterCount())), [4.0, 16.0, 32])'
        assert layer.style._style['point']['color'] == 'opacity(#FFB927, 0.8)'
        assert layer.style._style['point']['strokeColor'] == 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))'
        assert layer.style._style['point']['filter'] == '1'
        assert layer.style._style['point']['resolution'] == '32'

        assert layer.popups is not None

        popup = layer.popups.elements[0]

        assert popup.title == 'count'
        assert popup.value == 'clusterCount()'
        assert layer.legends is not None
        assert layer.legends._type['point'] == 'size-continuous-point'
        assert layer.legends._title == 'count'
        assert layer.legends._description == ''
        assert layer.legends._footer == ''

    def test_valid_operation(self):
        """cluster_size_layer should raise an error if the operation is invalid"""

        msg = '"invalid" is not a valid operation. Valid operations are count, avg, min, max, sum'
        with pytest.raises(CartoException) as e:
            layers.cluster_size_layer(
                source=self.source,
                value='name',
                operation='invalid'
            )
        assert str(e.value) == msg
