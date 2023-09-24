from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from werkzeug.utils import secure_filename  # Import secure_filename
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'student'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    stud_id = request.form['stud_id']
    stud_name = request.form['stud_name']
    stud_gender = request.form['stud_gender']
    stud_IC = request.form['stud_ic']
    stud_email = request.form['stud_mail']
    stud_HP = request.form['stud_phone']
    stud_currAddress = request.form['stud_currAddress']
    stud_homeAddress = request.form['stud_homeAddress']
    stud_programme = request.form['stud_program']
    stud_image_file = request.files['stud_image_file']
    stud_pwd = request.form['password']
    stud_cgpa = request.form['stud_cgpa']
    lec_email = request.form['lec_email']
    com_email = request.form['com_email']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if stud_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (stud_id, stud_name, stud_gender, stud_IC, stud_email, stud_HP, stud_currAddress, stud_homeAddress, stud_programme, stud_image_file, stud_pwd, stud_cgpa, lec_email, com_email))
        db_conn.commit()

        # Securely generate a unique filename for the resume
        updated_resume_filename = secure_filename(stud_image_file.filename)

        # Uplaod image file in S3
        stud_image_file_name_in_s3 = "stud-id-" + str(stud_id) + "_pdf/" + updated_resume_filename
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading pdf to S3...")
            s3.Bucket(custombucket).put_object(Key=stud_image_file_name_in_s3, Body=stud_image_file, ContentType='application/pdf')
            object_url = f"https://{custombucket}.s3.amazonaws.com/{stud_image_file_name_in_s3}"
        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('appStudOutput.html', name=stud_name, object_url=object_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
