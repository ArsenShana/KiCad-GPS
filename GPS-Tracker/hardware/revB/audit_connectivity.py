from pathlib import Path
import re,json
p=Path(__file__).resolve().parent
stack=[];root=None
for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',(p/'Tracker-RevB.net').read_text()):
 if t=='(':stack.append([])
 elif t==')':
  a=stack.pop()
  if stack:stack[-1].append(a)
  else:root=a
 else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
def child(a,key):return next(x for x in a if isinstance(x,list) and x[0]==key)
actual={}
for net in child(root,'nets')[1:]:
 name=child(net,'name')[1]
 for node in [n for n in net if isinstance(n,list) and n[0]=='node']:
  actual[(child(node,'ref')[1],child(node,'pin')[1])]=name
expected=json.loads((p/'connectivity.json').read_text())
mismatch=[{'ref':r,'pin':n,'expected':v,'actual':actual.get((r,n))} for r,pins in expected.items() for n,v in pins.items() if actual.get((r,n))!='/'+v]
report={'checked_connections':sum(map(len,expected.values())),'mismatches':mismatch}
(p/'netlist-audit.json').write_text(json.dumps(report,indent=2))
assert not mismatch, mismatch
print(report)
