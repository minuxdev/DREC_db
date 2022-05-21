from variables import *
from db_query import connecting


conn = connecting(
    user=user, host=host, database=database
)

cur = conn.cursor()

tables = 'music', 'session', 'artist', 'comment'

for table in tables:
    statement = f'drop table if exists {table}'
    cur.execute(statement)
    print(f'{table.upper()} was deleted!')
    
conn.commit()

artist = '''create table artist(art_id int primary key auto_increment, 
                    artist_name varchar(200) not null unique, 
                    phone_nr int not null unique, 
                    email varchar(200)
                );'''


session = '''create table session(sess_id int primary key auto_increment, 
                    artist_name varchar(200) not null,
                    session_type varchar(200) not null default "Record",
                    session_date datetime unique not null, 
                    status varchar(15) default "Pendente", artist_id int, 
                    foreign key(artist_id) references artist(art_id)
                );'''


music = '''create table music(music_id int primary key auto_increment, 
                    artist_name varchar(200) not null,
                    file_name varchar(200) unique,
                    release_date date unique, artist_id int not null, 
                    sess_id int unique not null,
                    download_link text unique,
                    foreign key(artist_id) references artist(art_id),
                    foreign key(sess_id) references session(sess_id)
                );'''

comment = '''create table comment(com_id int primary key auto_increment,
            author varchar(100) not null, author_email varchar(45) not null,
            message text not null unique, 
            com_date datetime not null unique
            )'''

# conn.commit_changes(artist)
# conn.commit_changes(session)
# conn.commit_changes(music)

tables = artist, session, music, comment

for table in tables:
    cur.execute(table)

conn.commit()

statement = 'show tables'
cur.execute(statement)
tables = cur.fetchall()

print('')
for table in tables:
    print(table)