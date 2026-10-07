from pathlib import Path
import pcbnew as k
p=Path('/Users/arsenshanaqbai/Documents/KiCad/GPS-Tracker/hardware/revB');m=p/'models';m.mkdir(exist_ok=True)
b=k.LoadBoard(str(p/'Tracker-RevB.kicad_pcb'))
# Simplified envelopes, explicitly identified as approximate in review.md.
for f in b.GetFootprints():
 dims={'U3':(23.6,19.9,2.2),'U4':(9.7,10,2.5),'U1':(3,3,1)}.get(f.GetReference())
 if not dims:continue
 w,h,d=dims;z0=.05
 coords=[(x*w/2/2.54,y*h/2/2.54,(z0+z*d)/2.54) for x,y,z in [(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 name=f.GetReference()+'-envelope.wrl'
 color='0.65 0.67 0.69' if f.GetReference() in ['U3','U4'] else '0.13 0.14 0.15'
 (m/name).write_text('#VRML V2.0 utf8\n# Simplified candidate envelope; not a manufacturer CAD model.\nShape { appearance Appearance { material Material { diffuseColor '+color+' } } geometry IndexedFaceSet { coord Coordinate { point [ '+', '.join('%g %g %g'%v for v in coords)+' ] } coordIndex [ 0,3,2,1,-1,4,5,6,7,-1,0,1,5,4,-1,1,2,6,5,-1,2,3,7,6,-1,3,0,4,7,-1 ] } }')
 f.Models().clear();model=k.FP_3DMODEL();model.m_Filename='${KIPRJMOD}/models/'+name;f.Add3DModel(model)
k.SaveBoard(str(p/'Tracker-RevB.kicad_pcb'),b)
