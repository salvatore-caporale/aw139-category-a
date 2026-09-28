"""Digitize the supplied PDF vector paths, preserving source-page provenance.
Curve coordinates are converted using the printed axes; no aircraft model is fitted.
"""
import pdfplumber,json,collections,math
from pathlib import Path
PDF=pdfplumber.open('/Users/macstudio/Desktop/AW139RFM.pdf')
OUT=Path('aw139-category-a/web');OUT.mkdir(exist_ok=True)
groups={'A':[48,49,50,51],'B':[99,100,101,102],'C':[139,140,141,142],'D':[192,193,194,195],'E':[256,257,258,259],'F':[288,289,290,291],'L':[518,519,520,521],'LC':[524,525,526,527]}
figs={'A':['4A-3','4A-4','4A-5','4A-5A'],'B':['4B-1','4B-2','4B-3','4B-3A'],'C':['4C-3','4C-4','4C-5','4C-5A'],'D':['4D-4','4D-5','4D-6','4D-6A'],'E':['4E-1','4E-2','4E-3','4E-3A'],'F':['4F-1','4F-2','4F-3','4F-3A'],'L':['4L-1','4L-2','4L-3','4L-4'],'LC':['4L-7','4L-8','4L-9','4L-10']}
def points(c):
 out=[];start=None
 for cmd in c['path']:
  if cmd[0]=='m':out.append(cmd[1]);start=cmd[1]
  elif cmd[0]=='l':out.append(cmd[1])
  elif cmd[0]=='c':
   a=out[-1];b,d,e=cmd[1:]
   for k in range(1,41):
    t=k/40;u=1-t;out.append(tuple(u**3*a[i]+3*u*u*t*b[i]+3*u*t*t*d[i]+t**3*e[i] for i in [0,1]))
  elif cmd[0]=='h' and start:out.append(start)
 return out

def intersections(pts,y):
 xs=[]
 for a,b in zip(pts,pts[1:]):
  if abs(b[1]-a[1])>1e-8 and min(a[1],b[1])-1e-7<=y<=max(a[1],b[1])+1e-7:
   xs.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return xs

data={}
for family,nums in groups.items():
 for config,n in enumerate(nums):
  s=PDF.pages[n-1]
  idx=list(range(6,16));temps=list(range(-40,51,10));caps=[]
  if family=='E':idx=list(range(15,24)) if n==256 else list(range(12,21)) if n in [257,258] else list(range(6,15));temps=list(range(-30,51,10));caps=[-40]
  if n==288:idx=[6,7,8,9,11,12,13,14,15];temps=list(range(-40,41,10));caps=[50]
  if n==291:idx=list(range(6,13));temps=list(range(-10,51,10));caps=[-40,-30,-20]
  if n==524:idx=list(range(6,12));temps=list(range(-20,31,10));caps=[-40,-30,40,50]
  if n==525:idx=list(range(6,14));temps=list(range(-30,41,10));caps=[-40,50]
  if n==527:idx=list(range(6,11));temps=list(range(10,51,10));caps=list(range(-40,1,10))
  xmin=5800 if family=='E' and n!=258 else 4800 if n==258 else 4400 if family in ['A','B','C'] and config==3 else 4200
  xmax=7000 if family=='E' else 6500 if xmin==4400 else 6400 if family in ['L','LC'] else 6600
  paMax=5000 if family=='E' else 10000 if family=='D' or config==3 else 14000
  first=s.curves[idx[0]];bottom=max(s.curves[i]['bottom'] for i in idx)
  if n not in [257,258]:
   horiz=[l for l in s.lines if l['width']>250 and l['height']<.1 and 180<l['top']<bottom+1]
   key=collections.Counter((round(l['x0'],1),round(l['x1'],1))for l in horiz).most_common(1)[0][0]
   lines=[l for l in horiz if (round(l['x0'],1),round(l['x1'],1))==key]
   x0=sum(l['x0']for l in lines)/len(lines);x1=sum(l['x1']for l in lines)/len(lines)
   y0=min(l['top'] for l in lines);y1=max(l['top'] for l in lines)
  else:
   box=s.curves[10];x0=box['x0']+.35;x1=box['x1']-.35;y0=box['top']+.35;y1=box['bottom']-.35
  def convert(p):return [round(xmin+(p[0]-x0)/(x1-x0)*(xmax-xmin),3),round(paMax-(p[1]-y0)/(y1-y0)*(paMax+1000),3)]
  curves=[]
  for i,t in zip(idx,temps):
   c=s.curves[i];pts=points(c)
   if n in [257,258]:
    # These PDF pages encode strokes as closed filled outlines.
    ys=sorted(set([p[1]for p in pts]+[c['top']+(c['bottom']-c['top'])*j/400 for j in range(1,400)]))
    pts=[(sum(xx)/len(xx),y)for y in ys if len(xx:=intersections(pts,y))>0]
   curves.append({'oat':t,'points':[convert(p)for p in pts]})
  cap=6800 if family=='E' else 6200 if family in ['L','LC'] else 6400
  for curve in curves:
   for point in curve['points']:
    if abs(point[0]-cap)<3: point[0]=cap
  for t in caps:
   top=paMax if t<=30 else 5000 if t==40 else 0
   curves.append({'oat':t,'points':[[cap,-1000],[cap,top]]})
  limits=[]
  for i,c in enumerate(s.curves):
   col=c.get('stroking_color');blue=isinstance(col,(tuple,list))and len(col)==3 and col[2]>col[0]+.2
   if blue and c['top']>=y0-2 and c['bottom']<=y1+2 and c['height']>20:limits.append([convert(p)for p in points(c)])
  wind=[]
  if family in ['A','B','C','E'] and n not in [257,258]:
   cs=[c for c in s.curves if c['stroke'] and not c['fill'] and c['top']>=y1+1 and c['bottom']<710 and c['height']>40 and c['width']>1]
   for c in cs:
    ps=points(c);top=c['top'];bot=c['bottom'];wind.append({'base':round(convert(ps[0])[0],2),'points':[[round(convert(p)[0],3),round(20*(p[1]-top)/(bot-top),4)]for p in ps]})
  data[f'{family}-{config}']={'page':n,'figure':figs[family][config],'family':family,'config':config,'paMax':paMax,'densityMax':5000 if family=='E' else 10000 if family=='D' else 14000,'cap':cap,'curves':sorted(curves,key=lambda c:c['oat']),'limits':limits,'wind':wind,'calibration':{'weight':[xmin,xmax],'pa':[-1000,paMax],'box':[x0,y0,x1,y1]}}
  print(n,'axes',xmin,xmax,paMax,[round(v,2)for v in [x0,y0,x1,y1]],'curves',len(curves),'limits',len(limits),'wind',len(wind))
(OUT/'wat-data.js').write_text('globalThis.AW139_WAT='+json.dumps(data,separators=(',',':'))+';\n')
Path('aw139-category-a/research/wat-data.json').write_text(json.dumps(data,indent=2))
