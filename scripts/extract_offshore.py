import json,collections,math
from pathlib import Path
ns={};exec(Path('aw139-category-a/scripts/extract_wat.py').read_text().split('data={}')[0],ns)
PDF=ns['PDF'];points=ns['points'];out={}
def ps(s,ids):return [[[round(x,5),round(y,5)]for x,y in points(s.curves[i])]for i in ids]
def grids(s):
 c=collections.Counter((round(l['x0'],3),round(l['x1'],3))for l in s.lines if l['height']<.01 and l['width']>50 and l['top']>300)
 return sorted([v for v,n in c.items()if n>20])
for n,start,groups,fig in [(443,12,[[20]]+[[i,i+1]for i in range(21,30,2)],'4I-2'),(445,14,[[i,i+1]for i in range(22,34,2)],'4I-4'),(447,12,[[i,i+1]for i in range(20,32,2)],'4I-6'),(449,6,[list(range(14,17)),list(range(18,23)),list(range(24,31)),list(range(31,40)),list(range(40,50)),list(range(50,60))],'4I-8')]:
 s=PDF.pages[n-1];g=grids(s)
 # Plot frames use rectangles on the older offshore charts.
 x0=s.curves[start]['x0'];x1=s.curves[start]['x1']
 if n==443:d0,d1=215.9042,533.627
 elif n==445:d0,d1=212.8302,530.553
 elif n==447:d0,d1=200.1481,524.49
 else:d0,d1=268.268,538.107
 print(n,'grids',g,'rects',[(round(r['x0'],2),round(r['x1'],2))for r in s.rects if r['width']>100 and r['height']>100])
 out[str(n)]={'page':n,'figure':fig,'kind':'offshoreBL','oatAxis':[x0,x1,-40,50],'distanceAxis':[d0,d1,0,600],'pressure':[{'value':-1000+j*1000,'paths':ps(s,[start+j])}for j in range(7)],'weight':[{'value':4400+j*400,'paths':ps(s,g)}for j,g in enumerate(groups)]}
# Assign pieces to their labelled OAT curves by endpoint continuity.
cto=[(261,[36,35,34,33,32,31,37,38,39,40],list(range(12,41))+[44]),(263,[28,29,30,31,32,33,34,35,36,37],list(range(12,38))),(265,[30,31,32,33,34,35,36,37,38,29],list(range(12,39))),(267,[29,30,31,32,33,34,35,36,37,38],list(range(12,39))+[52,53,54])]
for ci,(n,seeds,ids) in enumerate(cto):
 s=PDF.pages[n-1];g=grids(s);g0,g1=g[:2]
 groups={t:[seed]for t,seed in zip(range(-40,51,10),seeds)};unassigned=set(ids)-set(seeds)
 while True:
  best=None
  for i in unassigned:
   a=points(s.curves[i])
   for t,group in groups.items():
    for j in group:
     b=points(s.curves[j]);dist=min(math.dist(x,y)for x in [a[0],a[-1]]for y in [b[0],b[-1]])
     if best is None or dist<best[0]:best=(dist,i,t)
  if best is None or best[0]>1.2:break
  groups[best[2]].append(best[1]);unassigned.remove(best[1])
 print(n,'unassigned',sorted(unassigned),'groups',groups)
 out[str(n)]={'page':n,'figure':['4E-4','4E-5','4E-6','4E-6A'][ci],'kind':'offshoreCTO','paAxis':[g0[0],g0[1],-1000,5000],'distanceAxis':[g1[0],g1[1],230,370],'weight':[{'value':4400+j*400,'paths':ps(s,[6+j])}for j in range(6)],'temperature':[{'value':t,'paths':ps(s,ids)}for t,ids in groups.items()]}
Path('aw139-category-a/web/offshore-data.js').write_text('globalThis.AW139_OFFSHORE='+json.dumps(out,separators=(',',':'))+';\n')
