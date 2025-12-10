import os,collections
paths=[]
for dirpath,dirs,files in os.walk('tests'):
    for f in files:
        if f.endswith('.py'):
            paths.append(os.path.join(dirpath,f))
byname=collections.defaultdict(list)
for p in paths:
    byname[os.path.basename(p)].append(p)
for name,ps in sorted(byname.items()):
    if len(ps)>1:
        print(name)
        for p in ps:
            print('  ',p)
