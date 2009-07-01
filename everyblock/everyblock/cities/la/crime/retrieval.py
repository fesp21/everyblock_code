"""
Scraper for crime in Los Angeles

http://www.lapdonline.org/crimemap/
http://www.lapdonline.org/crimemap/crime_search.php?&startDate=07/13/2008&interval=3&radius=1&lon=-118.322109&lat=34.07141&c[1]=1&c[2]=1&c[3]=1&c[4]=1&c[5]=1&c[6]=1&c[7]=1&c[8]=1
"""

from django.contrib.gis.geos import Point
from ebdata.retrieval.scrapers.base import ScraperBroken
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.dates import parse_date, parse_time
import datetime
import re
import time
from urllib import urlencode

# This list of long/lat tuples was generated by ebgeo.maps.tess.cover_city
# with a one-mile (1.609 km) radius.
SEARCH_POINTS = (
    (-118.28013040793886, 33.710913934398796),
    (-118.31768272329963, 33.728947212353383),
    (-118.29264784639244, 33.728947212353383),
    (-118.26761296948527, 33.728947212353383),
    (-118.2425780925781, 33.728947212353383),
    (-118.30516528484603, 33.746976701674861),
    (-118.28013040793886, 33.746976701674861),
    (-118.25509553103169, 33.746976701674861),
    (-118.29264784639244, 33.765002401374289),
    (-118.26761296948527, 33.765002401374289),
    (-118.30516528484603, 33.783024310464434),
    (-118.28013040793886, 33.783024310464434),
    (-118.25509553103169, 33.783024310464434),
    (-118.23006065412451, 33.783024310464434),
    (-118.30516528484603, 33.819056752876492),
    (-118.30516528484603, 33.855074021047329),
    (-118.43033966938185, 33.927063003346973),
    (-118.28013040793886, 33.927063003346973),
    (-118.25509553103169, 33.927063003346973),
    (-118.44285710783544, 33.94505075280977),
    (-118.41782223092827, 33.94505075280977),
    (-118.39278735402112, 33.94505075280977),
    (-118.26761296948527, 33.94505075280977),
    (-118.2425780925781, 33.94505075280977),
    (-118.45537454628904, 33.963034701884808),
    (-118.43033966938185, 33.963034701884808),
    (-118.40530479247471, 33.963034701884808),
    (-118.38026991556754, 33.963034701884808),
    (-118.30516528484603, 33.963034701884808),
    (-118.28013040793886, 33.963034701884808),
    (-118.46789198474262, 33.981014849603611),
    (-118.41782223092827, 33.981014849603611),
    (-118.31768272329963, 33.981014849603611),
    (-118.29264784639244, 33.981014849603611),
    (-118.26761296948527, 33.981014849603611),
    (-118.45537454628904, 33.998991194999419),
    (-118.40530479247471, 33.998991194999419),
    (-118.33020016175321, 33.998991194999419),
    (-118.30516528484603, 33.998991194999419),
    (-118.28013040793886, 33.998991194999419),
    (-118.25509553103169, 33.998991194999419),
    (-118.44285710783544, 34.016963737107147),
    (-118.41782223092827, 34.016963737107147),
    (-118.36775247711394, 34.016963737107147),
    (-118.3427176002068, 34.016963737107147),
    (-118.31768272329963, 34.016963737107147),
    (-118.29264784639244, 34.016963737107147),
    (-118.26761296948527, 34.016963737107147),
    (-118.2425780925781, 34.016963737107147),
    (-118.21754321567094, 34.016963737107147),
    (-118.19250833876377, 34.016963737107147),
    (-118.53047917701053, 34.034932474963448),
    (-118.45537454628904, 34.034932474963448),
    (-118.43033966938185, 34.034932474963448),
    (-118.40530479247471, 34.034932474963448),
    (-118.38026991556754, 34.034932474963448),
    (-118.35523503866035, 34.034932474963448),
    (-118.33020016175321, 34.034932474963448),
    (-118.30516528484603, 34.034932474963448),
    (-118.28013040793886, 34.034932474963448),
    (-118.25509553103169, 34.034932474963448),
    (-118.23006065412451, 34.034932474963448),
    (-118.20502577721736, 34.034932474963448),
    (-118.56803149237129, 34.05289740760665),
    (-118.54299661546412, 34.05289740760665),
    (-118.51796173855696, 34.05289740760665),
    (-118.49292686164979, 34.05289740760665),
    (-118.46789198474262, 34.05289740760665),
    (-118.44285710783544, 34.05289740760665),
    (-118.41782223092827, 34.05289740760665),
    (-118.39278735402112, 34.05289740760665),
    (-118.36775247711394, 34.05289740760665),
    (-118.3427176002068, 34.05289740760665),
    (-118.31768272329963, 34.05289740760665),
    (-118.29264784639244, 34.05289740760665),
    (-118.26761296948527, 34.05289740760665),
    (-118.2425780925781, 34.05289740760665),
    (-118.21754321567094, 34.05289740760665),
    (-118.5555140539177, 34.070858534076763),
    (-118.53047917701053, 34.070858534076763),
    (-118.50544430010338, 34.070858534076763),
    (-118.48040942319621, 34.070858534076763),
    (-118.45537454628904, 34.070858534076763),
    (-118.43033966938185, 34.070858534076763),
    (-118.38026991556754, 34.070858534076763),
    (-118.35523503866035, 34.070858534076763),
    (-118.33020016175321, 34.070858534076763),
    (-118.30516528484603, 34.070858534076763),
    (-118.28013040793886, 34.070858534076763),
    (-118.25509553103169, 34.070858534076763),
    (-118.23006065412451, 34.070858534076763),
    (-118.20502577721736, 34.070858534076763),
    (-118.17999090031019, 34.070858534076763),
    (-118.56803149237129, 34.088815853415539),
    (-118.54299661546412, 34.088815853415539),
    (-118.51796173855696, 34.088815853415539),
    (-118.49292686164979, 34.088815853415539),
    (-118.46789198474262, 34.088815853415539),
    (-118.44285710783544, 34.088815853415539),
    (-118.3427176002068, 34.088815853415539),
    (-118.31768272329963, 34.088815853415539),
    (-118.29264784639244, 34.088815853415539),
    (-118.26761296948527, 34.088815853415539),
    (-118.2425780925781, 34.088815853415539),
    (-118.21754321567094, 34.088815853415539),
    (-118.19250833876377, 34.088815853415539),
    (-118.1674734618566, 34.088815853415539),
    (-118.5555140539177, 34.106769364666398),
    (-118.53047917701053, 34.106769364666398),
    (-118.50544430010338, 34.106769364666398),
    (-118.48040942319621, 34.106769364666398),
    (-118.45537454628904, 34.106769364666398),
    (-118.43033966938185, 34.106769364666398),
    (-118.40530479247471, 34.106769364666398),
    (-118.38026991556754, 34.106769364666398),
    (-118.35523503866035, 34.106769364666398),
    (-118.33020016175321, 34.106769364666398),
    (-118.30516528484603, 34.106769364666398),
    (-118.28013040793886, 34.106769364666398),
    (-118.25509553103169, 34.106769364666398),
    (-118.23006065412451, 34.106769364666398),
    (-118.20502577721736, 34.106769364666398),
    (-118.17999090031019, 34.106769364666398),
    (-118.56803149237129, 34.124719066874498),
    (-118.54299661546412, 34.124719066874498),
    (-118.51796173855696, 34.124719066874498),
    (-118.49292686164979, 34.124719066874498),
    (-118.46789198474262, 34.124719066874498),
    (-118.44285710783544, 34.124719066874498),
    (-118.41782223092827, 34.124719066874498),
    (-118.39278735402112, 34.124719066874498),
    (-118.36775247711394, 34.124719066874498),
    (-118.3427176002068, 34.124719066874498),
    (-118.31768272329963, 34.124719066874498),
    (-118.29264784639244, 34.124719066874498),
    (-118.26761296948527, 34.124719066874498),
    (-118.2425780925781, 34.124719066874498),
    (-118.21754321567094, 34.124719066874498),
    (-118.19250833876377, 34.124719066874498),
    (-118.58054893082488, 34.14266495908663),
    (-118.5555140539177, 34.14266495908663),
    (-118.53047917701053, 34.14266495908663),
    (-118.50544430010338, 34.14266495908663),
    (-118.48040942319621, 34.14266495908663),
    (-118.45537454628904, 34.14266495908663),
    (-118.43033966938185, 34.14266495908663),
    (-118.40530479247471, 34.14266495908663),
    (-118.38026991556754, 34.14266495908663),
    (-118.33020016175321, 34.14266495908663),
    (-118.30516528484603, 34.14266495908663),
    (-118.28013040793886, 34.14266495908663),
    (-118.20502577721736, 34.14266495908663),
    (-118.61810124618565, 34.160607040351344),
    (-118.59306636927846, 34.160607040351344),
    (-118.56803149237129, 34.160607040351344),
    (-118.54299661546412, 34.160607040351344),
    (-118.51796173855696, 34.160607040351344),
    (-118.49292686164979, 34.160607040351344),
    (-118.46789198474262, 34.160607040351344),
    (-118.44285710783544, 34.160607040351344),
    (-118.41782223092827, 34.160607040351344),
    (-118.39278735402112, 34.160607040351344),
    (-118.36775247711394, 34.160607040351344),
    (-118.65565356154637, 34.178545309718842),
    (-118.63061868463923, 34.178545309718842),
    (-118.60558380773205, 34.178545309718842),
    (-118.58054893082488, 34.178545309718842),
    (-118.5555140539177, 34.178545309718842),
    (-118.53047917701053, 34.178545309718842),
    (-118.50544430010338, 34.178545309718842),
    (-118.48040942319621, 34.178545309718842),
    (-118.45537454628904, 34.178545309718842),
    (-118.43033966938185, 34.178545309718842),
    (-118.40530479247471, 34.178545309718842),
    (-118.38026991556754, 34.178545309718842),
    (-118.64313612309282, 34.196479766241048),
    (-118.61810124618565, 34.196479766241048),
    (-118.59306636927846, 34.196479766241048),
    (-118.56803149237129, 34.196479766241048),
    (-118.54299661546412, 34.196479766241048),
    (-118.51796173855696, 34.196479766241048),
    (-118.49292686164979, 34.196479766241048),
    (-118.46789198474262, 34.196479766241048),
    (-118.44285710783544, 34.196479766241048),
    (-118.41782223092827, 34.196479766241048),
    (-118.39278735402112, 34.196479766241048),
    (-118.63061868463923, 34.214410408971595),
    (-118.60558380773205, 34.214410408971595),
    (-118.58054893082488, 34.214410408971595),
    (-118.5555140539177, 34.214410408971595),
    (-118.53047917701053, 34.214410408971595),
    (-118.50544430010338, 34.214410408971595),
    (-118.48040942319621, 34.214410408971595),
    (-118.45537454628904, 34.214410408971595),
    (-118.43033966938185, 34.214410408971595),
    (-118.40530479247471, 34.214410408971595),
    (-118.38026991556754, 34.214410408971595),
    (-118.35523503866035, 34.214410408971595),
    (-118.64313612309282, 34.23233723696579),
    (-118.61810124618565, 34.23233723696579),
    (-118.59306636927846, 34.23233723696579),
    (-118.56803149237129, 34.23233723696579),
    (-118.54299661546412, 34.23233723696579),
    (-118.51796173855696, 34.23233723696579),
    (-118.49292686164979, 34.23233723696579),
    (-118.46789198474262, 34.23233723696579),
    (-118.44285710783544, 34.23233723696579),
    (-118.41782223092827, 34.23233723696579),
    (-118.39278735402112, 34.23233723696579),
    (-118.36775247711394, 34.23233723696579),
    (-118.3427176002068, 34.23233723696579),
    (-118.31768272329963, 34.23233723696579),
    (-118.29264784639244, 34.23233723696579),
    (-118.26761296948527, 34.23233723696579),
    (-118.63061868463923, 34.250260249280622),
    (-118.60558380773205, 34.250260249280622),
    (-118.58054893082488, 34.250260249280622),
    (-118.5555140539177, 34.250260249280622),
    (-118.53047917701053, 34.250260249280622),
    (-118.50544430010338, 34.250260249280622),
    (-118.48040942319621, 34.250260249280622),
    (-118.45537454628904, 34.250260249280622),
    (-118.43033966938185, 34.250260249280622),
    (-118.40530479247471, 34.250260249280622),
    (-118.38026991556754, 34.250260249280622),
    (-118.35523503866035, 34.250260249280622),
    (-118.33020016175321, 34.250260249280622),
    (-118.30516528484603, 34.250260249280622),
    (-118.28013040793886, 34.250260249280622),
    (-118.61810124618565, 34.268179444974798),
    (-118.59306636927846, 34.268179444974798),
    (-118.56803149237129, 34.268179444974798),
    (-118.54299661546412, 34.268179444974798),
    (-118.51796173855696, 34.268179444974798),
    (-118.49292686164979, 34.268179444974798),
    (-118.46789198474262, 34.268179444974798),
    (-118.44285710783544, 34.268179444974798),
    (-118.41782223092827, 34.268179444974798),
    (-118.39278735402112, 34.268179444974798),
    (-118.36775247711394, 34.268179444974798),
    (-118.3427176002068, 34.268179444974798),
    (-118.31768272329963, 34.268179444974798),
    (-118.29264784639244, 34.268179444974798),
    (-118.26761296948527, 34.268179444974798),
    (-118.2425780925781, 34.268179444974798),
    (-118.58054893082488, 34.286094823108719),
    (-118.5555140539177, 34.286094823108719),
    (-118.53047917701053, 34.286094823108719),
    (-118.50544430010338, 34.286094823108719),
    (-118.48040942319621, 34.286094823108719),
    (-118.45537454628904, 34.286094823108719),
    (-118.30516528484603, 34.286094823108719),
    (-118.54299661546412, 34.304006382744468),
    (-118.51796173855696, 34.304006382744468),
    (-118.49292686164979, 34.304006382744468),
    (-118.46789198474262, 34.304006382744468),
    (-118.44285710783544, 34.304006382744468),
    (-118.41782223092827, 34.304006382744468),
    (-118.50544430010338, 34.32191412294582),
    (-118.48040942319621, 34.32191412294582),
    (-118.45537454628904, 34.32191412294582),
    (-118.43033966938185, 34.32191412294582),
    (-118.40530479247471, 34.32191412294582)
)

class CrimeScraper(NewsItemListDetailScraper):
    schema_slugs = ('crime',)
    has_detail = False
    parse_list_re = re.compile(r"(?si)new searchPoint \('\d+', '\#(?P<case_number>\d+)', '(?P<color>[^']*)', '\d+', '(?P<lon>-\d+\.\d+)', '(?P<lat>\d+\.\d+)', '(?P<location_name>[^']*)', '[^']*', '[^']*', '(?P<crime_date>\d\d-\d\d-\d\d\d\d) (?P<crime_time>\d\d?:\d\d:\d\d [AP]M)', '(?P<division>[^']*)'\);")
    sleep = 8

    def __init__(self, start_date=None, end_date=None):
        NewsItemListDetailScraper.__init__(self)
        today = datetime.date.today()
        self.start_date = start_date or (today - datetime.timedelta(days=31))
        self.end_date = end_date or today

    def get_html(self, *args, **kwargs):
        MAX_TRIES = 4
        tries = 0
        while tries <= MAX_TRIES:
            html = NewsItemListDetailScraper.get_html(self, *args, **kwargs)
            if 'Unable to connect to PostgreSQL server' in html:
                self.logger.debug('Got "Unable to connect to PostgreSQL" error')
                time.sleep(3)
                continue
            return html
        raise ScraperBroken('Got PostgreSQL error %s times' % MAX_TRIES)

    def list_pages(self):
        INTERVAL = 3
        date = self.end_date - datetime.timedelta(days=INTERVAL)
        while date >= self.start_date - datetime.timedelta(days=INTERVAL):
            for lng, lat in SEARCH_POINTS:
                params = {
                    'startDate': date.strftime('%m/%d/%Y'),
                    'interval': INTERVAL,
                    'radius': 1,
                    'lon': lng,
                    'lat': lat,
                    'c[1]': '1',
                    'c[2]': '1',
                    'c[3]': '1',
                    'c[4]': '1',
                    'c[5]': '1',
                    'c[6]': '1',
                    'c[7]': '1',
                    'c[8]': '1',
                }
                yield self.get_html('http://www.lapdonline.org/crimemap/crime_search.php?%s' % urlencode(params))
            date -= datetime.timedelta(days=INTERVAL)

    def parse_list(self, page):
        records = list(NewsItemListDetailScraper.parse_list(self, page))
        self.logger.debug('Got %s records', len(records))
        if len(records) >= 99:
            raise ScraperBroken('Got %s records. Consider changing date interval' % len(records))
        return records

    def clean_list_record(self, record):
        record['crime_date'] = parse_date(record['crime_date'], '%m-%d-%Y')
        record['crime_time'] = parse_time(record['crime_time'], '%I:%M:%S %p')
        record['lon'] = float(record['lon'])
        record['lat'] = float(record['lat'])
        return record

    def existing_record(self, record):
        try:
            qs = NewsItem.objects.filter(schema__id=self.schema.id, item_date=record['crime_date'])
            return qs.by_attribute(self.schema_fields['case_number'], record['case_number'])[0]
        except IndexError:
            return None

    def save(self, old_record, list_record, detail_record):
        crime_type = self.get_or_create_lookup('crime_type', list_record['color'], list_record['color'])
        division = self.get_or_create_lookup('division', list_record['division'], list_record['division'])
        attributes = {
            'case_number': list_record['case_number'],
            'crime_time': list_record['crime_time'],
            'crime_type': crime_type.id,
            'division': division.id,
            'xy': '%s;%s' % (list_record['lon'], list_record['lat'])
        }
        title = u'#%s: %s' % (list_record['case_number'], crime_type.name)

        crime_location = Point(list_record['lon'], list_record['lat'], srid=4326)
        crime_location = self.safe_location(list_record['location_name'].replace('XX', '01'), crime_location, 375)

        if old_record is None:
            ni = self.create_newsitem(
                attributes,
                title=title,
                item_date=list_record['crime_date'],
                location=crime_location,
                location_name=list_record['location_name'],
            )
        else:
            # Convert the date to a datetime, because it's stored as a datetime
            # in the database, and the comparison to the existing record will
            # fail if we compare a date to a datetime.
            item_date = datetime.datetime(list_record['crime_date'].year, list_record['crime_date'].month, list_record['crime_date'].day)
            new_values = {'title': title, 'item_date': item_date, 'location_name': list_record['location_name']}
            self.update_existing(old_record, new_values, attributes)
            ni = old_record

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    CrimeScraper().update()