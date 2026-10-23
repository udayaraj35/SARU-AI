"""Native Windows Store activation; no shell command parsing or elevation."""
def activate_registered(appid):
 import re
 if not re.fullmatch(r'[A-Za-z0-9_.!{}+-]{1,250}',appid):raise ValueError('Invalid registered application identifier.')
 import ctypes,comtypes
 from comtypes import IUnknown,GUID,COMMETHOD,HRESULT,CLSCTX_INPROC_SERVER
 from comtypes.client import CreateObject
 class IApplicationActivationManager(IUnknown):
  _iid_=GUID('{2E941141-7F97-4756-BA1D-9DECDE894A3D}')
  _methods_=[COMMETHOD([],HRESULT,'ActivateApplication',(['in'],ctypes.c_wchar_p,'appUserModelId'),(['in'],ctypes.c_wchar_p,'arguments'),(['in'],ctypes.c_ulong,'options'),(['out'],ctypes.POINTER(ctypes.c_ulong),'processId'))]
 comtypes.CoInitialize()
 try:
  manager=CreateObject('{45BA127D-10A8-46EA-8AB7-56EA9078943C}',interface=IApplicationActivationManager,clsctx=CLSCTX_INPROC_SERVER)
  pid=manager.ActivateApplication(appid,None,0);del manager
  return pid
 finally:comtypes.CoUninitialize()
