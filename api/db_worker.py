"""
The module is responsible for the operation of databases: creating, 
indexing, checking for data, entering / changing data, sorting data ...
"""

import os
# import sqlite3
import psycopg2
# from _config import DB_URI, DATA_BASE       # for local app

ID = "ID_USER"
NUMBERS = "NUMBERS_POSTING_IMG"
KEYWORD = "KEYWORD"
KEYWORDS = "KEYWORDS" 
GROUP_CHANNEL = "GROUP_CHANNEL"
HISTORY_REQUESTS = "HISTORY_REQUESTS"
TIMESCRIPT = 'TIME_START_SCRIPT'
SITE = 'SITE'

DATA_BASE = psycopg2  # sqlite3 - SQlite  # for server app

DB_URI = os.environ.get('DB_URI')         # for server app

class DBworker:
    '''
        def create_db(self):\n\n
    The CREAT_DB function is responsible for creating the two databases USERS and HISTORY_REQUESTS.\n
    \n
        def setup_settings(self, id_user, numbers, keywords, group_channel, timescript):\n\n
    The SETUP_SETTINGS function is responsible for writing the user query setup data to the USERS database.\n
    \n
        def add_links_to_db(self, id, keyword, sitename, error_links):\n\n
    The ADD_LINK_TO_DB function is responsible for writing ID_USER, KEYWORD, SITENAME 
        data to the HISTORY_REQUESTS database, i.e. writes unique links to the database.\n

    Function returned two arguments: 'error_links' & 'added_links':\n
        error_links  - this variable is called before the function, with the value '0', to catch all unsaved references.\n
        added_links - this variable is called before the function, with the value '0', to catch all saved references.
    '''
    def create_db(self): 
        '''Create two database 'USERS' and 'HISTORY_REQUESTS'.'''
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
        try:
            cur.execute(f"""CREATE TABLE IF NOT EXISTS USERS 
                            (
                                {ID} VARCHAR ( 128 ) UNIQUE NOT NULL,
                                {NUMBERS} CHAR(3), 
                                {KEYWORDS} VARCHAR ( 256 ) NOT NULL, 
                                {GROUP_CHANNEL} VARCHAR ( 512 ) NOT NULL, 
                                {TIMESCRIPT} VARCHAR ( 58 ),
                                PRIMARY KEY({ID})
                            ) """)
            cur.execute(f"""CREATE TABLE IF NOT EXISTS {HISTORY_REQUESTS} 
                            (
                            {ID} VARCHAR ( 128 ) NOT NULL,
                            {KEYWORD} VARCHAR ( 256 ) NOT NULL,
                            {SITE} VARCHAR ( 512 ) NOT NULL
                            )""")
            

            print('USERS and HISTORY_REQUESTS databases created!')

        except:
            print('An error occurred while creating the databases.')

        conn.commit()
        cur.close()

    def create_index_db(self): 
        '''Create indexes for two database 'USERS' and 'HISTORY_REQUESTS'.'''
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
        try:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_id ON USERS (ID_USER)")
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_history_requests_id ON {HISTORY_REQUESTS} (ID_USER)")
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_history_requests_keyword ON {HISTORY_REQUESTS} (KEYWORD)")
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_history_requests_site ON {HISTORY_REQUESTS} (SITE)")
            print("Creating indexes for two databases 'USERS' and 'HISTORY_REQUESTS' DONE!")
        except TypeError as e:
            print('[Error]: ', e)

        conn.commit()
        cur.close()

    def sort_db_by_column(self, column_name):
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()

        if column_name == 'USERS':
            cur.execute(f"SELECT * FROM USERS ORDER BY {ID}")
            sorted_data = cur.fetchall()
            cur.execute("DELETE FROM USERS")
            for row in sorted_data:
                cur.execute("INSERT INTO USERS VALUES (%s,%s,%s,%s,%s)", row)
            print('СОРТИРОВКА ЗАВЕРШЕНА ПО USERS')

        elif column_name == 'HISTORY_REQUESTS':
            cur.execute(f"SELECT * FROM {HISTORY_REQUESTS} ORDER BY {ID}, {KEYWORD}, {SITE}")
            sorted_data = cur.fetchall()
            cur.execute(f"DELETE FROM {HISTORY_REQUESTS}")
            for row in sorted_data:
                cur.execute(f"INSERT INTO {HISTORY_REQUESTS} VALUES (%s,%s,%s)", row)
            print('СОРТИРОВКА ЗАВЕРШЕНА ПО HISTORY_REQUESTS')

        conn.commit()
        cur.close()

    def setup_settings(self, id_user, numbers, keywords, group_channel, timescript):  
        '''INSERT and UPDATE database DB 'USERS'.'''
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
        try:
            cur.execute(f"""INSERT INTO USERS VALUES (%s, %s, %s, %s, %s) """, (id_user, numbers, str(keywords), group_channel, timescript))
        except DATA_BASE.IntegrityError as e:
            conn.rollback()
            try:
                print(f"""[ATTANTION 1:2]: The user - '{id_user}' is in the database. His details will be updated.\n[ATTANTION 2:2]: """, e)
                cur.execute(f"""UPDATE USERS SET 
                                {NUMBERS} = %s, 
                                {KEYWORDS} = %s, 
                                {GROUP_CHANNEL} = %s, 
                                {TIMESCRIPT} = %s  
                                WHERE {ID} = %s::varchar""", 
                                (numbers, str(keywords), group_channel, timescript, id_user)
                                )
                print('[INFO] Update USER settings.')
            except DATA_BASE.errors.InFailedSqlTransaction as e :
                conn.rollback()
                print(f"[ERROR]: DATA_BASE: ", e)

        conn.commit()
        cur.close()

    def add_links_to_db(self, id_user, keyword, sitename, error_links, added_links):
        '''
        Add new link to DB 'HISTORY_REQUESTS'.
        But before that it checks if there is a link in the database given the user ID and keyword.

        Returns two variables: error_links, added_links.
        '''
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
 
        cur.execute(f"""SELECT * FROM {HISTORY_REQUESTS} WHERE {ID} = %s::varchar AND {KEYWORD} = %s::varchar AND {SITE} = %s::varchar""",
                    (id_user, keyword, sitename))
        existing_link = cur.fetchone()
        name_added_links = []

        try:
            cur.execute(f"""INSERT INTO {HISTORY_REQUESTS} VALUES (%s, %s, %s) """, (id_user, keyword, sitename))
            name_added_links.append(sitename)
            added_links += 1 
        except DATA_BASE.IntegrityError as e:
            print(f"""[ERROR] UNIQUE constraint failed. \n
                    This link - {sitename} is in DB. \n
                    Error - """, e)
            error_links += 1
        except ValueError or TypeError as e:
            print(f"""[ERROR] This link - {sitename}. \n
            Error - """, e)
            error_links += 1

        conn.commit()
        cur.close()
        print (error_links, ' - error_links, ', added_links, ' - added_links')
        return error_links, added_links, name_added_links
    
    def check_amount_links(self, id_user, keyword):
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
        cur.execute(f"""SELECT COUNT(*) FROM {HISTORY_REQUESTS} WHERE {ID} = %s::varchar and {KEYWORD} = %s::varchar""", (id_user, keyword))
        result = cur.fetchone()
        count = result[0] if result else 0
        conn.commit()
        cur.close()
        print(count, '- number of links found' )
        return count
    
    def check_settings_user(self, id_user):
        conn = DATA_BASE.connect(DB_URI)
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM USERS WHERE {ID} = %s::varchar""", (str(id_user),))
        result_settings_user = cur.fetchone()
        print(result_settings_user)
        cur.close()
        conn.close()
        return result_settings_user
    
    
if __name__ == '__main__':
    # DBworker.create_db(DBworker)
    # DBworker.check_amount_links(DBworker, 1, 'car 4k')
    # DBworker. add_links_to_db(DBworker, 1, 'parcer', "https://stackoverflow.com/questions/16573332/jsondecodeerror-expecting-value-line-1-lur-0", error_links = 0, added_links= 0 )
    DBworker.setup_settings(DBworker, 1, 3, ["car 4k", "girl 4k", "parcer", "888"], '@parcer', "11:22:33")
    # a = 1
    # d = DBworker.check_settings_user(DBworker, a)
    # # print(d)
    # if d != None:
    #     # g = tuple(d[0])
    #     print(type(d))
    #     a,b,c,e,f = d
    #     print(a)
    #     print(b)
    #     c = ast.literal_eval(c)
    #     print(c)
    #     print(e)
    #     print(f)
    # else:
    #     print ("Data is empty.")
