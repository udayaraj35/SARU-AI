"""Offline country/timezone choices from the installed IANA tzdata tables."""
from functools import lru_cache
from importlib.resources import files
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError,available_timezones

OTHER='UTC / Other timezone'


@lru_cache(maxsize=1)
def country_catalog():
    folder=files('tzdata.zoneinfo')
    names={}
    for line in (folder/'iso3166.tab').read_text(encoding='utf8').splitlines():
        if line and not line.startswith('#'):
            code,name=line.split('\t',1);names[code]=name
    zones={}
    for line in (folder/'zone.tab').read_text(encoding='utf8').splitlines():
        if not line or line.startswith('#'):continue
        code,coordinates,zone,*comment=line.split('\t')
        zones.setdefault(code,[]).append(zone)
    return {code:{'name':names.get(code,code),'label':names.get(code,code)+' ('+code+')','zones':tuple(sorted(set(values)))} for code,values in zones.items()}


def country_choices():
    return [OTHER]+[row['label'] for row in sorted(country_catalog().values(),key=lambda row:row['name'].casefold())]


def country_code(label):
    if label==OTHER:return ''
    for code,row in country_catalog().items():
        if row['label']==label:return code
    raise ValueError('Choose a country from the list.')


def country_for_zone(zone):
    for code,row in country_catalog().items():
        if zone in row['zones']:return code
    return ''


def zones_for_country(code):
    if not code:return tuple(sorted(available_timezones()))
    if code not in country_catalog():raise ValueError('Unknown clock country.')
    return country_catalog()[code]['zones']


def validate_clock(country,zone):
    try:ZoneInfo(zone)
    except (ZoneInfoNotFoundError,ValueError):raise ValueError('Choose an available timezone from the list.') from None
    if zone not in zones_for_country(country):raise ValueError('Choose a timezone belonging to the selected country.')
    return country,zone
