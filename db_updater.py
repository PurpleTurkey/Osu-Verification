import os, sys
from tinydb import TinyDB, Query

db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'database.json'))
db_users = table = db.table('users', cache_size=0)

#db_users.update({'auto_server': None })