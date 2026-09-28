import json,sys
p=json.load(open('aw139-category-a/research/pages.json'))
t=str.maketrans({chr(i):str(i-19)for i in range(23,28)})
for n in map(int,sys.argv[1:]):print('\nPAGE',n,'\n',p[n-1]['text'].translate(t))
