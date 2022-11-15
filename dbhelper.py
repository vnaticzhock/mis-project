import psycopg2


class dbhelper:
    def __init__(self):
        self.host = 'localhost'
        self.dbname = 'mis'
        self.user = 'user'
        self.password = '1234'
        self.sslmode = 'allow'

        config_str = 'host={0} user={1} dbname={2} password={3} sslmode={4}'\
            .format(self.host, self.user, self.dbname, self.password, self.sslmode)
        self.conn = psycopg2.connect(config_str)
        self.conn.autocommit = True

        self.cursor = self.conn.cursor()
