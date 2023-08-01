from flask import Flask, render_template, redirect, request
import pyodbc
from flask import session, jsonify
import json

app = Flask(__name__)
app.secret_key = 'bhar&123'

def connection(server, database):
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes;'
    conn = pyodbc.connect(cstr)
    return conn

@app.route('/add_company', methods=['POST', 'GET'])
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
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
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


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        if username == 'admin' and password == 'bhar&123':
            return render_template('insertData.html')
        else:
            return redirect('/error')


@app.route('/add_data', methods=['POST'])
def add_data():
    # Check if the user is logged in and has a valid student_id in the session
    if 'student_id' not in session:
        return "Unauthorized access. Please log in first."

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    driver = '{ODBC Driver 17 for SQL Server}'
    trusted_connection = 'yes'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection}'
    
    try:
        cnxn = pyodbc.connect(connection_string)
        cursor = cnxn.cursor()

        if request.method == 'POST':
            # Retrieve form data
            full_name = request.form.get('name')
            dob = request.form.get('dob')
            email = request.form.get('email')
            phone_number = request.form.get('phnum')
            city = request.form.get('city')
            state = request.form.get('state')
            career_objective = request.form.get('ucareerob')
            about_self = request.form.get('uaboutself')
            id = session['student_id']
            fname = request.form.get('fname')
            mname = request.form.get('mname')
            paddress = request.form.get('paddress')

            # Insert the data into the Students table
            query = """
            MERGE INTO Students AS target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)) AS source (full_name, dob, email, phone_number, city, state, career_objective, about_self, id)
            ON target.student_id = source.id
            WHEN MATCHED THEN
                UPDATE SET
                    target.full_name = source.full_name,
                    target.dob = source.dob,
                    target.email = source.email,
                    target.phone_number = source.phone_number,
                    target.city = source.city,
                    target.state = source.state,
                    target.career_objective = source.career_objective,
                    target.about_self = source.about_self
            WHEN NOT MATCHED THEN
                INSERT (full_name, dob, email, phone_number, city, state, career_objective, about_self, student_id)
                VALUES (source.full_name, source.dob, source.email, source.phone_number, source.city, source.state, source.career_objective, source.about_self, source.id);
            """

            cursor.execute(query, full_name, dob, email, phone_number, city, state, career_objective, about_self, session['student_id'])
            cnxn.commit()

            # Insert data into PersonalDetails table
            query = """
            Insert into PersonalDetails (student_id, father_name, mother_name, permanent_address) values (?, ?, ?, ?)
            """
            cursor.execute(query, session['student_id'], fname, mname, paddress)
            cnxn.commit()

            # Fetch PersonalDetails data
            query = "SELECT * FROM PersonalDetails WHERE student_id = ?"
            cursor.execute(query, session['student_id'])
            pdetails = cursor.fetchone()

            # Fetch data for resume template
            query = "SELECT * FROM Students WHERE student_id = ?"
            cursor.execute(query, session['student_id'])
            result = cursor.fetchone()

            query = "SELECT * FROM Education WHERE student_id = ?"
            cursor.execute(query, session['student_id'])
            info = cursor.fetchall()

            query = "SELECT skill FROM Skills WHERE student_id = ?"
            cursor.execute(query, session['student_id'])
            skills = cursor.fetchall()
            
            return render_template('resume.html', data=result, info=info, skills=skills, pdetails=pdetails)

        else:
            return "This page is for data submission. Use POST to submit data."
    
    except Exception as e:
        # Handle any exceptions that may occur during database operations
        return f"An error occurred: {str(e)}"


@app.route('/student', methods=['POST'])
def student():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        id = session['student_id']
        print("id: ", id)
        
        conn = connection(server, database)
        cursor = conn.cursor()
        sql_query = "SELECT studentID from validlogin where studentId = ? and Password = ?"
        
        try:
            cursor.execute(sql_query, username, password)
            result = cursor.fetchone()

            if result is not None:
                # If login is successful, store the student_id in the session
                session['student_id'] = result[0]
                query = "SELECT * FROM Students WHERE student_id = ?"
                cursor.execute(query, session['student_id'])
                res = cursor.fetchone()
                query = "SELECT * FROM Education WHERE student_id = ?"
                cursor.execute(query, session['student_id'])
                info = cursor.fetchall()
                query = "Select skill from Skills where student_id = ?"
                cursor.execute(query, session['student_id'])
                skills = cursor.fetchall()
                query = "Select * from PersonalDetails where student_id = ?"
                cursor.execute(query, session['student_id'])
                pdetails = cursor.fetchall()
                print(pdetails)
                print(session['student_id'])

                return render_template('resume.html', data=res, info=info, skills=skills, pdetails=pdetails)

            else:
                return "Username and password do not exist!"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return "This page is for student login. Use POST to login."

@app.route('/details', methods=['POST'])
def details():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    id = request.form.get('details')
    print(id)
    conn = connection(server, database)
    cursor = conn.cursor()
    query = "SELECT * FROM Students WHERE student_id = ?"
    cursor.execute(query, id)
    result = cursor.fetchone()
    query = "SELECT * FROM Education WHERE student_id = ?"
    cursor.execute(query, id)
    info = cursor.fetchall()
    query = "Select skill from Skills where student_id = ?"
    cursor.execute(query, id)
    skills = cursor.fetchall()
    query = "Select * from PersonalDetails where student_id = ?"
    cursor.execute(query, id)
    pdetails = cursor.fetchall()
    print(pdetails)
    print(result)
    cursor.close()
    return render_template('comp.html', data=result, info=info, skills=skills, pdetails=pdetails)


@app.route('/add_education', methods=['POST'])
def add_education():
    student_id = session['student_id']
    course_name = request.form.get('course')
    college_name = request.form.get('college')
    graduation_month = request.form.get('graduation_month')
    graduation_year = request.form.get('graduation_year')
    cpi = request.form.get('cpi')
    
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    query = """
    INSERT INTO Education (student_id, course_name, college_name, graduation_month, graduation_year, cpi)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    try:
        cursor.execute(query, student_id, course_name, college_name, graduation_month, graduation_year, cpi)
        conn.commit()

        # Get the newly generated education_id
        new_education_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

        cursor.close()
        conn.close()

        # Return the new_education_id as JSON response
        return jsonify({"new_education_id": new_education_id})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

@app.route('/delete_education', methods=['POST'])
def delete_education():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID not found in session."})

    # Get the education_id from the client-side request JSON data
    data = request.get_json()
    education_id = data.get('education_id')

    if not education_id:
        return jsonify({"error": "Education ID not provided in the request."})

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    try:
        delete_query = """
            DELETE FROM Education
            WHERE student_id = ? AND education_id = ?;
        """

        cursor.execute(delete_query, (student_id, education_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": "Education record deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

@app.route('/get_achievements', methods=['GET'])
def get_achievements():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID not found in session."})

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    try:
        query = """
            SELECT achievement FROM Achievements
            WHERE student_id = ?;
        """
        cursor.execute(query, (student_id,))
        achievements = [{"achievement": row[0]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(achievements)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})


@app.route('/add_achievement', methods=['POST'])
def add_achievement():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID not found in session."})

    data = request.get_json()
    achievement = data.get('achievement')

    if not achievement:
        return jsonify({"error": "Achievement not provided in the request."})

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    try:
        insert_query = """
            INSERT INTO Achievements (student_id, achievement)
            VALUES (?, ?);
        """
        cursor.execute(insert_query, (student_id, achievement))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": "Achievement added successfully"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})
@app.route('/add_skills', methods=['POST'])
def add_skills():
    student_id = session.get('student_id')
    if not student_id:
        return json.dumps({"message": "Student ID not found in session."}), 400

    skills = request.form.get('skills')
    if not skills:
        return json.dumps({"message": "Skills not provided."}), 400

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    try:
        insert_query = """
            INSERT INTO Skills (student_id, skill)
            VALUES (?, ?);
        """
        cursor.execute(insert_query, (student_id, skills))
        conn.commit()
        cursor.close()
        conn.close()
        return json.dumps({"message": "Skills added successfully"}), 200
    except Exception as e:
        return json.dumps({"message": f"An error occurred: {str(e)}"}), 500
@app.route('/delete_skills', methods=['POST'])
def delete_skills():
    student_id = session.get('student_id')
    if not student_id:
        return "Student ID not found in session."

    skills = request.form.get('skills')
    if not skills:
        return "Skills not provided."

    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()

    try:
        delete_query = """
            DELETE FROM Skills
            WHERE student_id = ? AND skill = ?;
        """
        cursor.execute(delete_query, (student_id, skills))
        conn.commit()
        cursor.close()
        conn.close()
        return "Skills deleted successfully"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/filter_results', methods=['POST'])
def filter_results():
    skills = request.form.getlist('skills')
    batch = request.form.getlist('batch')
    job_name = request.form.get('job_name')
    
    
    return "Results page"  

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
            database='tcp_students'
            conn = connection(server, database)
            cursor = conn.cursor()
            sql_query = "SELECT * from Students"
            cursor.execute(sql_query)
            result = cursor.fetchall()
            username = session['student_id']
            sql_query = "SELECT skill from Skills"
            cursor.execute(sql_query)
            skill = cursor.fetchall()
            cursor.close()
            conn.close()
            print(skill)
            return render_template('index.html', data=result, skill=skill)
        else:
            cursor.close()
            conn.close()
            return "Username and password do not exist!"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
'''
@app.route('/add_data', methods=['POST', 'GET'])
def add_data():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    driver = '{ODBC Driver 17 for SQL Server}'
    trusted_connection = 'yes'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection}'
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    student_id = session['student_id']
    full_name = request.form['name']
    print(full_name)
    dob = request.form['dob']
    print(dob)
    email = request.form['email']
    phone_number = request.form['phnum']
    city = request.form['city']
    state = request.form['state']
    career_objective = request.form['ucareerob']
    about_self = request.form['uaboutself']

    # Insert the data into the Students table
    query = """
    MERGE INTO Students AS target
    USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)) AS source (full_name, dob, email, phone_number, city, state, career_objective, about_self, student_id)
    ON target.student_id = source.student_id
    WHEN MATCHED THEN
        UPDATE SET
            target.full_name = source.full_name,
            target.dob = source.dob,
            target.email = source.email,
            target.phone_number = source.phone_number,
            target.city = source.city,
            target.state = source.state,
            target.career_objective = source.career_objective,
            target.about_self = source.about_self
    WHEN NOT MATCHED THEN
        INSERT (full_name, dob, email, phone_number, city, state, career_objective, about_self, student_id)
        VALUES (source.full_name, source.dob, source.email, source.phone_number, source.city, source.state, source.career_objective, source.about_self, source.student_id);
"""
    cursor.execute(query, full_name, dob, email, phone_number, city, state, career_objective, about_self,student_id)
    cnxn.commit()

    # Redirect back to the main page after data insertion
    return redirect('/student')
'''
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get_education_data')
def get_education_data():
    server = 'LAPTOP-EJ54ELJD\MSSQLSERVER01'
    database = 'tcp_students'
    conn = connection(server, database)
    cursor = conn.cursor()
    student_id = session['student_id']
    query = "SELECT * FROM Education WHERE student_id = " +"'"+ student_id +"'"
    cursor.execute(query)
    result = cursor.fetchall()
    column_names = [col[0] for col in cursor.description]

    cursor.close()
    conn.close()

    # Convert the result rows to a list of dictionaries
    education_data = [dict(zip(column_names, row)) for row in result]

    # Convert the data to JSON format
    json_data = json.dumps(education_data)
    return json_data

@app.route('/success')
def success():
    return "Success! Connection established."

@app.route('/error')
def error():
    return "Error! Invalid username or password."

if __name__ == "__main__":
    app.run(debug=True)
