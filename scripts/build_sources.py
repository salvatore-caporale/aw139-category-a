from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,subprocess
from PIL import Image
base=Path('aw139-category-a');out=base/'web'/'charts';out.mkdir(parents=True,exist_ok=True)
pages=json.loads((base/'research/pages.json').read_text());tr=str.maketrans({chr(i):str(i-19)for i in range(23,28)})
extra={10,15,18,23,24,25,37,83,84,85,119,120,135,153,154,155,187,188,229,230,231,232,275,276,337,338,354,363,364,365,387,388,399,400,401,412,437,438,454,462,463,512,513,515,517}
parts=[(19,'A'),(81,'B'),(115,'C'),(149,'D'),(225,'E'),(271,'F'),(333,'G'),(359,'H'),(395,'I'),(451,'J'),(471,'K'),(507,'L')]
cat=[]
for row in pages:
 n=row['page'];text=row['text'].translate(tr)
 captions=re.findall(r'Figure\s+([^\s]+)\s+([^\n]*)',text)
 if not captions and n not in extra:continue
 if len(captions)>3 and n not in extra:continue
 part=next((part for first,part in reversed(parts)if n>=first),'General')
 figure=captions[-1][0] if captions else ''
 figure=figure.replace('\x10','-').replace('%','B').replace(')','F').replace('*','G').replace('+','H').replace('.','K')
 if figure.startswith('4-'):figure=figure.replace('4-','4J',1)
 label=f'Figure {figure}'if figure else f'PDF page {n}'
 cat.append({'page':n,'part':part,'label':label})
# All numerical sources must be included even if caption extraction fails.
for n in [145,197,391,354,269,441]:
 if not any(c['page']==n for c in cat):cat.append({'page':n,'part':next(part for first,part in reversed(parts)if n>=first),'label':f'PDF page {n}'})
cat.sort(key=lambda c:c['page']);(base/'web/source-catalog.js').write_text('globalThis.AW139_SOURCES='+json.dumps(cat)+';')
exe='/Users/macstudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
def render(row):
 n=row['page'];dest=out/f'p{n}.webp'
 if dest.exists():return
 temp=Path('/tmp')/f'aw139-chart-{n}'
 subprocess.run([exe,'-f',str(n),'-l',str(n),'-scale-to','2000','-png','-singlefile','/Users/macstudio/Desktop/AW139RFM.pdf',str(temp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 Image.open(str(temp)+'.png').convert('RGB').save(dest,quality=90,method=4);Path(str(temp)+'.png').unlink()
with ThreadPoolExecutor(4)as pool:list(pool.map(render,cat))
print('Built source library:',len(cat),'pages;',sum(f.stat().st_size for f in out.glob('*.webp'))//1024,'KiB')
