import pdfplumber,json,collections
from pathlib import Path
# Reuse the vector sampler without executing the WAT extraction.
ns={};exec(Path('aw139-category-a/scripts/extract_wat.py').read_text().split('data={}')[0],ns)
PDF=ns['PDF'];points=ns['points'];intersections=ns['intersections']
def C(*a):return [('c',i)for i in a]
def L(*a):return [('l',i)for i in a]
def pairs(start):return [C(i,i+1)for i in range(start,start+12,2)]
meta={
53:dict(figure='4A-6',temp=C(*range(6,15))+L(120),weight=pairs(15),pa=14000,dist=[0,800],limit=42),
111:dict(figure='4B-7',temp=C(*range(6,15))+L(120),weight=pairs(15),pa=14000,dist=[0,800],limit=42),
143:dict(figure='4C-6',temp=C(*range(6,15))+L(120),weight=pairs(15),pa=14000,dist=[0,800],limit=42),
199:dict(figure='4D-9',temp=C(*range(6,14),15)+L(91),weight=pairs(16),pa=10000,dist=[0,600],limit=14),
301:dict(figure='4F-7',temp=C(*range(6,15))+L(102),weight=[C(15,16),C(17,18),L(265),L(264),L(263)+C(19),C(20,21)],pa=14000,dist=[0,500],limit=37),
303:dict(figure='4F-8',temp=C(*range(6,15))+L(102),weight=[C(15,16),C(17,18),L(261),L(260),L(259),L(257)],pa=14000,dist=[0,500],limit=20),
305:dict(figure='4F-9',temp=C(*range(6,15))+L(102),weight=[C(15,16),C(17,18),L(260),L(259),L(258),L(256)],pa=14000,dist=[0,500],limit=20),
307:dict(figure='4F-9A',temp=C(*range(6,16)),weight=pairs(17),pa=14000,dist=[100,500],limit=16),
293:dict(figure='4F-4',temp=C(*range(6,15))+L(105),weight=[C(15,16),C(17,18),L(288),L(287),L(286),L(285)],pa=14000,dist=[0,1800],limit=34),
295:dict(figure='4F-5',temp=C(*range(6,15))+L(106),weight=[C(15,16),C(17,18),L(287),L(286),L(285),L(284)],pa=14000,dist=[0,2000],limit=20),
297:dict(figure='4F-6',temp=C(*range(6,15))+L(106),weight=[C(15,16),C(17,18),L(287),L(286),L(285),L(284)],pa=14000,dist=[0,2000],limit=23),
299:dict(figure='4F-6A',temp=C(*range(6,15))+L(109),weight=[C(i)for i in range(16,22)],pa=14000,dist=[0,1800],limit=15),
357:dict(figure='4G-2',temp=C(*range(6,16)),weight=[C(16)],pa=14000,dist=[0,500],limit=25),
393:dict(figure='4H-4',temp=C(*range(6,15),16),weight=[C(i)for i in range(22,16,-1)],pa=10000,dist=[0,400],limit=15),
465:dict(figure='4J-1',temp=C(*range(7,17)),weight=[C(i)for i in range(22,16,-1)],pa=14000,dist=[0,600],limit=6),
467:dict(figure='4J-2/1',temp=C(*range(6,16)),weight=[C(i)for i in range(21,15,-1)],pa=14000,dist=[0,600],limit=22),
}
# Short Field RTO uses a third panel for the TDP.
for n,fig in [(103,'4B-4'),(105,'4B-5'),(107,'4B-6'),(109,'4B-6A')]:
 s=PDF.pages[n-1]
 # The IBF chart has different path ordering; extracted separately after visual calibration.
 if n==109:
  diag=[i for i,l in enumerate(s.lines)if l['width']>4 and l['height']>4 and l['top']>450 and l['x0']<386]
  meta[n]=dict(figure=fig,temp=C(*range(6,15))+L(diag[0]),weight=[C(i)for i in range(16,22)],pa=14000,dist=[0,1],limit=15,tdp=list(range(22,31)),ascending=True)
  continue
 diag=[i for i,l in enumerate(s.lines)if l['width']>4 and l['height']>4 and l['top']>400 and l['x0']<377]
 meta[n]=dict(figure=fig,temp=C(*range(6,15))+L(diag[0]),weight=[C(i)for i in range(15,21)],pa=14000,dist=[0,1],limit=41 if n==103 else 30,tdp=list(range(21,30)),ascending=True)

data={}
for n,m in meta.items():
 s=PDF.pages[n-1]
 def pts(ref):
  typ,i=ref
  return points(s.curves[i]) if typ=='c' else list(s.lines[i]['pts'])
 def paths(refs):return [[[round(a,5),round(b,5)]for a,b in pts(r)]for r in refs]
 counts=collections.Counter((round(l['x0'],3),round(l['x1'],3))for l in s.lines if l['height']<.01 and l['width']>50 and l['top']>300)
 grids=sorted([v for v,c in counts.items()if c>20])
 # deduplicate near-identical grid bounds
 grids=[g for j,g in enumerate(grids)if j==0 or abs(g[0]-grids[j-1][0])>1]
 g0,g1=grids[:2]
 groups=[{'value':v,'paths':paths(r)}for v,r in zip(range(6400,4399,-400) if not m.get('ascending') else range(4400,6401,400),m['weight'])]
 if len(groups)==1:groups[0]['value']=None
 d=dict(page=n,figure=m['figure'],paAxis=[g0[0],g0[1],m['pa'],-1000],distanceAxis=[g1[0],g1[1],*m['dist']],temperature=[{'value':t,'paths':paths([r])}for t,r in zip(range(-40,51,10),m['temp'])],weight=groups)
 if m.get('limit') is not None:d['maxOAT']=paths(C(m['limit']))
 if 'tdp'in m:
  d['tdp']=[{'value':h,'paths':paths(C(i))}for h,i in zip([35,50,100,150,200,250,300,350,400],m['tdp'])]
  c=s.curves[m['tdp'][-1]]
  # top-panel grid: printed 150 .. 850 m.
  ys=[l['top']for l in s.lines if l['height']<.01 and abs(l['x0']-g1[0])<.1 and abs(l['x1']-g1[1])<.1 and l['top']<s.curves[m['tdp'][0]]['bottom']+2 and l['top']>200]
  d['tdpAxis']=[max(ys),min(ys),150,850]
 data[str(n)]=d
 print(n,'grids',grids,'temp',len(d['temperature']),'weight',len(groups),'tdp',d.get('tdpAxis'))
# Braking chart: PA axis increases left to right, unlike the airborne charts.
s=PDF.pages[468]
data['469']=dict(page=469,figure='4J-2/2',paAxis=[95.87588,298.62,-1000,14000],distanceAxis=[302.461,521.897,0,300],temperature=[{'value':t,'paths':paths([r])}for t,r in zip(range(-40,51,10),C(*range(128,136))+L(142,141))],weight=[{'value':4400+200*j,'paths':paths(C(6+j))}for j in range(11)],maxOAT=paths(L(140)))
Path('aw139-category-a/web/distance-data.js').write_text('globalThis.AW139_DISTANCE='+json.dumps(data,separators=(',',':'))+';\n')
