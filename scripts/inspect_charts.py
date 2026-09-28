import pdfplumber,sys,json
p=pdfplumber.open('/Users/macstudio/Desktop/AW139RFM.pdf')
for n in map(int,sys.argv[1:]):
 s=p.pages[n-1];print('\nPAGE',n)
 for j,c in enumerate(s.curves):
  if j>=6:print(j,tuple(round(c[k],2) for k in ['x0','top','x1','bottom','linewidth']),len(c['pts']),c['stroke'],c['fill'],c['path'][:2])
 print('LABELS',[(w['text'],round(w['x0'],1),round(w['top'],1))for w in s.extract_words() if w['text'] in ['42','44','64','-1','0','1','10','14','50','-40']])
