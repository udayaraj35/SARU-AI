"""Isolated native-widget checks: no network, microphone or owner data."""
import sqlite3,tempfile,tkinter as tk,unittest
from tkinter import ttk
from types import SimpleNamespace
from memory_journal import MemoryJournal
from memory_ui import MemoryPanel
from sidebar_navigation import SidebarNavigation
from reference_widgets import NeonButton

class WidgetTests(unittest.TestCase):
 def test_sidebar_fits_tall_window_and_wheels_over_last_buttons_in_small_window(self):
  root=tk.Tk();root.geometry('320x900')
  try:
   nav=tk.Frame(root);nav.pack(fill='both',expand=True);canvas=tk.Canvas(nav,highlightthickness=0);canvas.pack(side='left',fill='both',expand=True);scroll=ttk.Scrollbar(nav,command=canvas.yview);canvas.configure(yscrollcommand=scroll.set)
   links=tk.Frame(canvas);buttons=[]
   for index in range(13):
    button=NeonButton(links,'Button '+str(index),lambda:None,width=240,height=35);button.pack(fill='x',padx=4,pady=3);buttons.append(button)
   controller=SidebarNavigation(canvas,links,scroll,buttons);root.update()
   self.assertFalse(scroll.winfo_manager());self.assertLessEqual(links.winfo_height(),canvas.winfo_height())
   root.geometry('320x240');root.update();self.assertTrue(scroll.winfo_manager());self.assertGreater(links.winfo_height(),canvas.winfo_height())
   before=canvas.yview();buttons[-1].event_generate('<MouseWheel>',delta=-120);root.update();self.assertGreater(canvas.yview()[0],before[0])
   controller.wheel(SimpleNamespace(delta=60));controller.wheel(SimpleNamespace(delta=60));root.update();self.assertLessEqual(canvas.yview()[0],before[0]+.01)
   root.geometry('320x1000');root.update();self.assertFalse(scroll.winfo_manager());self.assertEqual(canvas.yview()[0],0)
  finally:root.destroy()
 def test_memory_page_search_filters_and_saved_record_refresh(self):
  root=tk.Tk();root.geometry('950x650');db=sqlite3.connect(':memory:')
  try:
   with tempfile.TemporaryDirectory() as folder:
    journal=MemoryJournal(db,{});journal.record('conversation','Boss','tea without sugar');journal.record('task','Chrome','window opened')
    page=MemoryPanel(root,journal,folder,lambda:None,lambda:None,lambda:None);root.update()
    self.assertGreater(page.foot.winfo_height(),25)
    self.assertLess(page.foot.winfo_y()+page.foot.winfo_height(),page.winfo_height()+1)
    self.assertIn('tea without sugar',page.output.get('1.0','end'));page.kind.set('task');page.query.set('Chrome');page.refresh()
    text=page.output.get('1.0','end');self.assertIn('window opened',text);self.assertNotIn('tea without sugar',text)
    journal.record('task','Chrome','closed verified window');page.refresh();self.assertIn('closed verified window',page.output.get('1.0','end'))
  finally:root.destroy();db.close()

if __name__=='__main__':unittest.main()
