import unittest
from floating_companion import clamp_position
class CompanionTests(unittest.TestCase):
 def test_stays_on_screen(self):self.assertEqual(clamp_position(9999,-100,106,140,(0,0,1920,1080)),(1814,0))
 def test_negative_monitor_coordinates(self):self.assertEqual(clamp_position(-1900,200,106,140,(-1920,0,3840,1080)),(-1900,200))
if __name__=='__main__':unittest.main()
