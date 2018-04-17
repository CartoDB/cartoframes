
Map Styling Functions[¶](#map-styling-functions "Permalink to this headline")
-----------------------------------------------------------------------------

Styling module that exposes CARTOColors schemes. Read more about CARTOColors in its [GitHub repository](https://github.com/Carto-color/).

[![CARTOColors](https://cloud.githubusercontent.com/assets/1566273/21021002/fc9df60e-bd33-11e6-9438-d67951a7a9bf.png)](https://cloud.githubusercontent.com/assets/1566273/21021002/fc9df60e-bd33-11e6-9438-d67951a7a9bf.png)

_class_ `cartoframes.styling.``BinMethod`

Data classification methods used for the styling of data on maps.

`quantiles`[¶](#cartoframes.styling.BinMethod.quantiles "Permalink to this definition")

_str_ – Quantiles classification for quantitative data

`jenks`[¶](#cartoframes.styling.BinMethod.jenks "Permalink to this definition")

_str_ – Jenks classification for quantitative data

`headtails`[¶](#cartoframes.styling.BinMethod.headtails "Permalink to this definition")

_str_ – Head/Tails classification for quantitative data

`equal`[¶](#cartoframes.styling.BinMethod.equal "Permalink to this definition")

_str_ – Equal Interval classification for quantitative data

`category`[¶](#cartoframes.styling.BinMethod.category "Permalink to this definition")

_str_ – Category classification for qualitative data

`mapping`[¶](#cartoframes.styling.BinMethod.mapping "Permalink to this definition")

_dict_ – The TurboCarto mappings

`cartoframes.styling.``get_scheme_cartocss`(_column_, _scheme_info_)

Get TurboCARTO CartoCSS based on input parameters

`cartoframes.styling.``custom`(_colors_, _bins=None_, _bin_method='quantiles'_)

Create a custom scheme.



Parameters:

*   **colors** (_list of str_) – List of hex values for styling data
*   **bins** (_int__,_ _optional_) – Number of bins to style by. If not given, the number of colors will be used.
*   **bin_method** (_str__,_ _optional_) – Classification method. One of the values in [`BinMethod`](cartoframes.styling.html#cartoframes.styling.BinMethod "cartoframes.styling.BinMethod"). Defaults to quantiles, which only works with quantitative data.

`cartoframes.styling.``scheme`(_name_, _bins_, _bin_method='quantiles'_)

Return a custom scheme based on CARTOColors.



Parameters:

*   **name** (_str_) – Name of a CARTOColor.
*   **bins** (_int_ _or_ _iterable_) – If an int, the number of bins for classifying data. CARTOColors have 7 bins max for quantitative data, and 11 max for qualitative data. If bins is a list, it is the upper range for classifying data. E.g., bins can be of the form `(10, 20, 30, 40, 50)`.
*   **bin_method** (_str__,_ _optional_) – One of methods in [`BinMethod`](cartoframes.styling.html#cartoframes.styling.BinMethod "cartoframes.styling.BinMethod"). Defaults to `quantiles`. If bins is an interable, then that is the bin method that will be used and this will be ignored.

Warning

Input types are particularly sensitive in this function, and little feedback is given for errors. `name` and `bin_method` arguments are case-sensitive.

`cartoframes.styling.``burg`(_bins_, _bin_method='quantiles'_)

CARTOColors Burg quantitative scheme

`cartoframes.styling.``burgYl`(_bins_, _bin_method='quantiles'_)

CARTOColors BurgYl quantitative scheme

`cartoframes.styling.``redOr`(_bins_, _bin_method='quantiles'_)

CARTOColors RedOr quantitative scheme

`cartoframes.styling.``orYel`(_bins_, _bin_method='quantiles'_)

CARTOColors OrYel quantitative scheme

`cartoframes.styling.``peach`(_bins_, _bin_method='quantiles'_)

CARTOColors Peach quantitative scheme

`cartoframes.styling.``pinkYl`(_bins_, _bin_method='quantiles'_)

CARTOColors PinkYl quantitative scheme

`cartoframes.styling.``mint`(_bins_, _bin_method='quantiles'_)

CARTOColors Mint quantitative scheme

`cartoframes.styling.``bluGrn`(_bins_, _bin_method='quantiles'_)

CARTOColors BluGrn quantitative scheme

`cartoframes.styling.``darkMint`(_bins_, _bin_method='quantiles'_)

CARTOColors DarkMint quantitative scheme

`cartoframes.styling.``emrld`(_bins_, _bin_method='quantiles'_)

CARTOColors Emrld quantitative scheme

`cartoframes.styling.``bluYl`(_bins_, _bin_method='quantiles'_)

CARTOColors BluYl quantitative scheme

`cartoframes.styling.``teal`(_bins_, _bin_method='quantiles'_)

CARTOColors Teal quantitative scheme

`cartoframes.styling.``tealGrn`(_bins_, _bin_method='quantiles'_)

CARTOColors TealGrn quantitative scheme

`cartoframes.styling.``purp`(_bins_, _bin_method='quantiles'_)

CARTOColors Purp quantitative scheme

`cartoframes.styling.``purpOr`(_bins_, _bin_method='quantiles'_)

CARTOColors PurpOr quantitative scheme

`cartoframes.styling.``sunset`(_bins_, _bin_method='quantiles'_)

CARTOColors Sunset quantitative scheme

`cartoframes.styling.``magenta`(_bins_, _bin_method='quantiles'_)

CARTOColors Magenta quantitative scheme

`cartoframes.styling.``sunsetDark`(_bins_, _bin_method='quantiles'_)

CARTOColors SunsetDark quantitative scheme

`cartoframes.styling.``brwnYl`(_bins_, _bin_method='quantiles'_)

CARTOColors BrwnYl quantitative scheme

`cartoframes.styling.``armyRose`(_bins_, _bin_method='quantiles'_)

CARTOColors ArmyRose divergent quantitative scheme

`cartoframes.styling.``fall`(_bins_, _bin_method='quantiles'_)

CARTOColors Fall divergent quantitative scheme

`cartoframes.styling.``geyser`(_bins_, _bin_method='quantiles'_)

CARTOColors Geyser divergent quantitative scheme

`cartoframes.styling.``temps`(_bins_, _bin_method='quantiles'_)

CARTOColors Temps divergent quantitative scheme

`cartoframes.styling.``tealRose`(_bins_, _bin_method='quantiles'_)

CARTOColors TealRose divergent quantitative scheme

`cartoframes.styling.``tropic`(_bins_, _bin_method='quantiles'_)

CARTOColors Tropic divergent quantitative scheme

`cartoframes.styling.``earth`(_bins_, _bin_method='quantiles'_)

CARTOColors Earth divergent quantitative scheme

`cartoframes.styling.``antique`(_bins_, _bin_method='category'_)

CARTOColors Antique qualitative scheme

`cartoframes.styling.``bold`(_bins_, _bin_method='category'_)

CARTOColors Bold qualitative scheme

`cartoframes.styling.``pastel`(_bins_, _bin_method='category'_)

CARTOColors Pastel qualitative scheme

`cartoframes.styling.``prism`(_bins_, _bin_method='category'_)

CARTOColors Prism qualitative scheme

`cartoframes.styling.``safe`(_bins_, _bin_method='category'_)

CARTOColors Safe qualitative scheme

`cartoframes.styling.``vivid`(_bins_, _bin_method='category'_)

CARTOColors Vivid qualitative scheme
