from flask import Flask, render_template, request, redirect, url_for, session, send_file
import secrets, requests, datetime, os
import pymysql
from config import get_db_connection
from scrapping import scrapp_website
from excel import convert_to_excel, convert_bulk_to_excel
from collections import defaultdict

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

@app.route('/')
def check_connection():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        if result:
            return 'Connected to the database'
        else:
            return 'Failed to connect to the database'

    except Exception as e:
        return f'Error: {str(e)}'

def zip_lists(list1, list2):
    return zip(list1, list2)

app.jinja_env.filters['zip_lists'] = zip_lists

@app.route('/login')
def login():
    error = session.pop('error', '')
    username = session.pop('username', '')
    email = session.pop('email', '')
    id = session.pop('id', '')
    return render_template('login.html', error=error, email=email, username=username, id=id)

@app.route('/process_login', methods=['POST'])
def process_login():
    username = request.form.get('username_email')
    password = request.form.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE USER_EMAIL = %s or USER_NAME = %s", (username,username))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        error = cur.rowcount
        session['error'] = error 
        return redirect(url_for('login'))
    else:
        if (password != row[3]):
            error = 'The password you entered is incorrect'
            session['error'] = error 
            return redirect(url_for('login'))
        else:
            session['username'] = row[1]
            session['email'] = row[2]
            session['id'] = row[0]
            return redirect(url_for('one_link'))


@app.route('/signup')
def signup():
    error = session.pop('error', '')
    return render_template('signup.html', error=error)

@app.route('/process_signup', methods=['POST'])
def process_signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if (password != confirm_password):
        error = 'the passwords are not identical'
        session['error'] = error 
        return redirect(url_for('signup'))
        

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE USER_EMAIL = %s or USER_NAME = %s", (email,username))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is not None:
        error = 'the email or the username you entered already exists'
        session['error'] = error 
        return redirect(url_for('signup'))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user (USER_EMAIL, USER_NAME, USER_PASSWORD) VALUES (%s, %s, %s)", (email, username, password))
        conn.commit()
        cur.execute("SELECT * FROM user WHERE USER_EMAIL = %s and USER_NAME = %s", (email,username))
        row = cur.fetchone()
        cur.close()
        conn.close()
        session['username'] = username
        session['email'] = email
        session['id'] = row[0]
        return redirect(url_for('one_link'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  

@app.route('/one_link')
def one_link():
    if ('username' in session and 'email' in session and 'id' in session):
        username = session['username']
        email = session['email']
        id = session['id']
        error = session.pop('error', '')
        return render_template('one_link.html' , username=username, email=email, id=id, error=error)
    else:
        return redirect(url_for('logout'))
    
@app.route('/process_onelink_action', methods=['POST'])
def process_onelink_action():
    url = request.form.get('url_input')
    emails = scrapp_website(url)
    count_emails = len(emails)
    id = session['id']
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO action (USER_ID, ACTION_DATE, ACTION_TIME, ACTION_RESULT, ACTION_SEPARATOR, ACTION_INPUT, ACTION_INPUT_TYPE ) VALUES (%s, %s, %s, NULL, NULL, %s, 'mono_link')", (id, formatted_date, formatted_time, url))
    conn.commit()
    
    cur.execute("SELECT ACTION_ID FROM action WHERE USER_ID = %s and ACTION_DATE = %s and ACTION_timE = %s and ACTION_INPUT = %s", (session['id'],formatted_date,formatted_time,url))
    action_id = cur.fetchone()[0]

    cur.execute("INSERT INTO URLS (ACTION_ID, USER_ID, URL_LINK, URL_EMAILS) VALUES (%s, %s, %s, %s)", (action_id, session['id'], url, count_emails))
    conn.commit()

    cur.close()
    conn.close()
    if count_emails > 0:

        convert_to_excel(action_id,emails,url)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE action SET ACTION_RESULT = 'results/%s.xlsx' WHERE ACTION_ID = %s", (action_id, action_id))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('process_result', action_id=action_id))
        

@app.route('/multi_link')
def multi_link():
    if ('username' in session and 'email' in session and 'id' in session):
        username = session['username']
        email = session['email']
        id = session['id']
        error = session.pop('error', '')
        return render_template('multi_link.html' , username=username, email=email, id=id, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/process_bulktext_action', methods=['POST'])
def process_bulktext_action():
    input = request.form.get('bulk_text')
    lines = input.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    urls = []
    bad_urls = []

    for line in lines:
        if line.startswith('http://') or line.startswith('https://'):
            try:
                response = requests.get(line)
                if response.status_code == 200:
                    urls.append(line)
                else:
                    bad_urls.append(line)
            except requests.exceptions.ConnectionError:
                bad_urls.append(line)
    
    if len(urls) == 0:
        error = 'Sorry, these urls you entered could not be scrapped'
        session['error'] = error
        return redirect(url_for('multi_link'))
    
    else:
        emails = []
        count_emails = []
        i = 0
        for url in urls:
            response = requests.get(url)
            emails.append(scrapp_website(response))
            count_emails.append(len(emails[i]))
            i += 1
        id = session['id']
        current_date = datetime.date.today()
        formatted_date = current_date.strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M")
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO action (USER_ID, ACTION_DATE, ACTION_TIME, ACTION_RESULT, ACTION_SEPARATOR, ACTION_INPUT, ACTION_INPUT_TYPE ) VALUES (%s, %s, %s, NULL, NULL, %s, 'bulk_text')", (id, formatted_date, formatted_time, input))
        conn.commit()
            
        cur.execute("SELECT ACTION_ID FROM action WHERE USER_ID = %s and ACTION_DATE = %s and ACTION_timE = %s and ACTION_INPUT = %s", (session['id'],formatted_date,formatted_time,input))
        action_id = cur.fetchone()[0]

        i=0

        for url in urls:
            cur.execute("INSERT INTO urls (ACTION_ID, USER_ID, URL_LINK, URL_EMAILS) VALUES (%s, %s, %s, %s)", (action_id, session['id'], url, count_emails[i]))
            conn.commit()
            i+=1

        cur.close()
        conn.close()

        if sum(count_emails) > 0:
            convert_bulk_to_excel(action_id,emails,urls)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE action SET ACTION_RESULT = 'results/%s.xlsx' WHERE ACTION_ID = %s", (action_id, action_id))
            conn.commit()
            cur.close()
            conn.close()
        
        return redirect(url_for('process_result', action_id=action_id))

@app.route('/historique')
def historique():
    if ('username' in session and 'email' in session and 'id' in session):
        username = session['username']
        email = session['email']
        id = session['id']
        error = session.pop('error', '')
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM action WHERE USER_ID = %s ORDER BY ACTION_DATE DESC, ACTION_TIME DESC", (id))
        rows = cur.fetchall()

        sorted_actions = []
        action_date = ''
        for row in rows:
            if row[2] == action_date:
                sorted_actions[-1].append(row)
            else:
                sorted_actions.append([row])
                action_date = row[2]

        cur.close()
        conn.close()
        return render_template('historique.html', username=username, email=email, id=id, error=error, actions = sorted_actions)
    else:
        return redirect(url_for('logout'))

@app.route('/delete_action/<action_id>')
def delete_action(action_id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM urls WHERE ACTION_ID = %s", (action_id))
    conn.commit()
    cur.execute("DELETE FROM action WHERE ACTION_ID = %s", (action_id))
    conn.commit()

    cur.close()
    conn.close()


    file_path = 'results/' + str(action_id) +'.xlsx'

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for('historique'))

    

@app.route('/result')
def result():
    if ('username' in session and 'email' in session and 'id' in session):
        username = session['username']
        email = session['email']
        id = session['id']
        error = session.pop('error', '')
        action_id = request.args.get('action_id')
        heading = request.args.get('heading')
        count_emails = request.args.get('count_emails')
        urls = request.args.getlist('urls')
        emails = request.args.getlist('emails')
        zipped_data = list(zip(urls, emails))
        type_result = request.args.get('type_result')
        return render_template('result.html', action_id = action_id, count_emails=count_emails, heading=heading, zipped_data=zipped_data, type_result = type_result , username=username, email=email, id=id, error=error)
    else:
        return redirect(url_for('logout'))

@app.route('/process_result/<action_id>')
def process_result(action_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM action WHERE ACTION_ID = %s", (action_id))
    row = cur.fetchone()
    user_id = row[1]
    if user_id != session['id']:
        return redirect(url_for(one_link))
    if row[7] == 'mono_link':
        type_result = 'mono_link'
        urls = row[6]
        cur.execute("SELECT * FROM urls WHERE ACTION_ID = %s", (action_id))
        row = cur.fetchone()
        emails = row[4]
        count_emails = emails
        if emails == 0 :
            heading = '0 out of 1 that has emails'
        else :
            heading = '1 out of 1 that has emails'
    elif row[7] == 'bulk_text':
        type_result = 'bulk_text'
        cur.execute("SELECT * FROM urls WHERE ACTION_ID = %s", (action_id))
        rows = cur.fetchall()
        emails = []
        urls = []
        i = 0
        for row in rows:
            emails.append(row[4])
            urls.append(row[3])
            if row[4] != 0:
                i+=1
        count_emails = sum(emails)
        heading = str(i) + ' out of ' + str(len(emails)) + ' that has emails'
        cur.close()
        conn.close()
    return redirect(url_for('result',action_id=action_id, heading=heading, count_emails = count_emails, emails=emails, urls=urls , type_result=type_result))
    
    
        
        
    

    

@app.route('/download_excel/<filename>')
def download_excel(filename):

    folder = 'results/'
    full_path = folder + filename

    return send_file(full_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
