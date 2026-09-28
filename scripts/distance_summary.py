import pdfplumber,sys
p=pdfplumber.open('/Users/macstudio/Desktop/AW139RFM.pdf')
for n in map(int,sys.argv[1:]):
 s=p.pages[n-1];print('\nPAGE',n)
 for i,c in enumerate(s.curves):
  if i>=6 and c['top']>300 and c['width']>4 and c['height']>4:print('C',i,','.join(str(round(c[k],2))for k in ['x0','top','x1','bottom']),c['stroke'],c['fill'],c['linewidth'],c['dash'])
 print('LINES',[(i,tuple(round(c[k],2)for k in ['x0','top','x1','bottom']),c['linewidth'])for i,c in enumerate(s.lines)if c['width']>4 and c['height']>4 and c['top']>300])
