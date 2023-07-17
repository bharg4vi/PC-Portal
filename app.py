from flask import Flask, render_template, redirect, request
import pyodbc

app = Flask(__name__)


def connection(server, database):
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes;'
    conn = pyodbc.connect(cstr)
    return conn

@app.route('/add_company', methods=['POST'])
def add_company():
    # Get form data from the request
    server = ''
    database = 'tcp_companies'
    name = request.form['name']
    description = request.form['description']
    location = request.form['location']
    package = float(request.form['package'])
    roles = request.form['roles']

    # Create a database connection
    conn = connection(server, database)
    cursor = conn.cursor()

    sql_query = "INSERT INTO companies (name, description, location, package, roles) VALUES (?, ?, ?, ?, ?)"
    values = (name, description, location, package, roles)

    try:
    # Execute the SQL query with parameterized values
        cursor.execute(sql_query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return "Company added successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/gen_company', methods=['POST'])
def gen_company():
    # Get form data from the request
    server = ''
    database = 'tcp_companies'
    name = request.form['company_name']

    # Create a database connection
    conn = connection(server, database)
    cursor = conn.cursor()

    sql_query = "EXEC GenerateCompanyCredentials @CompanyName =" + name
 
    try:
    # Execute the SQL query with parameterized values
        cursor.execute(sql_query)
        conn.commit()
        cursor.close()
        conn.close()

        return "Company added successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/add_student', methods=['POST'])
def add_student():
    # Get form data from the request
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    startId = request.form['student_start_id']
    endId = request.form['student_end_id']

    # Create a database connection
    conn = connection(server, database)
    cursor = conn.cursor()

    sql_query = "EXEC InsertIDsInRange @startID = ?, @endID = ?"
    values = (startId, endId)

    try:
        # Execute the SQL query with parameterized values
        cursor.execute(sql_query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return "Student added successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/admin', methods=['POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        if username == 'admin' and password == 'bhar&123':
            return render_template('insertData.html')
        else:
            return redirect('/error')


@app.route('/student', methods=['POST'])
def student():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    username = request.form['username']
    password = request.form['password']

    conn = connection(server, database)
    cursor = conn.cursor()

    sql_query = "SELECT CompanyName FROM CompanyCredentials WHERE CompanyId = " +"'"+ username +"'"+ "and "+"Password = " +"'"+ password +"'"
    print(username, password)
    print(sql_query)
    try:
        # Execute the SQL query with parameterized values
        cursor.execute(sql_query)
        result = cursor.fetchall()

        if result is not None:
            # Username and password combination exists in the table
            cursor.close()
            conn.close()
            return render_template('index.html')
        else:

            cursor.close()
            conn.close()
            return "Username and password do not exist!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/company', methods=['POST'])
def company():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_companies'
    username = request.form['username']
    password = request.form['password']

    # Create a database connection
    conn = connection(server, database)
    cursor = conn.cursor()

    sql_query = "SELECT CompanyName FROM CompanyCredentials WHERE CompanyId = " +"'"+ username +"'"+ "and "+"Password = " +"'"+ password +"'"
    print(username, password)
    print(sql_query)
    try:
        # Execute the SQL query with parameterized values
        cursor.execute(sql_query)
        result = cursor.fetchall()

        if result is not None:
            # Username and password combination exists in the table
            cursor.close()
            conn.close()
            return render_template('index.html')
        else:
            # Username and password combination does not exist in the table
            cursor.close()
            conn.close()
            return "Username and password do not exist!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/success')
def success():
    return "Success! Connection established."

@app.route('/error')
def error():
    return "Error! Invalid username or password."

if __name__ == "__main__":
    app.run(debug=True)
