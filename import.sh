rm -rf ../neo/data/graph.db
../neo/bin/neo4j-import \
--into ../neo/data/graph.db \
--id-type string \
--nodes:Post csvs/posts.csv \
--nodes:User csvs/users.csv \
--nodes:Tag csvs/tags.csv \
--relationships:PARENT_OF csvs/posts_rel.csv \
--relationships:HAS_TAG csvs/tags_posts_rel.csv \
--relationships:POSTED csvs/users_posts_rel.csv
../neo/bin/neo4j restart