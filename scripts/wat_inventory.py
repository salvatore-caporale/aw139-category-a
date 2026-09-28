import pdfplumber, json, collections
p=pdfplumber.open('/Users/macstudio/Desktop/AW139RFM.pdf')
nums=[48,49,50,51,99,100,101,102,139,140,141,142,192,193,194,195,256,257,258,259,288,289,290,291,518,519,520,521,524,525,526,527]
for n in nums:
 s=p.pages[n-1]
 print('\nPAGE',n)
 for i,c in enumerate(s.curves):
  if c['top']>180 and c['height']>50 and c['stroke'] and not c['fill']:print('C',i,'bb',[round(c[k],1)for k in ['x0','top','x1','bottom']], 'color',c['stroking_color'],'dash',c['dash'])
 for i,c in enumerate(s.lines):
  if c['top']>180 and c['height']>40 and (c['linewidth']>.7 or (c['x0']>350 and c['width']<1)): print('L',i,'bb',[round(c[k],1)for k in ['x0','top','x1','bottom']],c['linewidth'],c['stroking_color'])
