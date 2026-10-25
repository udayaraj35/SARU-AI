import datetime,unittest
from unittest.mock import Mock
from header_status import clock_text,fetch_weather

class HeaderTests(unittest.TestCase):
 def test_offline_country_choices_and_timezone_validation(self):
  from clock_regions import country_catalog,country_for_zone,zones_for_country,validate_clock
  self.assertGreater(len(country_catalog()),200)
  self.assertEqual(country_for_zone('Asia/Kathmandu'),'NP')
  self.assertEqual(zones_for_country('NP'),('Asia/Kathmandu',))
  self.assertGreater(len(zones_for_country('US')),1)
  self.assertEqual(validate_clock('NP','Asia/Kathmandu'),('NP','Asia/Kathmandu'))
  with self.assertRaises(ValueError):validate_clock('NP','Europe/Sofia')
  with self.assertRaises(ValueError):validate_clock('','invalid/timezone')
 def test_country_clock_offsets_and_dst(self):
  winter=datetime.datetime(2026,1,15,12,tzinfo=datetime.timezone.utc)
  summer=datetime.datetime(2026,7,15,12,tzinfo=datetime.timezone.utc)
  self.assertIn('17:45:00',clock_text(winter,'Asia/Kathmandu')[0])
  self.assertIn('07:00:00',clock_text(winter,'America/New_York')[0])
  self.assertIn('08:00:00',clock_text(summer,'America/New_York')[0])
 def test_real_bs_conversion_and_timezone(self):
  text,bs=clock_text(datetime.datetime(2020,9,4,9,tzinfo=datetime.timezone.utc))
  self.assertIn('12:00:00',text);self.assertIn('Europe/Sofia',text)
  self.assertIn('२०७७',bs);self.assertIn('१९',bs)
 def test_weather_uses_response_not_sample_values(self):
  session=Mock();geo=Mock();geo.json.return_value={'results':[{'name':'Kathmandu','latitude':27.7,'longitude':85.3}]}
  response=Mock();response.json.return_value={'current':{'temperature_2m':17.3,'weather_code':3,'time':'2026-10-23T18:15'}}
  session.get.side_effect=[geo,response]
  value=fetch_weather('Kathmandu',session)
  self.assertIn('17.3°C',value);self.assertIn('Kathmandu',value);self.assertIn('Open-Meteo',value)
 def test_unknown_city_does_not_invent_temperature(self):
  session=Mock();session.get.return_value.json.return_value={'results':[]}
  with self.assertRaises(ValueError):fetch_weather('unknown',session)

if __name__=='__main__':unittest.main()
