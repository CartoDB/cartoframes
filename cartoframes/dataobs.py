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
        'australia': 'Australia',
        'brazil': 'Brazil',
        'brasil': 'Brazil',
        'canada': 'Canada',
        'european union': 'European Union',
        'eu': 'European Union',
        'e.u.': 'European Union',
        'france': 'France',
        'mexico': 'Mexico',
        'méxico': 'Mexico',
        'méjico': 'Mexico',
        'spain': 'Spain',
        'espana': 'Spain',
        'españa': 'Spain',
        'uk': 'United Kingdom',
        'u.k.': 'United Kingdom',
        'united kingdom': 'United Kingdom',
        'united states of america': 'United States',
        'united states': 'United States',
        'us': 'United States',
        'usa': 'United States',
        'u.s.': 'United States',
        'u.s.a.': 'United States'
    }
    if country is not None and country.lower() in norm_name:
        return REGIONTAGS.get(norm_name.get(country.lower()))
    else:
        raise ValueError(
            'The available regions are {0}.'.format(
                ', '.join('\'{}\''.format(k) for k in REGIONTAGS)))
