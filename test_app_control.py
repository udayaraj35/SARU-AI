import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from app_catalog import AppEntry,launch_entry
from app_windows import match_windows
from assistant_commands import parse_command
from voice_requests import voice_request
from screen_ui import ScreenPanel

class AppControlTests(unittest.TestCase):
 def test_store_launcher_uses_native_activation_without_shell(self):
  entry=AppEntry('Calculator','registered','Microsoft.WindowsCalculator_8wekyb3d8bbwe!App')
  with patch('windows_activation.activate_registered',return_value=42) as activate,patch('app_catalog.subprocess.Popen') as shell:
   self.assertEqual(launch_entry(entry),42)
  activate.assert_called_once_with(entry.target);shell.assert_not_called()
 def test_native_activation_uses_in_process_interface(self):
  import comtypes
  from windows_activation import activate_registered
  manager=Mock();manager.ActivateApplication.return_value=42
  with patch('comtypes.client.CreateObject',return_value=manager) as create,patch('comtypes.CoInitialize'),patch('comtypes.CoUninitialize'):
   self.assertEqual(activate_registered('Microsoft.WindowsCalculator_8wekyb3d8bbwe!App'),42)
  self.assertEqual(create.call_args.kwargs['clsctx'],comtypes.CLSCTX_INPROC_SERVER)
  manager.ActivateApplication.assert_called_once_with('Microsoft.WindowsCalculator_8wekyb3d8bbwe!App',None,0)
 def test_command_keeps_app_and_task_separate(self):
  for command in ('use Notepad: write Hello SARU','open Notepad and write Hello SARU','Notepad kholera write Hello SARU'):
   self.assertEqual(parse_command(command),('desktop_task',('Notepad','write Hello SARU')))
  self.assertEqual(voice_request('Saru, use Notepad: write Hello'),('desktop_task',('Notepad','write Hello')))
 def test_exact_executable_and_ambiguous_windows(self):
  entry=AppEntry('Editor','exe',r'C:\Apps\editor.exe')
  windows=[{'hwnd':1,'title':'Unsaved document','exe':r'C:\Apps\editor.exe'},{'hwnd':2,'title':'Editor','exe':r'C:\Other\editor.exe'}]
  self.assertEqual([w['hwnd'] for w in match_windows(entry,windows)],[1])
  windows.append({'hwnd':3,'title':'Other document','exe':entry.target})
  self.assertEqual(len(match_windows(entry,windows)),2)
 def test_store_title_match_does_not_choose_unrelated_title(self):
  entry=AppEntry('Notepad','registered','Microsoft.WindowsNotepad!App')
  windows=[{'hwnd':1,'title':'Untitled - Notepad','exe':''},{'hwnd':2,'title':'Notepad tutorial - Browser','exe':''}]
  self.assertEqual([w['hwnd'] for w in match_windows(entry,windows)],[1])
  self.assertEqual(match_windows(AppEntry('Unknown','registered','Unknown!App'),windows),[])
 def panel(self):
  return SimpleNamespace(pending_action=('type','Hello'),target_window=123,snapshot=object(),point=(50,60),captured_at=1,status=Mock(),steps=[],after=Mock(return_value='capture-timer'),take_snapshot=Mock(),restore=Mock(),canvas=Mock())
 def test_input_restores_target_then_captures_result(self):
  panel=self.panel()
  with patch('screen_ui.activate_window') as activate,patch('screen_ui.execute_action',return_value='Input performed') as execute:
   ScreenPanel.run_input(panel)
  activate.assert_called_once_with(123);execute.assert_called_once();panel.after.assert_called_once_with(400,panel.take_snapshot)
  self.assertEqual(panel.steps,['type']);panel.restore.assert_not_called()
 def test_failed_input_never_reports_success_or_schedules_capture(self):
  panel=self.panel()
  with patch('screen_ui.activate_window',side_effect=RuntimeError('Window closed')),patch('screen_ui.execute_action') as execute:
   ScreenPanel.run_input(panel)
  execute.assert_not_called();panel.after.assert_not_called();self.assertEqual(panel.steps,[]);panel.restore.assert_called_once()

if __name__=='__main__':unittest.main()
