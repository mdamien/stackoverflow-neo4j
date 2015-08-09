import xmltodict, json, sys, os
from os.path import join

from py2neo import Graph, Node, Relationship, watch


graph = Graph("http://neo4j:n@localhost:7474/db/data/")

def commit(*data, total=None, progress=0):
	if not total:
		total = len(data)
	L = len(data)
	print('     ', progress,'/',total,'... +',L)
	try:
		if L > 1000:
			raise Exception('split it')
		graph.create(*data)
		print('        -> success!')
	except Exception as e:
		print('     ',e)
		split = L//2
		commit(*data[:split], total=total, progress=progress)
		commit(*data[split:], total=total, progress=progress+split)

SPECIFIC_DIR = sys.argv[1].replace('extracted/','') if len(sys.argv) > 1 else None

def delall():
	print('delete previous data')
	remove_all = """
	MATCH (n)
	OPTIONAL MATCH (n)-[r]-()
	DELETE n,r
	"""
	graph.cypher.execute(remove_all)
delall()

done = {}

with open('done') as f:
	done = {x.strip() for x in f.readlines() if len(x.strip()) > 0}

print('done:',' - '.join(done))

DIRS = [SPECIFIC_DIR] if SPECIFIC_DIR else os.listdir('extracted/')

for DIR in DIRS:
	print(DIR)
	DIR2 = 'extracted/'+DIR

	if DIR in done and DIR != SPECIFIC_DIR:
		continue

	ALL = {}

	with open(join(DIR2,'Posts.xml')) as fd:
	    ALL = xmltodict.parse(fd.read())

	print("STATS", len(ALL['posts']['row']),'posts') 

	with open(join(DIR2,'Tags.xml')) as fd:
	    ALL.update(xmltodict.parse(fd.read()))

	print("STATS", len(ALL['tags']['row']),'tags') 

	with open(join(DIR2,'Users.xml')) as fd:
	    ALL.update(xmltodict.parse(fd.read()))

	print("STATS", len(ALL['users']['row']),'users') 

	"""
	with open(join(DIR2,'Comments.xml')) as fd:
	    ALL.update(xmltodict.parse(fd.read()))

	print("STATS", len(ALL['comments']['row']),'comments') 
	"""

	NEW_ALL = {}
	for bigkey,els in ALL.items():
		new_els = []
		for el in els['row']:
			new = {}
			for key,val in el.items():
				new[key.lower().replace('@','')] = val
			new_els.append(new)
		NEW_ALL[bigkey] = new_els
	out = DIR.replace('/','') \
			.replace('stackexchange.com','')
	out += '.json'


	with open(join('out',out),'w') as f:
		json.dump(NEW_ALL,f,indent=2)

	data = NEW_ALL
	user_nodes = {}
	tags_nodes = {}
	posts_nodes = {}


	print(len(data['users']),'users')
	for user in data['users']:
		user['community'] = DIR
		node = Node("User", **user)
		user_nodes[user['id']] = node

	commit(*user_nodes.values())

	print(len(data['tags']),'tags')
	for tag in data['tags']:
		tag['community'] = DIR
		node = Node("Tag", **tag)
		tags_nodes[tag['tagname']] = node

	commit(*tags_nodes.values())

	rels = []
	children = []

	print(len(data['posts']),'posts')
	for post in data['posts']:
		post['community'] = DIR
		post['body'] = ''
		node = Node("Post", **post)
		if 'owneruserid' in post:
			user_id = post['owneruserid']
			if user_id in user_nodes:
				link = Relationship(user_nodes[user_id], "POSTED", node)
				rels.append(link)
		if 'parentid' in post:
			children.append((node,post))
		if 'tags' in post:
			tags = [x.replace('<','') for x in post['tags'].split('>')]
			tags = [x for x in tags if x]
			for tag in tags:
				if tag in tags_nodes:
					link = Relationship(tags_nodes[tag], "HAS_TAG", node)
					rels.append(link)
		posts_nodes[post['id']] = node
	commit(*posts_nodes.values())
	commit(*rels)

	rels = []
	print(len(children),'posts children')
	for node, post in children:
		parentid = post['parentid']
		if parentid in posts_nodes:
			link = Relationship(posts_nodes[parentid], "HAS_ANSWER", node)
			rels.append(link)
	commit(*rels)

	rels = []

	done.add(DIR)
	with open('done','w') as f:
		f.write('\n'.join(sorted(list(done))))
