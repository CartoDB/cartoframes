# -*- coding: utf-8 -*-
"""Data Observatory utility functions"""

# Country names are pegged to the following query:
# SELECT
#    count(*) num_measurements,
#    tag.key region_id,
#    tag.value region_name
#  FROM (
#    SELECT *
#    FROM OBS_GetAvailableNumerators()
#    WHERE jsonb_pretty(numer_tags) LIKE '%subsection/%'
#  ) numers,
#  Jsonb_Each(numers.numer_tags) tag
#  WHERE tag.key like 'section%'
#  GROUP BY tag.key, tag.value
#  ORDER BY region_name

REGIONTAGS = {
    'Australia': 'section/tags.au',
    'Brazil': 'section/tags.br',
    'Canada': 'section/tags.ca',
    'European Union': 'section/tags.eu',
    'France': 'section/tags.fr',
    'Mexico': 'section/tags.mx',
    'Spain': 'section/tags.spain',
    'United Kingdom': 'section/tags.uk',
    'United States': 'section/tags.united_states'
}


def get_countrytag(country):
    """normalize country name to match data obs"""
    norm_name = {
        'Australia': 'Australia',
        'Brazil': 'Brazil',
        'Canada': 'Canada',
        'European Union': 'European Union',
        'France': 'France',
        'Mexico': 'Mexico',
        'Spain': 'Spain',
        'United Kingdom': 'United Kingdom',
        'United States': 'United States',
        'Brasil': 'Brazil',
        'EU': 'European Union',
        'E.U.': 'European Union',
        'México': 'Mexico',
        'Méjico': 'Mexico',
        'Espana': 'Spain',
        'España': 'Spain',
        'UK': 'United Kingdom',
        'U.K.': 'United Kingdom',
        'United States of America': 'United States',
        'USA': 'United States',
        'U.S.': 'United States',
        'U.S.A.': 'United States'
    }
    if country in norm_name:
        return REGIONTAGS.get(norm_name.get(country))
    else:
        raise ValueError('The available regions are {1}.'.format(
                             country,
                             ', '.join('\'{}\''.format(k)
                                       for k in REGIONTAGS.keys())
                         ))
