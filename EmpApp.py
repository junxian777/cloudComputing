from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from werkzeug.utils import secure_filename

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
    


    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s ,%s, %s ,%s)"
    cursor = db_conn.cursor()

    # Check if an updated resume file was uploaded
    if 'stud_image_file' in request.files:
        updated_resume = request.files['stud_image_file']

        # Check if the file has a filename
        if updated_resume.filename != '':
            # Get the file extension (e.g., ".pdf", ".doc", ".docx")
            file_extension = os.path.splitext(updated_resume.filename)[1]

            # Check if the file extension is allowed (PDF, DOC, DOCX, etc.)
            allowed_extensions = ['.pdf', '.doc', '.docx']  # Add more extensions as needed
            if file_extension.lower() not in allowed_extensions:
                return "File type not allowed. Please upload a PDF, DOC, or DOCX file."

            # Securely generate a unique filename for the resume
            updated_resume_filename = secure_filename(updated_resume.filename)

            # Determine the content type based on the file extension
            content_type = "application/pdf"  # Default to PDF
            if file_extension.lower() == '.doc':
                content_type = "application/msword"
            elif file_extension.lower() == '.docx':
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            # Upload the resume to S3 with the appropriate content type
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(custombucket).put_object(
                    Key=updated_resume_filename,
                    Body=updated_resume,
                    ContentType=content_type
                )

                # Construct the URL to the uploaded resume
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])
                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location
                updated_resume_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_resume_filename}"
            except Exception as e:
                return str(e)
            finally:
                cursor.close()
        else:
            # Handle the case where the file has no filename
            updated_resume_url = None
    else:
        updated_resume_url = updated_resume_url

        print("all modification done...")
        return render_template('appStudOutput.html', name=stud_name)
        #return to xinyi

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

