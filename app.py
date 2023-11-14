from flask import Flask, url_for, render_template, redirect, request, session
from flask_mysqldb import MySQL
from flask_login import current_user
import mysql.connector

app = Flask(__name__)

app.secret_key = 'your-secret-key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
# get data with db column name instead of index
app.config["MYSQL_CURSORCLASS"] = "DictCursor" 


mysql = MySQL(app)
# login_manage = LoginManager()
# login_manage.init_app(app)

@app.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM post")
    data = cur.fetchall()
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None  

    if 'username' not in session:

        print(">>>>>> HOME RED", session)
        # User is not logged in, redirect them to the login page
        return redirect(url_for('login'))


    return render_template("index.html", post=data, username=username)



@app.route('/insert', methods = ['GET', 'POST'])
def insert():
    if request.method == "POST":

        caption = request.form['caption']
        image = request.form['image']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post (caption, image) VALUES ('%s', '%s')" % (caption, image),)
        mysql.connection.commit()

        return redirect(url_for('index'))
    
@app.route('/update',methods=['GET', 'POST'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        caption = request.form['caption']
        sql = "UPDATE post SET caption='{caption}' WHERE id={id}".format(caption = caption, id = id_data)
        print(sql)
        cur = mysql.connection.cursor()
        cur.execute(sql)
        mysql.connection.commit()
        return redirect(url_for('index'))
    
@app.route('/delete/<string:id_data>', methods = ['GET', 'POST'])
def delete(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM post WHERE id = %s", [id_data])
    mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/edit/<string:id_data>', methods=['GET', 'POST'])
def edit(id_data):
    item = {'key' : 'value'}

    if request.method == 'POST':
        id_data = request.form['id']
        caption = request.form['caption']
        sql = "SELECT * FROM post caption='{caption}' WHERE id={id}".format(caption = caption, id = id_data)
    else:
        sql = "SELECT * FROM post WHERE id={id}".format(id = id_data)
        cur = mysql.connection.cursor()
        cur.execute(sql)
        mysql.connection.commit()
    return render_template('edit.html', item = item)

# @app.route('/upvote/<int:id>')
# def upvote(id):
#     if request.method == 'POST':
#         post_id = request.form['id']
#         cur = mysql.connection.cursor(dictionary=True)
#         cur.execute("UPDATE posts SET upvotes = upvotes + 1 WHERE id = %s", (id,))
#         cur.close()
#         return redirect(url_for('index', post_id= post_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        

        print(">>>>>> user in sess")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT id, username, password from users WHERE username = %s"
        cur = mysql.connection.cursor()
        cur.execute(sql, (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and password == user['password']:
            session['username'] = user['username']
            print(">>>>>> user in 120")
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()

        # Check if the username already exists in the database
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return render_template('signup.html', error = "Username already exists. Please choose a different username.")
        else:
            # Insert new user data into the database
            sql = "INSERT INTO users (name, username, password) VALUES(%s, %s, %s)"
            data = (name, username, password)
            cur.execute(sql, data)
            cur.close()
            mysql.connection.commit()
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port = 8080)