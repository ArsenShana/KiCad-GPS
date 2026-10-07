from pathlib import Path
import pcbnew as k,json
BASE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
OUT=Path('/Users/arsenshanaqbai/Documents/KiCad/GPS-Tracker/hardware/revB')
parts=json.loads((OUT/'placement.json').read_text());links=json.loads((OUT/'connectivity.json').read_text())
b=k.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(k.FromMM(1.6))
v=lambda x,y:k.VECTOR2I(k.FromMM(x),k.FromMM(y))
# Board origin offset permits convenient editing in the canvas.
ox,oy=100,100
for a,z in [((0,0),(90,0)),((90,0),(90,60)),((90,60),(0,60)),((0,60),(0,0))]:
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(v(ox+a[0],oy+a[1]));s.SetEnd(v(ox+z[0],oy+z[1]));s.SetLayer(k.Edge_Cuts);s.SetWidth(k.FromMM(.1));b.Add(s)
netmap={}
for name in sorted({n for r in links.values() for n in r.values()}):
 net=k.NETINFO_ITEM(b,"/"+name);b.Add(net);netmap[name]=net
pos={'J1':(15,56,0),'U1':(30,44,0),'U2':(20,20,0),'U3':(62,25,0),'U4':(42,13,0),'U5':(37,27,0),'U6':(39,39,0),'R1':(11,48,0),'R2':(17,48,0),'R3':(25,44,90),'R4':(25,48,90),'C1':(24,37,90),'C2':(35,44,90),'C3':(35,13,90),'C4':(37,34,0),'J2':(45,52,0),'J3':(14,37,0)}
missing=[]
for part in parts:
 ref=part['ref'];lib,name=part['footprint'].split(':');f=k.FootprintLoad(str(BASE/'footprints'/(lib+'.pretty')),name)
 if f is None:raise RuntimeError(part['footprint'])
 f.SetReference(ref);f.SetValue(part['value']);x,y,angle=pos[ref];f.SetPosition(v(ox+x,oy+y));f.SetOrientationDegrees(angle);b.Add(f)
 f.SetFPID(k.LIB_ID(lib,name))
 f.Reference().SetTextSize(v(.9,.9));f.Reference().SetTextThickness(k.FromMM(.15));# Preserve the library reference placement rather than placing text on pads.
 f.Value().SetVisible(False)
 nums={pad.GetNumber() for pad in f.Pads()}
 for number,net in links.get(ref,{}).items():
  if number not in nums:missing.append((ref,number,net))
 for pad in f.Pads():
  n=links.get(ref,{}).get(pad.GetNumber())
  if n:pad.SetNet(netmap[n])
for i,(x,y) in enumerate([(4,4),(86,4),(4,56),(86,56)],1):
 f=k.FootprintLoad(str(BASE/'footprints'/'MountingHole.pretty'),'MountingHole_2.2mm_M2');f.SetReference('H'+str(i));f.SetPosition(v(ox+x,oy+y));b.Add(f);f.Value().SetVisible(False)
def text(s,x,y,size=1,layer=k.F_SilkS):
 t=k.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(ox+x,oy+y));t.SetTextSize(v(size,size));t.SetTextThickness(k.FromMM(.15));t.SetLayer(layer);b.Add(t)
def rectangle(x,y,w,h,label):
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_RECT);s.SetStart(v(ox+x,oy+y));s.SetEnd(v(ox+x+w,oy+y+h));s.SetLayer(k.Dwgs_User);s.SetWidth(k.FromMM(.2));b.Add(s);text(label,x+w/2,y+h/2,.8,k.Dwgs_User)
text('GPS TRACKER / REV B',63,48,1.4)
text('ENGINEERING DRAFT',64,52,1)
text('USB-C',15,61,.9,k.Dwgs_User);text('LiPo',45,57,.9,k.Dwgs_User);text('SWD',14,44,.9,k.Dwgs_User)
rectangle(9,5,21,7,'BLE RF / MATCHING TBD')
rectangle(49,43,10,4,'eUICC MFF2 TBD')
rectangle(70,9,12,7,'LTE ANT / RF TBD')
rectangle(32,3,23,5,'GNSS ANT / RF TBD')
rectangle(24,52,13,6,'RAILS / ESD TBD')
text('90 x 60 mm | 4-layer planning | NO ROUTING',45,65,1,k.Dwgs_User)
k.SaveBoard(str(OUT/'Tracker-RevB.kicad_pcb'),b)
(OUT/'pad-audit.json').write_text(json.dumps({'missing_numbered_pads':missing,'assigned_net_count':len(netmap),'board_status':'unrouted electrical draft'},indent=2))
if missing:raise RuntimeError(missing)
print('All mapped schematic pin numbers exist on PCB footprints;',len(netmap),'named nets.')
