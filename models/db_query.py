from mysql.connector import connect


def connecting(user, host, database=None, passwd=None):
    conn = connect(user=user, host=host, database=database)
    cursor = conn.cursor()
    
    if not database == None:
        cursor.execute(f'USE {database}')
        
    conn.commit()
    cursor.close()
    
    return conn



def commit_changes(conn, statement=None):
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute(statement)
        conn.commit()
        print('Changes commited successfully...')
        cursor.close()
        
    except Exception as e:
        print(e)



class DB_Connection:

    def __init__(self, connector, cursor):
        self.__conn__ = connector
        self.cursor = cursor
    
    def commit_changes(self, statement=None):
        try:
            self.cursor.execute(statement)
            self.__conn__.commit()
            print(f'Changes commited successfully...\n{statement}')
            self.cursor.close()
            # self.__conn__.close()
        except Exception as e:
            print(e)


class Create_Objects(DB_Connection):

    def create_db(self, data_base):

        statement = 'CREATE DATABASE IF NOT EXISTS %s' %data_base
        self.commit_changes(statement)
    
    
    def create_table(self, table_name, statement):

        statement = f'CREATE TABLE {table_name}({statement})'
        self.commit_changes(statement)
    
    
    def create_user(self, user_name, privileges=None):

        statement = f'CREATE USER IF NOT EXISTS {user_name}@{host}'
        self.commit_changes(statement)
        if privileges:
            statement = f'GRANT {privileges} ON *.* TO {user_name}@{host}'
            self.commit_changes(statement)
            statement = 'FLUSH PRIVILEGES'
            self.commit_changes(statement)


class Insert_Data:
    def __init__(self, conn) -> None:
        self.conn = conn

    def insert_data(self, table, **kwargs):

        keys = []
        values = []
        
        for key, value in kwargs.items():
            keys.append(str(key))
            values.append(str(value))
        
        attribute = ','.join(keys)
        attribute_values = tuple([value for value in values])        
        
        statement = f'''INSERT INTO {table}({attribute})
                    VALUES{attribute_values}'''
                    
        commit_changes(self.conn, statement)

        
    def update_entries(self, table, **kwargs):
        keys = []
        values = []
        
        for key, value in kwargs.items():
            keys.append(str(key))
            values.append(str(value))
            
        statement = 'SELECT sess_id FROM session'
        cursor = self.conn.cursor()
        cursor.execute(statement)
        
        session_id = cursor.fetchall()

        for i in range(len(session_id)):
            if int(values[0]) == int(session_id[i][0]):
                sess_id = session_id[i][0]
                
                print('Print IDs: ', values[0], sess_id)
            
                statement = f'''UPDATE {table} 
                SET {keys[1]}="{values[1]}",
                    {keys[2]}="{values[2]}",
                    {keys[3]}="{values[3]}"
                WHERE {keys[0]}={sess_id}'''
                    
                print(f'Print statement: ---> {statement}')    
                cursor.execute(statement)
                self.conn.commit()
                print('Commited.....')
                break
        
        
class Read_Data(DB_Connection):
    def show_tables(self):
        db_entities = []
        statement = f'SHOW TABLES FROM {self.database}'
        self.cursor.execute(statement)
        tables = self.cursor.fetchall()

        if tables:
            for table in tables:
                db_entities.append(table[0])

        return db_entities


    def show_columns(self, table):
        table_attributes = []

        statement = f'SHOW COLUMNS FROM {table}'
        self.cursor.execute(statement)
        attributes = self.cursor2.fetchall()

        for attribute in attributes:
            table_attributes.append(attribute[:2])
        return table_attributes
    

    def read_data_from_single_table(self, table, clausule='*',
                                    size=None, **kwargs):
        entities_collection = []

        statement = f'SELECT {clausule} FROM {table}'

        if kwargs:
            for attribute, value in kwargs.items():
                attribute = attribute
                value = value
                statement = f'''SELECT {clausule} FROM {table}
                                WHERE {attribute}="{value}"'''

        self.cursor.execute(statement)
        entities = self.cursor.fetchall()
        
        
        if entities:
            
            if size and len(entities) >= size:
                entities = self.cursor.fetchmany(2)
                print(entities, 'size: ', size)    
            for entity in entities:
                entities_collection.append(entity)
        
        return entities_collection


    def read_data_in_join_mode(self, table1, table2, artist=None, size=None):

        sess_id = 'sess_id'
        artist_id = 'artist_id'
        artist_name = 'artist_name'
        phone_nr =  'phone_nr'
        session_type = 'session_type'
        session_date = 'session_date'
        satus = 'status'

        if artist:
            statement = f'''SELECT 
                            {table1}.sess_id,
                            {table1}.artist_name,
                            {table2}.phone_nr,
                            {table1}.session_type,
                            {table1}.session_date,
                            {table1}.status FROM {table1} 
                            INNER JOIN {table2}
                            ON {table1}.artist_name="{artist}"
                            WHERE {table1}.artist_id={table2}.art_id
                        '''
        else:
            statement = f'''SELECT 
                        {table1}.{sess_id},
                        {table1}.{artist_name}, 
                        {table2}.{phone_nr},
                        {table1}.{session_type},
                        {table1}.{session_date},
                        {table1}.{satus} FROM {table1} 
                        INNER JOIN {table2}
                    '''

        self.cursor.execute(statement)
        result = self.cursor.fetchall()

        if result:
            if size and len(result) >= size:
                result = self.cursor.fetchmany(size)  
        return result


class Delete_Object(DB_Connection):
    def drop_table(self, table):
        statement = f'DROP TABLE {table}'
        self.commit_changes()
    
    
    def delete_entries(self, table, **kwargs):
        if clausule:
            for key, value in kwargs.items():
                key = key
                value = value
            statement = f'DELETE FROM {table} WHERE {key}="{value}"'
        else:
            statement = f'DELETE FROM {table}'
        self.commit_changes(statement)
    
    
    def remove_user(self, user_name, host=None):
        if host:
            statement = f'DROP USER {user_name}@{host}'
        else:
            statement = f'DROP USER {user_name}'
        self.commit_changes()


def get_artist_entity(instance_object, artist_name):
        return instance_object.read_data_from_single_table('artist',
                'artist_name, art_id', artist_name=artist_name)


if __name__ == '__main__':
    
    user='minux'
    host='localhost'
    db='mydb'
    clausule = 'name="Ern"'
    conn = connecting(user=user, host=host, database=db)
    
    # conn = DB_Connection(user='drec', host='localhost')
    # create = Create_Objects()
    # create.create_db(db)
    # create.create_table('client', 'id int primary key auto_increment, \
    #                     name varchar(50) not null, address varchar(50)')
    
    # create.create_table('product', 'id int primary key auto_increment, \
    #                     name varchar(50) not null, client_id int, \
    #                     foreign key(client_id) references client(id)')

