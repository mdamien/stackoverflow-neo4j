import json, sys, os, xmltodict, csv
from os.path import join
from fun import *

PATH = sys.argv[1]
DIR = PATH.replace('extracted/','')

print("importing",DIR)

file = join(PATH,'Posts.xml')

def clean(x):
    return x.replace('\n','').replace('\r','').replace('"','')

posts = csv.writer(open('csvs/posts.csv', 'w'))
posts_rel = csv.writer(open('csvs/posts_rel.csv', 'w'))
users = csv.writer(open('csvs/users.csv', 'w'))
users_posts_rel = csv.writer(open('csvs/users_posts_rel.csv', 'w'))
tags = csv.writer(open('csvs/tags.csv', 'w'))
tags_posts_rel = csv.writer(open('csvs/tags_posts_rel.csv', 'w'))

posts.writerow(['postId:ID(Post)', 'title', 'body'])
posts_rel.writerow([':START_ID(Post)', ':END_ID(Post)'])

users.writerow(['userId:ID(User)', 'name'])
users_posts_rel.writerow([':START_ID(User)', ':END_ID(Post)'])

tags.writerow(['tagId:ID(Tag)'])
tags_posts_rel.writerow([':START_ID(Post)', ':END_ID(Tag)'])

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            el = replace_keys(el)
            posts.writerow([
                el['id'],
                clean(el.get('title','')),
                clean(el.get('body',''))
            ])
            if el.get('parentid'):
                posts_rel.writerow([el['parentid'],el['id']])
            if el.get('owneruserid'):
                users_posts_rel.writerow([el['owneruserid'],el['id']])
            if el.get('tags'):
                eltags = [x.replace('<','') for x in el.get('tags').split('>')]
                for tag in [x for x in eltags if x]:
                    tags_posts_rel.writerow([el['id'],tag])
    except Exception as e:
        print('x',e)
    if i % 5000 == 0:
        print('.',end='')
    if i > 10000: #only a small sample
        break

print(i,'posts ok')

file = join(PATH,'Users.xml')

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            el = replace_keys(el)
            users.writerow([
                el['id'],
                clean(el.get('displayname','')),
            ])
    except Exception as e:
        print('x',e)
    if i % 5000 == 0:
        print('.',end='')
    if i > 1000: #only a small sample
        break

print(i,'users ok')

file = join(PATH,'Tags.xml')

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            el = replace_keys(el)
            tags.writerow([
                el['tagname'],
            ])
    except Exception as e:
        print('x',e)
    if i % 5000 == 0:
        print('.',end='')
    if i > 1000: #only a small sample
        break

print(i,'tags ok')
