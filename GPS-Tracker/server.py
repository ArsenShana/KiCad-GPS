from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import ctypes, json, threading, os
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
lib=ctypes.CDLL(str(ROOT/'firmware/libtracker.dylib'))
lib.step.argtypes=[ctypes.c_int,ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]
for n in ['sent','lost','head_id']:getattr(lib,n).restype=ctypes.c_uint64
for n in ['head_lat','head_lon']:getattr(lib,n).restype=ctypes.c_double
lock=threading.Lock()
class Handler(SimpleHTTPRequestHandler):
 def do_POST(self):
  try:
   length=int(self.headers.get('Content-Length',0))
   if length>4096:raise ValueError('request too large')
   data=json.loads(self.rfile.read(length) or b'{}')
   with lock:
    if self.path=='/reset':lib.reset()
    elif self.path=='/step':
     lib.step(bool(data.get('fix')),float(data.get('lat',43.238)),float(data.get('lon',76.945)),bool(data.get('cell')),bool(data.get('ble')),bool(data.get('internet')),bool(data.get('ack')))
    else:self.send_error(404);return
    result={n:getattr(lib,n)() for n in ['pending','channel','sent','lost','head_id','head_lat','head_lon']}
   body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  except (ValueError,TypeError) as e:self.send_error(400,str(e))
if __name__=='__main__':
 print('Simulation: http://127.0.0.1:8765',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
