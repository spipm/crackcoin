import crackcoin.wallets
import crackcoin.transactions
import sqlite3
import threading


CRACKCOIN_DB_TEMPLATE = 'crackcoinBase.sql'
CRACKCOIN_DB_FILE = 'crackcoin.db'


class crackDB(object):
	""" crackcoin database class """

	def __init__(self, dbFile = CRACKCOIN_DB_FILE):
		
		self.dbFile = dbFile
		self.dblock = threading.Lock()

	def doQuery(self, query, args=False, result='all'):
		''' Perform a thread-safe query on the database '''

		self.dblock.acquire()

		self.conn = sqlite3.connect(self.dbFile)
		self.cursor = self.conn.cursor()

		if args:
			self.cursor.execute(query, args)
		else:
			self.cursor.execute(query)

		res = ''
		if result == 'all':
			res = crackcoin.db.cursor.fetchall()
		if result == 'one':
			res = crackcoin.db.cursor.fetchone()

		self.conn.commit()
		self.conn.close()

		self.dblock.release()

		return res


	def createDB(self):
		''' Create database from template and create wallet '''

		# maak db met genesis transaction en wallet
		sql = open(CRACKCOIN_DB_TEMPLATE,'r').read() 
		tmpConn = sqlite3.connect(self.dbFile)
		tmpCursor = tmpConn.cursor()
		tmpCursor.executescript(sql)
		tmpConn.commit()
		tmpConn.close()

		crackcoin.wallets.createNewWallet()