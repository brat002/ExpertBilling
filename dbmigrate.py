#!/usr/bin/env python

from optparse import OptionParser

import logging
import datetime
import time
import re
import os

logger = logging.getLogger("dbmigrate")
SCRIPT_ROOT = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))
SCHEMAS_PATH = os.environ.get('SCHEMAS_PATH', os.path.join(SCRIPT_ROOT, '../dbschema'))
MIGRATION_FILENAME = re.compile(r'^[0-9]{4}_[0-9a-zA-Z_.]*'
                                r'(\.sql)?$')


class Migrations:
    def __init__(self, tl):
        self.tl = tl

    def keys(self):
        return [x for x, y in self.tl]

    def items(self):
        return [(x, y) for x, y in self.tl]

    def __iter__(self):
        return iter(self.tl)

    def __getitem__(self, key):
        try:
            return [y for x, y in self.tl if x == key][0]
        except IndexError:
            return None


class Db:
    _driver = None

    def __init__(self, **options):
        logger.debug("Backend conf=%s" % options)
        self.options = options

    def _connect(self, host, port, database, username, password):
        raise NotImplemented

    def init(self):
        raise NotImplemented

    def fetch_one(self, query):
        return self.execute(query).fetchone()

    def execute(self, query):
        return self.execute_many((query,))

    def execute_many(self, sqls):
        self._connect(**self.options)

        cursor = self._driver.cursor()

        try:
            for query in sqls:
                logger.debug(query)
                cursor.execute(query)

            self._driver.commit()

            return cursor
        except Exception as e:
            self._driver.rollback()
            cursor.close()
            logger.exception(e)
            raise


class PgSql(Db):
    adapter = 'psycopg2'
    defaults = {
        'host': 'localhost',
        'port': 5432
    }

    def __init__(self, host, port, database, username, password):
        host = self.defaults['host'] if host is None else host
        port = self.defaults['port'] if port is None else port
        Db.__init__(self, host=host, port=port, database=database,
                    username=username, password=password)

    def init(self):
        self.execute("""
        CREATE TABLE IF NOT EXISTS _db_migrationhistory (
        id serial,
        migration varchar(255) NOT NULL,
        created_at timestamp NOT NULL,
        PRIMARY KEY ("id"));
        """)

    def execute(self, query):
        return self.execute_many((query,))

    def execute_many(self, sqls):
        self._connect(**self.options)

        cursor = self._driver.cursor()

        try:
            for query in sqls:
                logger.debug(query)
                cursor.execute(query)

            self._driver.commit()

            return cursor
        except Exception as e:
            self._driver.rollback()
            cursor.close()
            logger.exception(e)
            raise

    def _connect(self, host, port, database, username, password):
        if not self._driver is None:
            return

        if self.adapter == 'psycopg2':
            import psycopg2
            self._driver = psycopg2.connect(host=host, port=port, database=database,
                                           user=username, password=password)
        else:
            # TODO
            raise NotImplemented


class MigrationManager(object):

    BACKENDS = {
        'postgresql': PgSql
    }

    def __init__(self, options):
        if not os.path.exists(options.path):
            raise EnvironmentError("Schemas path `%s` doesn't exists" % options.path)

        conf = {
            'host': options.host,
            'port': options.port,
            'database': options.database,
            'username': options.username,
            'password': options.password
        }

        try:
            self.connector = self.BACKENDS[options.backend](**conf)
        except KeyError:
            raise Exception("Backend `%s` is not supported yet!" % options.backend)

        self.options = options

    def init(self):
        """
        Migrations script initial logic
        """

        self.connector.init()

    def migrate(self, migration_num=None, fake=False):
        cur_num = self._current_migration_num
        migrations = self._get_migrations_list()
        if not migrations.keys():
            print "No migrations found"
            return
        max_num = max(migrations.keys())
        if migration_num is None:
            migration_num = max_num

        print "Current migration %s. Migrate to %s." % (cur_num, migration_num)

        if migration_num > max_num:
            print "Migration number too high. Last migration %s." % max_num
            return

        if migration_num > cur_num:
            self._migrate_forward(cur_num, migration_num, migrations, fake)
        elif migration_num < cur_num:
            self._migrate_backward(cur_num, migration_num, migrations, fake)
        else:
            print "Nothing to migrate."

    def _migrate_forward(self, cur_num, to_num, migrations, fake):
        for num, filename in migrations.items():
            # print cur_num, num, to_num, cur_num < num, num <= to_num, cur_num < num <= to_num
            if cur_num < num <= to_num:
                time.sleep(1)  # sleep to be sure not same time

                if not fake:
                    self._apply_migration(filename)

                now = datetime.datetime.now()
                self.connector.execute("""
                INSERT INTO _db_migrationhistory (migration, created_at)
                VALUES(%s, '%s');""" % (num, now.strftime('%Y-%m-%d %H:%M:%S')))

    def _migrate_backward(self, cur_num, to_num, migrations, fake):
        for num, filename in reversed(migrations.items()):
            # print cur_num, num, to_num, cur_num >= num >= to_num
            if cur_num >= num >= to_num:
                time.sleep(1)  # sleep to be sure not same time

                if not fake:
                    self._apply_migration(filename, False)

                now = datetime.datetime.now()
                self.connector.execute("""
                INSERT INTO _db_migrationhistory (migration, created_at)
                VALUES(%s, '%s');""" % (num - 1, now.strftime('%Y-%m-%d %H:%M:%S')))

                # self.connector.execute("""
                # DELETE FROM _db_migrationhistory WHERE migration = %s LIMIT 1;""" % num)

    @property
    def _current_migration_num(self):
        """
        Returns last applied migration from database
        """

        sql = """SELECT migration FROM _db_migrationhistory ORDER BY created_at DESC LIMIT 1"""
        result = self.connector.fetch_one(sql)
        num = -1
        if result:
            num = int(float(result[0]))
        logger.debug("Current migration: %s." % num)
        return int(num)

    def _get_migrations_list(self):
        path = self.options.path
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        migrations = []
        for f in files:
            if MIGRATION_FILENAME.match(os.path.basename(f)):
                migrations.append((int(float(f[:4])), f))

        logger.debug('Migrations found: %s' % migrations)
        return Migrations(sorted(migrations, key=lambda m: m[0]))

    def _print_migrations_list(self):
        cur_num = self._current_migration_num
        migrations = self._get_migrations_list()
        logger.debug("Try to print")
        for num in migrations.keys():
            print "(*)" if cur_num >= num else "( )", migrations[num]
        logger.debug("HERE")

    def _parse_sql_file(self, filename, forward):
        lines = []
        with open(os.path.join(self.options.path, filename)) as f:
            right_section = False
            has_section = 0
            for line in f.readlines():
                line = line.strip()
                if line.startswith("--@ forward"):
                    right_section = forward
                    has_section += 1
                    continue
                elif line.startswith("--@ backward"):
                    right_section = not forward
                    has_section += 1
                    continue
                else:
                    if right_section:
                        lines.append(line)

            if not has_section == 2:
                raise Exception("Migration doesn't has required section")

        sqls = []
        sql_part = ''
        found_comment = False
        found_create = False
        for sql_str in lines:
            sql_str = sql_str.strip()
            if sql_str.startswith('--'): continue
            if sql_str.startswith('/*'):
                found_comment = True
            if sql_str.endswith('*/'):
                found_comment = False
                continue
            if found_comment: continue
            if not sql_str:
                continue

            sqls.append(sql_str)


        return sqls

    def _apply_migration(self, filename, forward=True):
        print "Applying migration `%s`." % filename
        sqls = self._parse_sql_file(filename, forward)
        self.connector.execute('\n'.join(sqls))
        print "Done."


if __name__ == "__main__":
    usage = """ %prog [options] init
        %prog [options] list
        %prog [options] migrate to_migration_num
        %prog [options] migrate -1
        %prog [options] fake to_migration_num
        %prog [options] fake -1
        %prog [options] help"""

    parser = OptionParser(usage=usage)

    # Options

    parser.set_conflict_handler('resolve')  # enable -h option for host instead 'help'

    parser.add_option("-b", "--backend", dest="backend", default=None, help="Backend name, i.e. postgresql etc")

    parser.add_option("-h", "--host", dest="host", default=None, help="Host name")
    parser.add_option("-p", "--port", dest="port", default=None, type=int, help="Port")
    parser.add_option("-d", "--database", dest="database", default=None, help="Database name")

    parser.add_option("-u", "--username", dest="username", default='', help="Username")
    parser.add_option("-w", "--password", dest="password", default=None, help="Password")

    parser.add_option("-s", "--schemas-path", dest="path", default=SCHEMAS_PATH, help="Schemas path")

    parser.add_option("-1", "--revert-all", dest="revert_all", action="store_true", default=False,
                      help="Revert all migrations")

    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Enable verbose mode")

    opts, args = parser.parse_args()

    if 'help' in args:
        if len(args) > 1:
            parser.error("Help doesn't accept any argument.")

        parser.print_help()
        exit(0)

    if not opts.backend:
        parser.error('Backend required')
    if not opts.database:
        parser.error('Database required')
    if not opts.username:
        parser.error('Username required')

    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.ERROR)

    logger.debug("Migrations path: `%s`." % opts.path)
    logger.debug("Script opts=%s args=%s" % (opts, args))

    manager = MigrationManager(opts)

    # Commands

    if len(args) < 1:
        parser.error("Command required.")

    if 'init' in args:
        if len(args) > 1:
            parser.error("Init doesn't accept any argument.")

        manager.init()
    elif 'list' in args:
        if len(args) > 1:
            parser.error("List doesn't accept any argument.")

        manager._print_migrations_list()
    elif 'migrate' in args:
        if len(args) == 2:
            manager.migrate(migration_num=int(float(args[1])))
        elif len(args) == 1:
            if opts.revert_all:
                manager.migrate(-1)
            else:
                manager.migrate()
        else:
            parser.error("Too mach arguments for migrate command.")
    elif 'fake' in args:
        if len(args) == 2:
            manager.migrate(migration_num=int(float(args[1])), fake=True)
        elif len(args) == 1:
            if opts.revert_all:
                manager.migrate(migration_num=-1, fake=True)
            else:
                manager.migrate(fake=True)
        else:
            parser.error("Too mach arguments for migrate command.")

