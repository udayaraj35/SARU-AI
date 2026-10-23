"""Explicit optional voice-model setup; does not record or open devices."""
import subprocess,sys
if __name__=='__main__':
 subprocess.check_call([sys.executable,'-m','pip','install','webrtcvad-wheels','torch>=2,<3','librosa>=0.11,<1','scipy>=1.12','numpy','typing'])
 subprocess.check_call([sys.executable,'-m','pip','install','--no-deps','resemblyzer==0.1.4'])
