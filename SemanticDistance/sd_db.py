
import MySQLdb, sys

class SemanticDistanceDB:

	def __init__ (self, sd, table, **mysql_args):

		# Connection to the database
		try:
			self.__connection = MySQLdb.connect(**mysql_args)
			self.__cursor = self.__connection.cursor()

		except MySQLdb.Error, msg:
			code, msg = msg.args[:2]
			raise Exception("Unable to connect to the database: %s (code %s, arguments was %s)" % (msg, code, mysql_args))

		self.__table = table

		self.__sd = sd
		self.__sd.distance_between_ = self.__sd.distance_between
		self.__sd.distance_between = self.distance_between

	def flush_table (self):
		table_structure = (
		  "termA VARCHAR(255) NOT NULL",
		  "termB VARCHAR(255) NOT NULL",
		  "distance FLOAT NOT NULL",
		  "PRIMARY KEY (termA, termB)",
		 )

		self.__cursor.execute("DROP TABLE IF EXISTS %s" % self.__table)
		self.__cursor.execute("CREATE TABLE %s (%s)" % (self.__table, ','.join(table_structure)))

	# Construct a database from the terms and distances
	# encoded in a SemanticDistance instance. A custom
	# list of terms can be provided (warning: ensure that
	# this list contains no duplicates and that all terms
	# have an information content)
	def process (self, terms = None, append = False, buffer_limit = 5000, verbose = True):

		# Check if the table already exists
		self.__cursor.execute("SHOW TABLES")
		table_exists = False

		for table in self.__cursor.fetchall():
			if (table[0] == self.__table):
				table_exists = True

		# Create a new one if it doesn't or if we want to overwrite
		if (not append) or (not table_exists):
			self.flush_table()

		# Creation of the distance matrix
		if (terms == None):
			terms = self.__sd._SemanticDistance__IC.keys()

		insertion_statement = "INSERT INTO %s VALUES (%%s, %%s, %%s)" % self.__table
		insertion_buffer = []

		def flush_buffer():
			self.__cursor.executemany(insertion_statement, insertion_buffer)

		terms.sort()
		for i, A in enumerate(terms):
			for B in terms[i+1:]:
				d = self.__sd.distance_between_(A, B, verbose)
				if (d < 0):
					return d

				insertion_buffer.append((A, B, d))

				if (len(insertion_buffer) > buffer_limit):
					flush_buffer()
					insertion_buffer = []

		if (len(insertion_buffer) > 0):
			flush_buffer()
			insertion_buffer = []

	def distance_between (self, A, B, verbose = True, check_ic = True):

		print "MySQL version"

		if (check_ic):
			for term in (A, B):
				if (not term in self.__sd._SemanticDistance__ic):
					if verbose:
						print >>sys.stderr, "distance_between(): no information content for term '%s'" % A

					return self.__sd.NO_INFORMATION_CONTENT

		if (A == B):
			return 0.0

		select_statement = "SELECT distance FROM %s WHERE (termA = '%%s' and termB = '%%s')" % self.__table

		try:
			self.__cursor.execute(select_statement % order(A, B))
			return self.__cursor.fetchone()

		except MySQLdb.Error, msg:
			code, msg = msg.args[:2]

			if (code == 1002):
				if (verbose):
					print >>sys.stderr, "distance_between(): terms '%s' and '%s' share no parents" % (A, B)

				return NO_SHARED_PARENTS
			else:
				raise Exception("Error while connecting to the database: %s (code %s)" % (msg, code))
