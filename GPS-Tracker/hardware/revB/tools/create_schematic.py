from pathlib import Path
import re,json,uuid,copy
BASE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport'); OUT=Path('/Users/arsenshanaqbai/Documents/KiCad/GPS-Tracker/hardware/revB');OUT.mkdir(exist_ok=True)
def extract(lib,name):
 s=(BASE/'symbols'/f'{lib}.kicad_sym').read_text();m=re.search(r'\(symbol "'+re.escape(name)+r'"\s',s);start=m.start();tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s[start:]);stack=[]
 for t in tokens:
  if t=='(':stack.append([])
  elif t==')':
   a=stack.pop()
   if not stack:return a
   stack[-1].append(a)
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
def children(a,key):return [x for x in a if isinstance(x,list) and x and x[0]==key]
def first(a,key):return next((x for x in a if isinstance(x,list) and x and x[0]==key),None)
def resolved(lib,name):
 a=extract(lib,name);ext=first(a,'extends')
 if ext:
  base=resolved(lib,ext[1]);sub=[copy.deepcopy(x) for x in children(base,'symbol')]
  for s in sub:s[1]=s[1].replace(ext[1],name)
  a=[x for x in a if x!=ext]+sub
 return a
parts=[('Connector','USB_C_Receptacle_USB2.0_16P','J1'),('Battery_Management','BQ24074RGT','U1'),('MCU_Nordic','nRF52840','U2'),('RF_GSM','BG95-M3','U3'),('RF_GPS','MAX-M10S','U4'),('Memory_Flash','W25Q32JVSS','U5'),('Logic_LevelTranslator','TXS0102DCT','U6')]
for lib,name,ref in parts:
 a=resolved(lib,name)
 print(ref,name, [(first(x,'number')[1],first(x,'name')[1]) for s in children(a,'symbol') for x in children(s,'pin')]);print('FP',[(x[1],x[2]) for x in children(a,'property') if x[1]=='Footprint'])
import csv,math
# Revision B is an electrically incomplete review design. Never suppress missing connections.
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s))
def render(a):
 if isinstance(a,list):return '('+' '.join(render(x) for x in a)+')'
 return q(a) if (a=='' or any(c in a for c in ' \n"()') or a.startswith('http') or a in ['Reference','Value','Footprint','Datasheet']) else a
# Always quote identifiers that KiCad expects as strings using original serializer heuristics.
string_second={'symbol','lib_id','uuid','label','text','name','number','project','path','reference','value'}
def emit(a):
 if not isinstance(a,list):return str(a)
 out=[]
 for i,x in enumerate(a):
  if isinstance(x,list):out.append(emit(x))
  elif (a[0]=='property' and i in [1,2]) or (a[0] in string_second and i==1) or (a[0]=='description' and i==1):out.append(q(x))
  elif any(c in x for c in ' \n"()') or x=='':out.append(q(x))
  else:out.append(x)
 return '('+' '.join(out)+')'
placements=[('Connector','USB_C_Receptacle_USB2.0_16P','J1',45,57,'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal'),('Battery_Management','BQ24074RGT','U1',112,58,None),('MCU_Nordic','nRF52840','U2',105,168,None),('RF_GSM','BG95-M3','U3',295,113,None),('RF_GPS','MAX-M10S','U4',201,60,None),('Memory_Flash','W25Q32JVSS','U5',201,118,None),('Logic_LevelTranslator','TXS0102DCT','U6',201,167,None),('Device','R','R1',25,95,'Resistor_SMD:R_0603_1608Metric'),('Device','R','R2',45,95,'Resistor_SMD:R_0603_1608Metric'),('Device','R','R3',82,90,'Resistor_SMD:R_0603_1608Metric'),('Device','R','R4',102,90,'Resistor_SMD:R_0603_1608Metric'),('Device','C','C1',18,57,'Capacitor_SMD:C_0603_1608Metric'),('Device','C','C2',141,58,'Capacitor_SMD:C_0603_1608Metric'),('Device','C','C3',178,88,'Capacitor_SMD:C_0603_1608Metric'),('Device','C','C4',222,118,'Capacitor_SMD:C_0603_1608Metric'),('Connector_Generic','Conn_01x02','J2',140,90,'Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical'),('Connector_Generic','Conn_02x05_Odd_Even','J3',200,207,'Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical')]
values={'R1':'5.1k','R2':'5.1k','R3':'ISET_TBD','R4':'ILIM_TBD','C1':'4.7uF','C2':'4.7uF','C3':'100nF','C4':'100nF','J2':'PROTECTED_LIPO','J3':'SWD_REVIEW'}
# Explicit connection intent, not a validated reference design.
nets={
'J1':{'GND':'GND','VBUS':'USB_5V','CC1':'USB_CC1','CC2':'USB_CC2','D+':'USB_DP','D-':'USB_DM'},
'U1':{'BAT':'BAT_PROTECTED','IN':'USB_5V','OUT':'SYS_CHARGER','VSS':'GND','~{CE}':'GND','EN1':'GND','EN2':'GND','ISET':'CHG_ISET','ILIM':'CHG_ILIM'},
'U2':{'VDD':'3V3_TBD','VSS':'GND','VSS_PA':'GND','VBUS':'USB_5V','D+':'USB_DP','D-':'USB_DM','SWDCLK':'SWDCLK','SWDIO':'SWDIO','P0.18/~{RESET}':'MCU_RESET','P0.06':'MCU_MODEM_TX','P0.08':'MCU_MODEM_RX','P0.26':'GNSS_RX','P0.27':'GNSS_TX','P0.13':'FLASH_CS','P0.14':'FLASH_MISO','P0.15':'FLASH_MOSI','P0.16':'FLASH_SCK','ANT':'BLE_RF_REVIEW'},
'U3':{'GND':'GND','USIM_GND':'GND','VBAT_BB':'MODEM_VBAT_TBD','VBAT_RF':'MODEM_VBAT_TBD','VDD_EXT':'MODEM_1V8','MAIN_RXD':'MODEM_RX_1V8','MAIN_TXD':'MODEM_TX_1V8','USIM_VDD':'SIM_VDD','USIM_RST':'SIM_RST','USIM_DATA':'SIM_DATA','USIM_CLK':'SIM_CLK','ANT_MAIN':'LTE_RF_REVIEW'},
'U4':{'GND':'GND','VCC':'3V3_TBD','VCC_IO':'3V3_TBD','TXD':'GNSS_RX','RXD':'GNSS_TX','RF_IN':'GNSS_RF_REVIEW','V_BCKP':'GNSS_BACKUP_TBD'},
'U5':{'VCC':'3V3_TBD','GND':'GND','~{CS}':'FLASH_CS','DO/IO_{1}':'FLASH_MISO','DI/IO_{0}':'FLASH_MOSI','CLK':'FLASH_SCK'},
'U6':{'GND':'GND','VCCA':'MODEM_1V8','VCCB':'3V3_TBD','A1':'MODEM_RX_1V8','A2':'MODEM_TX_1V8','B1':'MCU_MODEM_TX','B2':'MCU_MODEM_RX','OE':'UART_OE_TBD'},
'R1':{'1':'USB_CC1','2':'GND'},'R2':{'1':'USB_CC2','2':'GND'},'R3':{'1':'CHG_ISET','2':'GND'},'R4':{'1':'CHG_ILIM','2':'GND'},
'C1':{'1':'USB_5V','2':'GND'},'C2':{'1':'SYS_CHARGER','2':'GND'},'C3':{'1':'3V3_TBD','2':'GND'},'C4':{'1':'3V3_TBD','2':'GND'},'J2':{'1':'BAT_PROTECTED','2':'GND'},'J3':{'1':'3V3_TBD','2':'SWDIO','3':'GND','4':'SWDCLK','5':'GND','9':'GND','10':'MCU_RESET'}}
root=uid();libs={};instances=[];connections={};bom=[]
for lib,name,ref,x,y,fp in placements:
 x=round(x/2.54)*2.54;y=round(y/2.54)*2.54
 a=resolved(lib,name);lid=lib+':'+name
 if fp is None:fp=next((v[2] for v in children(a,'property') if v[1]=='Footprint'),'')
 if lid not in libs:
  a[1]=lid;libs[lid]=emit(a)
 val=values.get(ref,name)
 inst=f'(symbol (lib_id {q(lid)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid()})'
 for prop,v,py in [('Reference',ref,y-4),('Value',val,y-1),('Footprint',fp,y)]:
  hide=' (hide yes)' if prop=='Footprint' else ''
  inst+=f'(property {q(prop)} {q(v)} (at {x} {py} 0) (effects (font (size 1.27 1.27)){hide}))'
 inst+=f'(instances (project "Tracker-RevB" (path "/{root}" (reference "{ref}") (unit 1)))))'
 instances.append(inst);pn={}
 for sub in children(a,'symbol'):
  for pin in children(sub,'pin'):
   number=first(pin,'number')[1];pname=first(pin,'name')[1];at=first(pin,'at');net=nets.get(ref,{}).get(pname,nets.get(ref,{}).get(number))
   if not net:continue
   pn[number]=net
   px=x+float(at[1]);py=y-float(at[2]);ang=float(at[3]);dx,dy={0:(-5.08,0),180:(5.08,0),90:(0,5.08),270:(0,-5.08)}[int(ang)]
   ex,ey=px+dx,py+dy
   instances.append(f'(wire (pts (xy {px} {py}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid()}))')
   la=0 if dx else 90;just='left' if dx>=0 else 'right'
   instances.append(f'(label "{net}" (at {ex} {ey} {la}) (effects (font (size 1 1)) (justify {just} bottom)) (uuid {uid()}))')
 connections[ref]=pn;bom.append([ref,val,fp,'DRAFT: verify datasheet and assembly'])
for title,x,y in [('01 / USB-C AND POWER',18,18),('02 / MCU, USB AND DEBUG',18,115),('03 / GNSS AND A-GNSS',165,18),('04 / OFFLINE FLASH',165,95),('05 / UART LEVEL TRANSLATION',165,146),('06 / CELLULAR AND eUICC INTERFACE',250,18),('ENGINEERING REVIEW — NOT RELEASED FOR MANUFACTURE',18,245),('TBD: regulators, battery NTC, charger programming, MCU clocks/DEC, RF, eUICC, ESD, modem power control.',18,257),('Named nets show connection intent. Open pins are unresolved; see review.md and ERC report.',18,265)]:
 instances.append(f'(text {q(title)} (at {x} {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid()}))')
(OUT/'Tracker-RevB.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A3") (title_block (title "GPS Tracker / Engineering Review") (date "2026-10-07") (rev "B-DRAFT") (company "Tracker development")) (lib_symbols '+''.join(libs.values())+') '+''.join(instances)+')')
(OUT/'Tracker-RevB.kicad_pro').write_text(json.dumps({'meta':{'filename':'Tracker-RevB.kicad_pro','version':1}}))
with (OUT/'BOM.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Status']);w.writerows(bom)
(OUT/'connectivity.json').write_text(json.dumps(connections,indent=2))
(OUT/'placement.json').write_text(json.dumps([{'ref':a[2],'footprint':row[2],'value':row[1]} for a,row in zip(placements,bom)],indent=2))
