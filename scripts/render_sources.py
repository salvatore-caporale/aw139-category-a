from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
pages=[48,49,50,51,99,100,101,102,139,140,141,142,192,193,194,195,256,257,258,259,288,289,290,291,518,519,520,521,524,525,526,527,53,103,111,143,199,261,263,265,267,293,295,297,299,301,303,305,307,357,391,393,441,443,444,445,446,447,448,449,465,467,469,512,513,515,517]
exe='/Users/macstudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
out=Path('aw139-category-a/research');
def render(n):
 dest=out/f'p{n}'
 if not dest.with_suffix('.png').exists():subprocess.run([exe,'-f',str(n),'-l',str(n),'-scale-to','1200','-png','-singlefile','/Users/macstudio/Desktop/AW139RFM.pdf',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(4) as pool:list(pool.map(render,pages))
print('Rendered',len(pages),'source pages')
