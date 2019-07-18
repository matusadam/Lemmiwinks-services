
from tinydb import TinyDB

if __name__ == "__main__":
	# new file
	open('login_access', 'w').close()
	db = TinyDB('login_access')

	db.insert({'id' : 1, 'username' : 'admin', 'password' : 'admin'})