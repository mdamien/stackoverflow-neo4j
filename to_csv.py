import json, sys, os, xmltodict, csv
from os.path import join
from fun import *

PATH = sys.argv[1]
DIR = PATH.replace('extracted/','')

print("importing",DIR)

file = join(PATH,'Posts.xml')

def clean(x):
    return x.replace('\n','').replace('\r','').replace('"','')

spamWriter = csv.writer(open('csvs/posts.csv', 'w'))
spamWriter_rels = csv.writer(open('csvs/posts_rel.csv', 'w'))

spamWriter.writerow(['postId:ID(Post)', 'userId', 'title', 'body'])
spamWriter_rels.writerow([':START_ID(Post)', ':END_ID(Post)'])

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            el = replace_keys(el)
            spamWriter.writerow([
                el['id'], el.get('owneruserid'),
                clean(el.get('title','')),
                clean(el.get('body',''))
            ])
            if el.get('parentid'):
                spamWriter_rels.writerow([el['parentid'],el['id']])
    except Exception as e:
        print('x')
    if i % 5000 == 0:
        print('.',end='')
    if i > 1000: #only a small sample
        break