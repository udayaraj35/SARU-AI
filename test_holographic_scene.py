"""Rendering invariants: honest activity, reduced motion, resize and memory routing."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from holographic_scene import HolographicScene


class SceneTests(unittest.TestCase):
 def test_reduced_motion_freezes_decorative_and_audio_motion(self):
  scene=HolographicScene(320,360,points=180)
  self.assertEqual(scene.render(0,0,'STOPPED',True).tobytes(),scene.render(9,1,'SPEAKING',True).tobytes())

 def test_motion_and_actual_audio_level(self):
  scene=HolographicScene(320,360,points=180)
  idle=scene.render(1,0,'STOPPED').tobytes()
  self.assertNotEqual(idle,scene.render(2,0,'STOPPED').tobytes())
  self.assertEqual(idle,scene.render(1,1,'STOPPED').tobytes())
  self.assertNotEqual(scene.render(1,0,'LISTENING').tobytes(),scene.render(1,1,'LISTENING').tobytes())

 def test_resized_output_and_sphere_remain_inside_canvas(self):
  for width,height in ((320,360),(1400,750),(2200,1100)):
   scene=HolographicScene(width,height,points=100)
   self.assertEqual(scene.render().size,(width,height))
   left,top,right,bottom=scene.sphere_bounds
   self.assertTrue(0<=left<right<=width and 0<=top<bottom<=height)

 def test_memory_click_only_inside_sphere(self):
  from dashboard_ui import Dashboard
  scene=HolographicScene(600,400,points=100);callback=Mock()
  view=SimpleNamespace(holo_renderer=scene,actions={'Saved memory':callback})
  left,top,right,bottom=scene.sphere_bounds
  Dashboard.hologram_click(view,SimpleNamespace(x=left,y=top));callback.assert_not_called()
  Dashboard.hologram_click(view,SimpleNamespace(x=(left+right)/2,y=(top+bottom)/2));callback.assert_called_once_with()

 def test_readings_do_not_fabricate_missing_values(self):
  from dashboard_ui import Dashboard
  canvas=Mock();canvas.winfo_width.return_value=700
  view=SimpleNamespace(holo_renderer=object(),ring=canvas,scene_metrics=1,scene_status_dot=2,hero_voice_state='STOPPED')
  Dashboard.update_scene_readings(view,{'cpu':12.3,'ram':None})
  canvas.itemconfigure.assert_any_call(1,text='CPU 12%   RAM —   Disk —')
  canvas.itemconfigure.assert_any_call(2,fill='#8a96bc')


if __name__=='__main__':unittest.main()
