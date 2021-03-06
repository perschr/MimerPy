# The database to run the tests on. Having it empty means that the
# environment variable MIMER_DATABASE controls the database to connect to.
DBNAME = ''

# The test connects to SYSADM_USR and creates a subident that is used for all
# the tests. After testing, the subident is dropped and everything goes away.
SYSADM_USR = 'SYSADM'
SYSADM_PWD = 'SYSADM'


#################################################################
## Stuff below defines routines for all tests.
## Do not change for configuration purposes
#################################################################

import mimerpy
import os
import getpass

# Connection arguments for SYSADM
SYSUSR = dict(dsn      = DBNAME,
              user     = SYSADM_USR,
              password = SYSADM_PWD)

# Connection arguments for test user
TSTUSR = dict(dsn      = DBNAME,
              user     = 'MIMERPY',
              password = 'PySecret')

OSUSER = getpass.getuser()
KEEP_MIMERPY_IDENT = os.environ.get('MIMER_KEEP_MIMERPY_IDENT', 'false') == 'true'
MIMERPY_STABLE = os.environ.get('MIMERPY_STABLE', 'True')

def setup():
    syscon = mimerpy.connect(**SYSUSR)
    with syscon.cursor() as c:
        try:
            c.execute("DROP IDENT MIMERPY CASCADE")
        except mimerpy.DatabaseError as de:
            if de.message[0] != -12517:
                pass
            else:
                pass

        c.execute("CREATE IDENT MIMERPY AS USER USING 'PySecret'")
        c.execute("GRANT DATABANK,IDENT TO MIMERPY")
    syscon.commit()
    tstcon = mimerpy.connect(**TSTUSR)
    with tstcon.cursor() as c:
        c.execute("CREATE DATABANK PYBANK")
        c.execute("CREATE IDENT %s AS USER" % OSUSER)
        c.execute("ALTER IDENT %s ADD OS_USER '%s'" % (OSUSER, OSUSER))
    tstcon.commit()
    return (syscon, tstcon)

def teardown(tstcon, syscon):
        tstcon.close()
        if not KEEP_MIMERPY_IDENT:
            with syscon.cursor() as c:
                c.execute("DROP IDENT MIMERPY CASCADE")
            syscon.commit()
        syscon.close()