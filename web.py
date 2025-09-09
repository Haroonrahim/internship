from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector

#Database connection function
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='2659',
        database='Projecttest'
    )

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

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
            conn.close()
            return render_template('signin.html', msg='Username already exists.')
        cursor.close()
        conn.close()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
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
            session['username'] = username  # Store username in session
            session['role'] = user[3]  # Assuming role is the 4th column in user table
            return redirect(url_for('home'))  # Redirect to home
        else:
            return render_template('login.html', msg='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))

# Home Page
@app.route('/')
def home():
    # Home is public, but show login if not logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session.get('username'))

# View Function
@app.route('/view')
def view_events():
    if 'username' not in session or session.get('role') not in ['student', 'professor', 'admin']:
        return redirect(url_for('login'))
    conn = connect_db()
    cursor = conn.cursor()
    query = 'SELECT * FROM events'
    cursor.execute(query)
    events = cursor.fetchall()
    cursor.close()
    user_role = session.get('role')
    username = session.get('username') # Add userrname
    return render_template('view.html', events=events, role=user_role, username=username)

def get_event_locations():
    # Get enum values for event_location column
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM events WHERE Field = 'event_location'")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        # Parse enum values from Type string: "enum('A','B','C')"
        import re
        match = re.search(r"enum\((.*)\)", row[1])
        if match:
            return [v.strip("'") for v in match.group(1).split(",")]
    return []

def get_event_times():
    # Get enum values for event_location column
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM events WHERE Field = 'event_time'")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        # Parse enum values from Type string: "enum('A','B','C')"
        import re
        match = re.search(r"enum\((.*)\)", row[1])
        if match:
            return [v.strip("'") for v in match.group(1).split(",")]
    return []

# Add Function
@app.route('/add', methods=['GET', 'POST'])
def add_event():
    from datetime import date, datetime
    current_date = date.today().isoformat()

    if 'username' not in session or session.get('role') not in ['professor', 'admin']:
        return redirect(url_for('login'))

    event_locations = get_event_locations()
    event_times = get_event_times()

    if request.method == 'POST':
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        
        # Date validation
        if event_date:
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
            if event_date_obj < date.today():
                return render_template('add.html', msg='Please select a future date.', event_locations=event_locations, event_times=event_times, current_date=current_date)
        
        event_location = request.form.get('event_location')
        event_time = request.form.get('event_time')
        event_description = request.form.get('event_description')
        professor_id = session.get('username')  # Store professor's username

        conn = connect_db()
        cursor = conn.cursor()

        # Check for duplicate event at same date, time, location
        cursor.execute('SELECT * FROM events WHERE event_date = %s AND event_time = %s AND event_location = %s', (event_date, event_time, event_location))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('add.html', msg='An event already exists at this date, time, and location.', event_locations=event_locations, event_times=event_times)
        
        # Insert event along with professor_id
        query = 'INSERT INTO events (event_name, event_date, event_time, event_location, event_description, professor_id) VALUES (%s, %s, %s, %s, %s, %s)'
        values = (event_name, event_date, event_time, event_location, event_description, professor_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('add.html', msg='Event added successfully', event_locations=event_locations, event_times=event_times, current_date=current_date)

    return render_template('add.html', event_locations=event_locations, event_times=event_times, current_date=current_date)


# Delete Function
@app.route('/delete', methods=['GET', 'POST'])
def delete_event():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
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
    from datetime import date, datetime
    current_date = date.today().isoformat()

    # Check for logged-in user and role
    if 'username' not in session or session.get('role') not in ['professor', 'admin']:
        return redirect(url_for('login'))

    event_locations = get_event_locations()
    event_times = get_event_times()
    event_data = None

    if request.method == 'GET':
        event_id = request.args.get('event_id')
        if event_id and event_id.isdigit():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE event_id = %s', (event_id,))
            event_data = cursor.fetchone()
            cursor.close()
            conn.close()
            if not event_data:
                flash('Event not found.', 'error')
                return redirect(url_for('view_events'))

    if request.method == 'POST':
        # Process form submission for update
        event_id = request.form.get('event_id')
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_time = request.form.get('event_time')
        event_description = request.form.get('event_description')

        # Date validation to ensure future date
        if event_date:
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
            if event_date_obj < date.today():
                return render_template('update.html', msg='Please select a future date.', 
                                       event_locations=event_locations,
                                       event_times=event_times,
                                       current_date=current_date,
                                       event=(event_id, event_name, event_date, event_time, event_location, event_description))

        conn = connect_db()
        cursor = conn.cursor()

        # Check if duplicate event exists at same date, time, location excluding this event
        cursor.execute('SELECT event_id FROM events WHERE event_date = %s AND event_time = %s AND event_location = %s AND event_id != %s',
                       (event_date, event_time, event_location, event_id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('update.html', msg='Another event already exists at this date, time, and location!',
                                   event_locations=event_locations,
                                   event_times=event_times,
                                   current_date=current_date,
                                   event=(event_id, event_name, event_date, event_time, event_location, event_description))
        
        # Update event
        query = '''UPDATE events SET event_name = %s, event_date = %s, event_time = %s, event_location = %s, event_description = %s WHERE event_id = %s'''
        cursor.execute(query, (event_name, event_date, event_time, event_location, event_description, event_id))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('update.html', msg='Event updated successfully', event_locations=event_locations,
                               event_times=event_times, current_date=current_date, event=None)

    # For GET request without event_id or to show form pre-filled
    return render_template('update.html', event_locations=event_locations, event_times=event_times,
                           current_date=current_date, event=event_data)


# Search Function
@app.route('/search', methods=['GET', 'POST'])
def search_event():
    if 'username' not in session:
        return redirect(url_for('login'))
    role = session.get('role')
    username = session.get('username')  # get current username from session
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        conn = connect_db()
        cursor = conn.cursor()
        query = 'SELECT * FROM events WHERE event_name LIKE %s'
        cursor.execute(query, ('%' + search_term + '%',))
        results = cursor.fetchall()
        cursor.close()
        if results:
            return render_template('search.html', events=results, role=role, username=username)
        else:
            return render_template('search.html', msg='No events found with that name.', role=role, username=username)
    return render_template('search.html', role=role, username=username)


if __name__ == '__main__':
    app.run(debug=True)
