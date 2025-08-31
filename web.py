from flask import Flask,render_template,request
import mysql.connector

#Hardcoded credentials for demo
USERNAME = 'admin'
PASSWORD = '123'

#Database connection function
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='2659',
        database='Projecttest'
    )



app = Flask(__name__)

# Register Page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if not username or not password or not role:
            return render_template('signin.html', msg='All fields are required.')
        conn = connect_db()
        cursor = conn.cursor()
        try:
            query = 'INSERT INTO user (username, password, role) VALUES (%s, %s, %s)'
            cursor.execute(query, (username, password, role))
            conn.commit()
        except mysql.connector.IntegrityError:
            cursor.close()
            giconn.close()
            return render_template('signin.html', msg='Username already exists.')
        cursor.close()
        conn.close()
        return render_template('login.html', msg='Registration successful. Please log in.')
    return render_template('signin.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = connect_db()
        cursor = conn.cursor()
        query = 'SELECT * FROM user WHERE username = %s AND password = %s'
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return render_template('home.html')
        else:
            return render_template('login.html', msg='Invalid username or password')
    return render_template('login.html')

# Home Page
@app.route('/home')
def home():
    return render_template('home.html')

# View Function
@app.route('/view')
def view_events():
    conn = connect_db()
    cursor = conn.cursor()
    query = 'SELECT * FROM events'
    cursor.execute(query)
    events = cursor.fetchall()
    cursor.close()
    
    return render_template('view.html', events=events)

# Add Function
@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_description = request.form.get('event_description')

        conn = connect_db()
        cursor = conn.cursor()
        query = 'INSERT INTO events VALUES (%s, %s, %s, %s, %s)'
        values = (event_id, event_name, event_date, event_location, event_description)
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return render_template('add.html', msg='Event added successfully')
    return render_template('add.html')
    

# Delete Function
@app.route('/delete', methods=['GET', 'POST'])
def delete_event():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        # Check if event_id is a valid integer
        if not event_id or not event_id.isdigit():
            return render_template('delete.html', msg='Please enter a valid numeric Event ID.')
        conn = connect_db()
        cursor = conn.cursor()
        query = 'DELETE FROM events WHERE event_id = %s'
        cursor.execute(query, (event_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        if deleted_count == 0:
            return render_template('delete.html', msg='No event found with that ID.')
        return render_template('delete.html', msg='Event deleted successfully')
    return render_template('delete.html')

# Update Function
@app.route('/update', methods=['GET', 'POST'])
def update_event():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        venue = request.form.get('event_location')
        description = request.form.get('event_description')

        conn = connect_db()
        cursor = conn.cursor()
        query = 'UPDATE events SET event_name = %s, event_date = %s, venue = %s, description = %s WHERE event_id = %s'
        cursor.execute(query, (event_name, event_date, venue, description, event_id))
        updated_count = cursor.rowcount
        conn.commit()
        cursor.close()
        if updated_count == 0:
            return render_template('update.html', msg='No event found with that ID.')
        return render_template('update.html', msg='Event updated successfully')
    return render_template('update.html')

# Search Function
@app.route('/search', methods=['GET', 'POST'])
def search_event():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        conn = connect_db()
        cursor = conn.cursor()
        query = 'SELECT * FROM events WHERE event_name LIKE %s'
        cursor.execute(query, ('%' + search_term + '%',))
        results = cursor.fetchall()
        cursor.close()
        if results:
            return render_template('search.html', events=results)
        else:
            return render_template('search.html', msg='No events found with that name.')
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
