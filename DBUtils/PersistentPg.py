"""PersistentPg - persistent classic PyGreSQL connections.

Implements steady, thread-affine persistent connections to a PostgreSQL
database using the classic (not DB-API 2 compliant) PyGreSQL API.

This should result in a speedup for persistent applications such as the
application server of "Webware for Python," without loss of robustness.

Robustness is provided by using "hardened" SteadyPg connections.
Even if the underlying database is restarted and all connections
are lost, they will be automatically and transparently reopened.

Measures are taken to make the database connections thread-affine.
This means the same thread always uses the same cached connection,
and no other thread will use it. So the fact that the classic PyGreSQL
pg module is not thread-safe at the connection level is no problem here.

For best performance, the application server should keep threads persistent.
For this, you have to set MinServerThreads = MaxServerThreads in Webware.

For more information on PostgreSQL, see:
	http://www.postgresql.org
For more information on PyGreSQL, see:
	http://www.pygresql.org
For more information on Webware for Python, see:
	http://www.webwareforpython.org


Usage:

First you need to set up a generator for your kind of database connections
by creating an instance of PersistentPg, passing the following parameters:

	maxusage: the maximum number of reuses of a single connection
		(the default of 0 or False means unlimited reuse)
		When this maximum usage number of the connection is reached,
		the connection is automatically reset (closed and reopened).
	setsession: An optional list of SQL commands that may serve to
		prepare the session, e.g. ["set datestyle to german", ...]

	Additionally, you have to pass the parameters for the actual
	PostgreSQL connection which are passed via PyGreSQL,
	such as the names of the host, database, user, password etc.

For instance, if you want every connection to your local database 'mydb'
to be reused 1000 times:

	from DBUtils.PersistentPg import PersistentPg
	persist = PersistentPg(5, dbname='mydb')

Once you have set up the generator with these parameters, you can
request database connections of that kind:

	db = persist.connection()

You can use these connections just as if they were ordinary
classic PyGreSQL API connections. Actually what you get is the
hardened SteadyPg version of a classic PyGreSQL connection.

Closing a persistent connection with db.close() will be silently
ignored since it would be reopened at the next usage anyway and
contrary to the intent of having persistent connections. Instead,
the connection will be automatically closed when the thread dies.
You can change this behavior be setting persist._closeable to True.


Requirements:

Minimum requirement: Python 2.2 and PyGreSQL 3.4.
Recommended: Python 2.4.3 and PyGreSQL 3.8.


Ideas for improvement:

* Add thread for monitoring and restarting bad or expired connections
  (similar to DBConnectionPool/ResourcePool by Warren Smith).
* Optionally log usage, bad connections and exceeding of limits.


Copyright, credits and license:

* Contributed as supplement for Webware for Python and PyGreSQL
  by Christoph Zwerschke in September 2005
* Based on an idea presented on the Webware developer mailing list
  by Geoffrey Talvola in July 2005

Licensed under the Open Software License version 2.1.

"""

__version__ = '0.9.4'
__revision__ = "$Rev: 6696 $"
__date__ = "$Date: 2007-07-07 11:02:24 -0600 (Sat, 07 Jul 2007) $"


from DBUtils.SteadyPg import SteadyPgConnection


class PersistentPg:
	"""Generator for persistent classic PyGreSQL connections.

	After you have created the connection pool, you can use
	connection() to get thread-affine, steady PostgreSQL connections.

	"""

	def __init__(self, maxusage=0, setsession=None, *args, **kwargs):
		"""Set up the persistent PostgreSQL connection generator.

		maxusage: maximum number of reuses of a single connection
			(0 or False means unlimited reuse)
			When this maximum usage number of the connection is reached,
			the connection is automatically reset (closed and reopened).
		setsession: optional list of SQL commands that may serve to prepare
			the session, e.g. ["set datestyle to ...", "set time zone ..."]
		args, kwargs: the parameters that shall be used to establish
			the PostgreSQL connections using class PyGreSQL pg.DB()

		Set the _closeable attribute to True or 1 to allow closing
		connections. By default, this will be silently ignored.

		"""
		self._maxusage = maxusage
		self._setsession = setsession
		self._args, self._kwargs = args, kwargs
		self._closeable = 0
		self.thread = local()

	def steady_connection(self):
		"""Get a steady, non-persistent PyGreSQL connection."""
		return SteadyPgConnection(
			self._maxusage, self._setsession, *self._args, **self._kwargs)

	def connection(self):
		"""Get a steady, persistent PyGreSQL connection."""
		try:
			con = self.thread.connection
		except AttributeError:
			con = self.steady_connection()
			con._closeable = self._closeable
			self.thread.connection = con
		return con


try: # import a class for representing thread-local objects
	from threading import local
except ImportError: # for Python < 2.4, use the following simple implementation
	from threading import currentThread, enumerate, RLock
	class _localbase(object):
		__slots__ = '_local__key', '_local__args', '_local__lock'
		def __new__(cls, *args, **kwargs):
			self = object.__new__(cls)
			key = '_local__key', 'thread.local.' + str(id(self))
			object.__setattr__(self, '_local__key', key)
			object.__setattr__(self, '_local__args', (args, kwargs))
			object.__setattr__(self, '_local__lock', RLock())
			if args or kwargs and (cls.__init__ is object.__init__):
				raise TypeError("Initialization arguments are not supported")
			d = object.__getattribute__(self, '__dict__')
			currentThread().__dict__[key] = d
			return self
	def _patch(self):
		key = object.__getattribute__(self, '_local__key')
		d = currentThread().__dict__.get(key)
		if d is None:
			d = {}
			currentThread().__dict__[key] = d
			object.__setattr__(self, '__dict__', d)
			cls = type(self)
			if cls.__init__ is not object.__init__:
				args, kwargs = object.__getattribute__(self, '_local__args')
				cls.__init__(self, *args, **kwargs)
		else:
			object.__setattr__(self, '__dict__', d)
	class local(_localbase):
		def __getattribute__(self, name):
			lock = object.__getattribute__(self, '_local__lock')
			lock.acquire()
			try:
				_patch(self)
				return object.__getattribute__(self, name)
			finally:
				lock.release()
		def __setattr__(self, name, value):
			lock = object.__getattribute__(self, '_local__lock')
			lock.acquire()
			try:
				_patch(self)
				return object.__setattr__(self, name, value)
			finally:
				lock.release()
		def __delattr__(self, name):
			lock = object.__getattribute__(self, '_local__lock')
			lock.acquire()
			try:
				_patch(self)
				return object.__delattr__(self, name)
			finally:
				lock.release()
		def __del__():
			threading_enumerate = enumerate
			__getattribute__ = object.__getattribute__
			def __del__(self):
				try:
					key = __getattribute__(self, '_local__key')
					threads = list(threading_enumerate())
				except Exception:
					return
				for thread in threads:
					try:
						__dict__ = thread.__dict__
					except AttributeError:
						continue
					if key in __dict__:
						try:
							del __dict__[key]
						except KeyError:
							pass
			return __del__
		__del__ = __del__()
