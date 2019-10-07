from cartoframes.viz import Style


class TestStyle(object):
    def test_is_style_defined(self):
        """Style"""
        assert Style is not None

    def test_style_default_point(self):
        """Style.compute_viz should return the default viz for point"""
        style = Style()
        viz = style.compute_viz('point')

        assert 'color: hex("#EE4D5A")' in viz
        assert 'width: ramp(linear(zoom(),0,18),[2,10])' in viz
        assert 'strokeWidth: ramp(linear(zoom(),0,18),[0,1])' in viz
        assert 'strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))' in viz

    def test_style_default_line(self):
        """Style.compute_viz should return the default viz for line"""
        style = Style()
        viz = style.compute_viz('line')

        assert 'color: hex("#4CC8A3")' in viz
        assert 'width: ramp(linear(zoom(),0,18),[0.5,4])' in viz

    def test_style_default_polygon(self):
        """Style.compute_viz should return the default viz for polygon"""
        style = Style()
        viz = style.compute_viz('polygon')

        assert 'color: hex("#826DBA")' in viz
        assert 'strokeWidth: ramp(linear(zoom(),2,18),[0.5,1])' in viz
        assert 'strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))' in viz

    def test_style_string(self):
        """Style.compute_viz should return the viz from a string with defaults"""
        style = Style('@var: 1\ncolor: red')
        viz = style.compute_viz('line')

        assert '@var: 1' in viz
        assert 'color: red' in viz
        assert 'width: ramp(linear(zoom(),0,18),[0.5,4])' in viz
        assert 'color: hex("#4CC8A3")' not in viz

    def test_style_dict(self):
        """Style.compute_viz should return the viz from a dict with defaults"""
        style = Style({
            'vars': {
                'var': 1
            },
            'color': 'red',
            'strokeWidth': 0
        })
        viz = style.compute_viz('polygon')

        assert '@var: 1' in viz
        assert 'color: red' in viz
        assert 'strokeWidth: 0' in viz
        assert 'strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))', viz
        assert 'color: hex("#826DBA")' not in viz
        assert 'strokeWidth: ramp(linear(zoom(),2,18),[0.5,1])' not in viz

    def test_style_default_variables(self):
        """Style.compute_viz should return the default viz with the variables"""
        style = Style()
        viz = style.compute_viz('point', {
            'mimi': '$pop',
            'momo': 123
        })

        assert '@mimi: $pop' in viz
        assert '@momo: 123' in viz

    def test_style_string_variables(self):
        """Style.compute_viz should return the string viz with the variables"""
        style = Style('@var: 1')
        viz = style.compute_viz('line', {
            'mimi': '$pop',
            'momo': 123
        })

        assert '@var: 1' in viz
        assert '@mimi: $pop' in viz
        assert '@momo: 123' in viz

    def test_style_dict_variables(self):
        """Style.compute_viz should return the dict viz with the variables"""
        style = Style({
            'vars': {
                'var': 1
            }
        })
        viz = style.compute_viz('line', {
            'mimi': '$pop',
            'momo': 123
        })

        assert '@var: 1' in viz
        assert '@mimi: $pop' in viz
        assert '@momo: 123' in viz
