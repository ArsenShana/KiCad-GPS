import ctypes
from pathlib import Path
l=ctypes.CDLL(str(Path(__file__).with_name('libtracker.dylib')))
l.step.argtypes=[ctypes.c_int,ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]
def tick(f=1,c=0,b=0,i=0,a=0):l.step(f,43.2,76.9,c,b,i,a)
l.reset();tick(c=1,a=1);assert l.sent()==1 and l.pending()==0 and l.channel()==1
tick(b=1,i=1,a=1);assert l.sent()==2 and l.channel()==2
tick(b=1,a=1);assert l.pending()==1 and l.channel()==3
first=l.head_id();tick(f=0,c=1);assert l.head_id()==first and l.pending()==1
tick(f=0,c=1,a=1);assert l.pending()==0
l.reset()
for _ in range(257):tick()
assert l.pending()==256 and l.lost()==1
for _ in range(256):tick(f=0,b=1,i=1,a=1)
assert l.pending()==0 and l.sent()==256
l.reset();tick(f=0,c=1,a=1);assert l.sent()==0
print('PASS: LTE, phone fallback, offline, ACK retry, overflow, drain, no GNSS')
