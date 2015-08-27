import json, sys, os, xmltodict, csv
from os.path import join
from utils import *
import shutil

PATH = sys.argv[1]
DIR = PATH.replace('extracted/','')

print("importing",DIR)

file = join(PATH,'Posts.xml')

def clean(x):
    #neo4j-import doesn't support: multiline (coming soon), quotes next to each other and escape quotes with '\""'
    return x.replace('\n','').replace('\r','').replace('\\','').replace('"','')

def open_csv(name):
    return csv.writer(open('csvs/{}.csv'.format(name), 'w'), doublequote=False, escapechar='\\')

try:
    shutil.rmtree('csvs/')
except:
    pass
os.mkdir('csvs')

posts = open_csv('posts')
posts_rel = open_csv('posts_rel')
users = open_csv('users')
users_posts_rel = open_csv('users_posts_rel')
tags = open_csv('tags')
tags_posts_rel = open_csv('tags_posts_rel')

posts.writerow(['postId:ID(Post)', 'title', 'body','score','views','comments'])
posts_rel.writerow([':START_ID(Post)', ':END_ID(Post)'])

users_things = ['displayname', 'reputation', 'aboutme', \
    'websiteurl', 'location', 'profileimageurl', 'views', 'upvotes', 'downvotes']
users.writerow(['userId:ID(User)'] + users_things)
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
                clean(el.get('body',''))[:100],
                clean(el.get('score','')),
                clean(el.get('viewcount','')),
                clean(el.get('commentcount','')),
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
    if i and i % 5000 == 0:
        print('.',end='')
    if i and i % 1000000 == 0:
        print(i)

print(i,'posts ok')

file = join(PATH,'Users.xml')

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            el = replace_keys(el)
            row = [el['id'],]
            for k in users_things:
                row.append(clean(el.get(k,'')[:100]))
            users.writerow(row)
    except Exception as e:
        print('x',e)
    if i % 5000 == 0:
        print('.',end='')

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

print(i,'tags ok')
