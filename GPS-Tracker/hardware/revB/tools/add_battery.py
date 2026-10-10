from pathlib import Path
import pcbnew as k
p=Path(__file__).resolve().parents[1]
m=p/'models';m.mkdir(exist_ok=True)
# Millimetres converted to KiCad VRML units. Top of battery sits 1 mm below 1.6 mm PCB.
def box(x,y,z,w,h,d,color):
 pts=[((x+dx*w)/2.54,(y+dy*h)/2.54,(z+dz*d)/2.54) for dx,dy,dz in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
 return 'Shape { appearance Appearance { material Material { diffuseColor '+color+' } } geometry IndexedFaceSet { coord Coordinate { point [ '+', '.join('%g %g %g'%t for t in pts)+' ] } coordIndex [ 0,3,2,1,-1,4,5,6,7,-1,0,1,5,4,-1,1,2,6,5,-1,2,3,7,6,-1,3,0,4,7,-1 ] } }\n'
shapes=box(-30,-20,-8.6,60,40,6,'0.82 0.57 0.08')
shapes+=box(-28.5,-18.5,-8.65,57,37,.12,'0.72 0.75 0.78')
shapes+=box(-28.5,-18.5,-2.6,57,37,.12,'0.72 0.75 0.78')
# Bottom label makes battery readable from underside.
shapes+=box(-20,-11,-8.8,40,22,.12,'0.12 0.16 0.20')
# Stylized leads towards battery connector; visual only, no electrical net representation.
shapes+=box(-1,-22,-5.8,.9,3,.9,'0.85 0.04 0.04')
shapes+=box(1,-22,-5.8,.9,3,.9,'0.03 0.03 0.03')
(m/'LiPo-60x40x6-concept.wrl').write_text('#VRML V2.0 utf8\n# Mechanical placeholder. No selected capacity or commercial cell.\n'+shapes)
b=k.LoadBoard(str(p/'Tracker-RevB.kicad_pcb'))
for f in list(b.GetFootprints()):
 if f.GetReference()=='BT1':b.Remove(f)
f=k.FOOTPRINT(b);f.SetReference('BT1');f.SetValue('LiPo 60x40x6 CONCEPT');f.SetPosition(k.VECTOR2I(k.FromMM(145),k.FromMM(130)));f.SetAttributes(k.FP_EXCLUDE_FROM_BOM|k.FP_EXCLUDE_FROM_POS_FILES);f.Reference().SetVisible(False);f.Value().SetVisible(False)
model=k.FP_3DMODEL();model.m_Filename='${KIPRJMOD}/models/LiPo-60x40x6-concept.wrl';f.Add3DModel(model);b.Add(f)
# New view file avoids overwriting the user's open PCB document.
k.SaveBoard(str(p/'Tracker-RevB-Battery.kicad_pcb'),b)
print('Battery variant saved: 60 x 40 x 6 mm; 1 mm gap below PCB; mechanical placeholder only.')
