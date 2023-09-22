#this is all i need to import for this project
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
from config import get_db_connection
from scrapping import *
from excel import *
from advanced import *
import secrets, requests, datetime, os, pymysql

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

@app.route('/')
def check_connection():
    #using config.py to get a connection to the database
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            foundResult = cursor.fetchone()

        if foundResult:
            return redirect(url_for('login'))
        else:
            return 'Failed to connect to the database'

    except Exception as e:
        return f'Error: {str(e)}'

@app.route('/login')
def login():
    #the session must contain the error if it exist and the username his email and id
    error = session.pop('error', '')
    username = session.pop('username', '')
    email = session.pop('email', '')
    userId = session.pop('userId', '')
    return render_template('login.html', error=error, email=email, username=username, id=id)

@app.route('/process_login', methods=['POST'])
def process_login():
    username = request.form.get('username_email')
    enteredPassword = request.form.get('password')
    #check if the username or the emails entered is in the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE USER_EMAIL = %s or USER_NAME = %s", (username,username))
    userInfo = cur.fetchone()
    cur.close()
    conn.close()

    if userInfo is None:
        error = 'This username or the email does not exist'
        session['error'] = error 
        return redirect(url_for('login'))
    else:
        #check if the password is correct
        realPassword = userInfo[3]
        if check_password_hash(realPassword, enteredPassword):
            error = 'The password you entered is incorrect'
            session['error'] = error 
            return redirect(url_for('login'))
        else:
            session['username'] = userInfo[1]
            session['email'] = userInfo[2]
            session['userId'] = userInfo[0]
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
    userInfo = cur.fetchone()
    #check if the email or the username already exist
    if userInfo is not None:
        error = 'the email or the username you entered already exists'
        session['error'] = error 
        return redirect(url_for('signup'))
    else:
        cur.execute("INSERT INTO user (USER_EMAIL, USER_NAME, USER_PASSWORD) VALUES (%s, %s, %s)", (email, username, generate_password_hash(password)))
        conn.commit()
        cur.execute("SELECT USER_ID FROM user WHERE USER_NAME = %s", (username))
        userId = cur.fetchone()[0]
        cur.close()
        conn.close()
        session['username'] = username
        session['email'] = email
        session['userId'] = userId
        return redirect(url_for('one_link'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  

@app.route('/one_link')
def one_link():
    if ('username' in session and 'email' in session and 'userId' in session):
        username = session['username']
        email = session['email']
        userId = session['userId']
        error = session.pop('error', '')
        return render_template('one_link.html' , username=username, email=email, userId=userId, error=error)
    else:
        return redirect(url_for('logout'))
    
@app.route('/process_onelink_action', methods=['POST'])
def process_onelink_action():
    if ('username' in session and 'email' in session and 'userId' in session):
        #scrapp the enteredUrl and count the scrapped emails
        enteredUrl = request.form.get('url_input')
        scrappedEmails = scrapp_website(enteredUrl,'//body')
        countScrappedEmails = len(scrappedEmails)
        userId = session['userId']
        currentDate = datetime.date.today()
        formattedDate = currentDate.strftime("%d-%m-%Y")
        currentTime = datetime.datetime.now().time()
        formattedTime = currentTime.strftime("%H:%M")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO action (USER_ID, ACTION_DATE, ACTION_TIME, ACTION_RESULT, ACTION_INPUT, ACTION_INPUT_TYPE ) VALUES (%s, %s, %s, NULL, %s, 'mono_link')", (userId, formattedDate, formattedTime, enteredUrl))
        conn.commit()
        #there is a probability that the action id below can have more than one row
        cur.execute("SELECT ACTION_ID FROM action WHERE USER_ID = %s and ACTION_DATE = %s and ACTION_TIME = %s and ACTION_INPUT = %s", (userId,formattedDate,formattedTime,enteredUrl))
        actionId = cur.fetchone()[0]
        cur.execute("INSERT INTO URLS (ACTION_ID, USER_ID, URL_LINK, URL_EMAILS) VALUES (%s, %s, %s, %s)", (actionId, session['userId'], enteredUrl, countScrappedEmails))
        conn.commit()

        if countScrappedEmails > 0:
            resultPath = convert_to_excel(actionId,scrappedEmails,enteredUrl)
            cur.execute("UPDATE action SET ACTION_RESULT = %s WHERE ACTION_ID = %s", (resultPath, actionId))
            conn.commit()
        
        cur.close()
        conn.close()
        return redirect(url_for('process_result', actionId=actionId))
    else:
        return redirect(url_for('logout'))
        

@app.route('/multi_link')
def multi_link():
    if ('username' in session and 'email' in session and 'userId' in session):
        username = session['username']
        email = session['email']
        userId = session['userId']
        error = session.pop('error', '')
        return render_template('multi_link.html' , username=username, email=email, userId=userId, error=error)
    else:
        return redirect(url_for('logout'))

@app.route('/process_bulktext_action', methods=['POST'])
def process_bulktext_action():
    if ('username' in session and 'email' in session and 'userId' in session):
        bulkText = request.form.get('bulk_text')
        lines = bulkText.split('\n')
        #take all the lines and rmove the whitespace in them then remove the empty lines then check if it is a valid url
        lines = [line.replace(' ','') for line in lines]
        lines = [line for line in lines if line]
        validUrls = []
        for line in lines:
            if line.startswith('http://') or line.startswith('https://'):
                validUrls.append(line)
        if len(validUrls) == 0:
            error = 'Sorry, these urls you entered could not be scrapped'
            session['error'] = error
            return redirect(url_for('multi_link'))
        else:
            scrappedEmails = []
            countScrappedEmails = []
            i = 0
            for url in validUrls:
                try:
                    scrappedEmails.append(scrapp_website(url,'//body'))
                except:
                    scrappedEmails.append([])
                countScrappedEmails.append(len(scrappedEmails[i]))
                i += 1
            userId = session['userId']
            currentDate = datetime.date.today()
            formattedDate = currentDate.strftime("%d-%m-%Y")
            currentTime = datetime.datetime.now().time()
            formattedTime = currentTime.strftime("%H:%M")
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO action (USER_ID, ACTION_DATE, ACTION_TIME, ACTION_RESULT, ACTION_INPUT, ACTION_INPUT_TYPE ) VALUES (%s, %s, %s, NULL, %s, 'bulk_text')", (userId, formattedDate, formattedTime, bulkText))
            conn.commit()
            #there is a probability that the action id below can have more than one row
            cur.execute("SELECT ACTION_ID FROM action WHERE USER_ID = %s and ACTION_DATE = %s and ACTION_timE = %s and ACTION_INPUT = %s", (userId,formattedDate,formattedTime,bulkText))
            actionId = cur.fetchone()[0]

            i = 0
            for url in validUrls:
                cur.execute("INSERT INTO urls (ACTION_ID, USER_ID, URL_LINK, URL_EMAILS) VALUES (%s, %s, %s, %s)", (actionId, userId, url, countScrappedEmails[i]))
                conn.commit()
                i+=1
            if sum(countScrappedEmails) > 0:
                resultPath = convert_bulk_to_excel(actionId,scrappedEmails,validUrls)
                cur.execute("UPDATE action SET ACTION_RESULT = %s WHERE ACTION_ID = %s", (resultPath, actionId))
                conn.commit()

            cur.close()
            conn.close()
            return redirect(url_for('process_result', actionId=actionId))
    else:
        return redirect(url_for('logout'))

@app.route('/historique')
def historique():
    if ('username' in session and 'email' in session and 'userId' in session):
        username = session['username']
        email = session['email']
        userId = session['userId']
        error = session.pop('error', '')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM action WHERE USER_ID = %s ORDER BY ACTION_ID DESC", (userId))
        userActions = cur.fetchall()
        #sort the actions to be an array that contains arrays that have the same date
        sortedActions = []
        actionDate = ''
        for row in userActions:
            if row[2] == actionDate:
                sortedActions[-1].append(row)
            else:
                sortedActions.append([row])
                actionDate = row[2]
        cur.close()
        conn.close()
        print(sortedActions)
        return render_template('historique.html', username=username, email=email, userId=userId, error=error, actions = sortedActions)
    else:
        return redirect(url_for('logout'))

@app.route('/delete_action/<actionId>')
def delete_action(actionId):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ACTION_RESULT FROM ACTION WHERE ACTION_ID = %s",(actionId))
    actionResult = cur.fetchone()[0]
    cur.execute("DELETE FROM urls WHERE ACTION_ID = %s", (actionId))
    conn.commit()
    cur.execute("DELETE FROM action WHERE ACTION_ID = %s", (actionId))
    conn.commit()
    cur.close()
    conn.close()
    
    file_path = 'results/' + str(actionResult)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('historique'))

@app.route('/result')
def result():
    if ('username' in session and 'email' in session and 'userId' in session):
        username = session['username']
        email = session['email']
        userId = session['userId']
        error = session.pop('error', '')
        actionId = request.args.get('actionId')
        heading = request.args.get('heading')
        sumEmailsNumb = request.args.get('sumEmailsNumb')
        links = request.args.getlist('links')
        emailsNumb = request.args.getlist('emailsNumb')
        zipped_data = list(zip(links, emailsNumb))
        actionType = request.args.get('actionType')
        resultPath = request.args.get('resultPath')
        return render_template('result.html', actionId = actionId, resultPath=resultPath, sumEmailsNumb=sumEmailsNumb, heading=heading, zipped_data=zipped_data, actionType = actionType , username=username, emailsNumb=emailsNumb, UserId=userId, error=error)
    else:
        return redirect(url_for('logout'))

@app.route('/process_result/<actionId>')
def process_result(actionId):
    if ('username' in session and 'email' in session and 'userId' in session):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM action WHERE ACTION_ID = %s", (actionId))
        action = cur.fetchone()
        userId = action[1]
        resultPath = action[4]
        actionType = action[6]

        if userId != session['userId']:
            return redirect(url_for(one_link))
        if actionType == 'mono_link':
            cur.execute("SELECT * FROM urls WHERE ACTION_ID = %s", (actionId))
            url = cur.fetchone()
            emailsNumb = url[4]
            links = url[3]
            sumEmailsNumb = emailsNumb
            if emailsNumb == 0 :
                heading = '0 out of 1 that has emails'
            else :
                heading = '1 out of 1 that has emails'
        elif actionType == 'bulk_text':
            cur.execute("SELECT * FROM urls WHERE ACTION_ID = %s", (actionId))
            urls = cur.fetchall()
            emailsNumb = []
            links = []
            failedLinks = 0
            for row in urls:
                emailsNumb.append(row[4])
                links.append(row[3])
                if row[4] != 0:
                    failedLinks+=1
            sumEmailsNumb = sum(emailsNumb)
            heading = str(failedLinks) + ' out of ' + str(len(links)) + ' that has emails'
        cur.close()
        conn.close()
        return redirect(url_for('result',actionId=actionId, resultPath=resultPath, heading=heading, sumEmailsNumb = sumEmailsNumb, emailsNumb=emailsNumb, links=links , actionType=actionType))
    else:
        return redirect(url_for('logout'))

@app.route('/advanced_scrapping/<actionId>', methods=['POST'])
def advanced_scrapping(actionId):
    htmlInput = request.form.get('html_format')
    emailInput = request.form.get('email_format')
    actionTypeInput = request.form.get('action_type')
    actionInput = request.form.get('action_input')
    
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM urls WHERE ACTION_ID = %s", (actionId))
    urls_rows = cur.fetchall()
    cur.execute("SELECT * FROM action WHERE ACTION_ID = %s", (actionId))
    action_row = cur.fetchone()
    if action_row[6] == 'mono_link':
        emails = pick_scrapping_method(urls_rows[0][3],emailInput,htmlInput,actionTypeInput,actionInput)   
        if len(emails) > urls_rows[0][4]:
            if urls_rows[0][4] > 0:
                filePath = 'results/' + str(action_row[0])
                if os.path.exists(filePath):
                    os.remove(filePath)
            filename = convert_to_excel(actionId,emails,urls_rows[0][3])
            cur.execute("UPDATE urls SET URL_EMAILS = %s WHERE ACTION_ID = %s", (len(emails), actionId))
            conn.commit()
            cur.execute("UPDATE action SET ACTION_RESULT = %s WHERE ACTION_ID = %s", (filename, actionId))
            conn.commit()
    elif (action_row[6] == 'bulk_text'):
        i = 0
        urls = []
        emails = []
        countEmails = []
        for row in urls_rows:
            url = row[3]
            email = list(pick_scrapping_method(url,emailInput,htmlInput,actionTypeInput,actionInput))
            if len(email) > row[4]:
                urls.append(url)
                emails.append(email)
                count_emails.append(len(emails[i]))
                i+=1
        if sum(count_emails)>0:
            if action_row[4] == None:
                filename = convert_bulk_to_excel(actionId,emails,urls)
                cur.execute("UPDATE action SET ACTION_RESULT = %s WHERE ACTION_ID = %s", (filename, actionId))
                conn.commit()
            else:
                update_excel(action_row[4],emails,urls)
            for row in urls_rows:
                if row[3] in urls:
                    i = urls.index(row[3])
                    cur.execute("UPDATE urls SET URL_EMAILS = %s WHERE URL_ID = %s", (count_emails[i], row[0]))
                    conn.commit()
            
    cur.close()
    conn.close()
    return redirect(url_for('process_result', actionId=actionId))

@app.route('/download_excel/<filename>')
def download_excel(filename):
    folder = 'results/'
    full_path = folder + filename
    return send_file(full_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
