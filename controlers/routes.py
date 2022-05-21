from flask import request, render_template, redirect, url_for, flash
from models.db_query import (Read_Data, Insert_Data, 
                            Delete_Object, get_artist_entity, 
                            connecting)
from models.variables import *
from app import app
from time import strftime



messages = None

@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', messages=messages)


@app.route('/insert/<entities>')
def insert_data(entities):
    
    entities = entities.split(',')
    
    conn = connecting(user=user, host=host, database=database)
    insert_data = Insert_Data(conn)
    
    try:
        insert_data.insert_data('artist', 
                                artist_name=entities[0],
                                phone_nr=entities[1],
                                email=entities[2]
                            )
    except Exception as e:
        print(e)
    
    return redirect(url_for('schedule'))


form_values = {}

def create_session(read_data, insert_data, cursor):
    try:
        print('artist name: ', form_values['artist_name'])
        artist_id = get_artist_entity(read_data,
                        artist_name=form_values['artist_name'])[0][1]   
        
        print('Artist id Exception: ', artist_id)
        print('\nInserting data into table session...', end='---> ')
        insert_data.insert_data('session',
                                artist_name=form_values['artist_name'],
                                session_type=form_values['session_type'],
                                session_date=form_values['session_date'],
                                artist_id=artist_id
                                )
        
        statement = f'select sess_id from session where artist_name=\"{form_values["artist_name"]}\"'
        
        cursor.execute(statement)
        sess_id = cursor.fetchall()[-1][0]
        print(sess_id)
        
        if form_values['session_type'] == 'record':
            insert_data.insert_data('music', artist_id=artist_id,
                                    artist_name=form_values['artist_name'],
                                    sess_id=sess_id)
            
    except Exception as e:
        print(e)
            
            
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    
    read_data = Read_Data(conn, cursor=cursor)
    insert_data = Insert_Data(conn)
    
    if request.method == 'POST':
        artist_name = request.form['name']
        phone_nr = request.form['tel']
        email = request.form['email']
        session_type = request.form['session']
        _date = request.form['date']
        _time = request.form['time']
        session_date = f'{_date} {_time}:00'
        
        form_values['artist_name'] = artist_name
        form_values['session_type'] = session_type
        form_values['session_date'] = session_date
        
        try:
            artist_entity = get_artist_entity(read_data,artist_name=artist_name)
            
        except Exception as e:
            artist_entity = None
            
        if artist_entity is not None:
            entities = f'{artist_name},{phone_nr},{email}'
            return redirect(url_for('insert_data', entities=entities))
        else:
            create_session(read_data=read_data, insert_data=insert_data,
                        cursor=cursor)
    else:
        create_session(read_data=read_data, insert_data=insert_data, 
                    cursor=cursor)
        
    return render_template('schedule.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    global messages
    now_time = strftime('%Y-%m-%d %H:%M:%S')
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    insert_data = Insert_Data(conn)
    read_data = Read_Data(conn, cursor=cursor)
    
    if request.method == 'POST':
        author = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        try:
            insert_data.insert_data('comment',
                        author=author,
                        author_email=email,
                        message=message,
                        com_date=now_time)
            
            entity = read_data.read_data_from_single_table('comment')

            if len(entity) > 3:
                messages = entity[-3:]
            else:
                messages = entity

            return render_template('home.html', messages=messages)
        except Exception as e:
            print(e)
            
    return render_template('message_info.html', messages=messages)


@app.route('/release', methods=['GET', 'POST'])
def releases():
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    
    read_data = Read_Data(conn, cursor=cursor)

    music_table = read_data.read_data_from_single_table('music')
    
    return render_template('release.html', music_data=music_table)


@app.route('/session', methods=['GET', 'POST'])
def session():
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    
    read_data = Read_Data(conn, cursor=cursor)

    session_table = read_data.read_data_from_single_table('session')
    return render_template('session.html', session_data=session_table)


@app.route('/search', methods=['GET'])
def search():

    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    
    read_data = Read_Data(conn, cursor=cursor)

    if request.method == 'GET':
        kword = request.args.get('search')
        
        music_table = read_data.read_data_from_single_table(
            'music', artist_name=kword)
        
        session_table = read_data.read_data_from_single_table('session',
                                            artist_name=kword)
        
        return render_template('search.html', music_data=music_table, 
                            session_data=session_table, kword=kword)




#   ADMIN ROUTES    #

@app.route('/login', methods=['GET','POST'])
def login_hendler():
    
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        passwd = request.form['passwd']
        
        if username == 'admin' and passwd == 'minux':
            
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('admin_page'))
        else:
            flash('Invalid username or password!', 'error')
            return render_template('login.html')
                
    return render_template('login.html')


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


@app.route('/update', methods=['POST', 'GET'])
def manage_data():
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    
    read_data = Read_Data(conn, cursor=cursor)

    music_table = read_data.read_data_from_single_table('music')
    
    session_table = read_data.read_data_in_join_mode(
            'session', 'artist', 10)
    
    return render_template('update.html')


@app.route('/delete', methods=['POST', 'GET'])
def delete_data():
    pass


row_id = 0
table = 'music'

@app.route('/edit/<int:row>/<db>', methods=['POST', 'GET'])
def get_row(row, db):
    global row_id
    row_id = row
    if db == 'Music':
        return render_template('music_info.html')
    elif db == 'session':
        return render_template('session_info.html')
    else:
        return render_template('artist_info.html')


@app.route('/musicdb')
def redirect_music():
    global table
    table = 'music'
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    read_data = Read_Data(conn, cursor=cursor)
    music_table = read_data.read_data_from_single_table('music')
    
    return render_template('update_music.html', 
                            music_data=music_table, 
                            db='Music')


@app.route('/sessiondb')
def redirect_session():
    global table
    table = 'session'
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    read_data = Read_Data(conn, cursor=cursor)    
    
    session_table = read_data.read_data_in_join_mode(
            'session', 'artist')
    
    return render_template('update_session.html', 
                    session_data=session_table,
                    db='session')



@app.route('/artistdb')
def redirect_artist():
    global table
    table = 'artist'
    
    conn = connecting(user=user, host=host, database=database)
    cursor = conn.cursor(buffered=True)
    read_data = Read_Data(conn, cursor=cursor)

    artist_table = read_data.read_data_from_single_table('artist')
    
    return render_template('update_music.html', 
                            music_data=artist_table, 
                            db='Phone Nr',
                            table='Artist')


@app.route('/update/data', methods=['POST','GET'])
def update_music():
    global row_id, table
    
    print('Printing table: ', table)
    
    conn = connecting(user=user, host=host, database=database)
    insert_data = Insert_Data(conn)
    
    if request.method == 'POST':
        flash('Linha actualizada com sucesso!', 'success')
                
        if table == 'music':
            file_name = request.form['file_name']
            release_date = request.form['release']
            download_link = request.form['link']
            
            insert_data.update_entries('music', music_id=row_id,
                        file_name=file_name, 
                        release_date=release_date, 
                        download_link=download_link)

            return redirect(url_for('redirect_music'))
            
        elif table == 'session':
            session = request.form['session']
            status = request.form['status']
            session_date = request.form['date']
            
            insert_data.update_entries('session',
                        sess_id =row_id,
                        status=status,
                        session_type=session, 
                        session_date=session_date)

            return redirect(url_for('redirect_session'))
        else:
            phone_nr = request.form['tel']
            name = request.form['artist_name']
            email = request.form['email']
            
            insert_data.update_entries('artist',
                        art_id=row_id,
                        artist_name=name,
                        phone_nr=phone_nr, 
                        email=email)

            return redirect(url_for('redirect_artist'))
    else:
        return render_template('update_music.html')