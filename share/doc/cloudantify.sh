# find and replace all mention of CouchDB with Cloudant. 

find src -type f -print0 | xargs -0 sed -i '' 's/Apache CouchDB(TM)/Cloudant/g'
find src -type f -print0 | xargs -0 sed -i '' 's/couchdb.apache.org/cloudant.com/g'
find src -type f -print0 | xargs -0 sed -i '' 's/CouchDB/Cloudant/g'
find src -type f -print0 | xargs -0 sed -i '' 's/couchdb:5984/USERNAME.cloudant.com/g'
find src -type f -print0 | xargs -0 sed -i '' 's/couchdb-remote:5984/USERNAME.cloudant.com/g'

grep -r couchdb src