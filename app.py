# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for,session
from bs4 import BeautifulSoup
import requests
import csv
import re
import pandas as pd 
import json 
import os
from flask_login import login_required, logout_user,LoginManager
import csv
import PyPDF2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import smtplib







app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'


# Set a secret key
app.config['SECRET_KEY'] = '123'
# Initialize a list to store job data
job_data = []
saved_jobs = []

# Home page
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Registration form
@app.route('/sign_up')
def registration_form():
    return render_template('sign_up.html')

# Handle registration form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('n')
    email = request.form.get('el')
    password = request.form.get('cpsw')
    
    # Save data to a CSV file (you can replace 'registration.csv' with your desired filename)
    with open('registration.csv', mode='a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, password])
    
    return redirect(url_for('login_form'))

# Main page
@app.route('/main')
def main_page():
    return render_template('main.html')

# # Login page
# @app.route('/login')
# def login_form():
#     return render_template('login.html')

@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

# # Handle the form submission and authenticate the user
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('text')
#     password = request.form.get('password')

#     # Add your authentication logic here
#     # If authentication is successful, set the user's session

#     if username == 'text' and password == 'password':
#         session['username'] = username
#         return redirect(url_for('profile'))
#     else:
#         return 'Login failed'

# # Check login credentials
# @app.route('/check_login', methods=['POST'])
# def check_login():
#     username = request.form.get('n')
#     password = request.form.get('psw')
    
#     # Check the CSV file for the given username and password
#     with open('registration.csv', mode='r', newline='') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             if row[0] == username and row[2] == password:  # Check username and password
#                 return redirect(url_for('main_page'))  # Redirect to job listings after successful login
    
#     return redirect(url_for('login_form'))

@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form.get('n')
    password = request.form.get('psw')

    # Check the CSV file for the given username and password
    with open('registration.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[2] == password:  # Check username and password
                session['username'] = username  # Store the username in the session
                return redirect(url_for('main_page'))  # Redirect to a logged-in page after successful login

    return redirect(url_for('login_form'))

# def scrape_jobs():
#     try:
#         from bs4 import BeautifulSoup
#         import requests

#         response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")

#         page = response1.text

#         #Parse the HTML content
#         soup = BeautifulSoup(page, "html.parser")
        
#         #Find all span elements with class "wrap-title seo_title"
#         job_tags = soup.find_all(name="span", class_="wrap-title seo_title")

#         education_tags = soup.find_all(name="span",class_="bold_elig")

#         # Find all elements with class "loctext"
#         location_tags = soup.find_all(name="span", class_="job-location display-block modal-open job-details-span")

#         experieince_tags = soup.find_all(name="span",class_="experience job-details-span")

#         # Initialize a list to store the scraped job data
#         job_data = []

#         min_length = min(len(job_tags), len(education_tags), len(experieince_tags), len(location_tags))

#         for i in range(len(job_tags)):
#             job_title = job_tags[i].getText()
#             education_criteria = education_tags[i].getText() if i < len(education_tags) else "N/A"
#             experience=experieince_tags[i].getText() if i < len(experieince_tags) else "N/A"
#             location = location_tags[i].find_parent().find(class_="bold_font").get_text() if i < len(location_tags) else "N/A"

#             job_data.append({
#                 'title': job_title,
#                 'education': education_criteria,
#                 'experience':experience,
#                 'location': location,
#             })


#         with open('job.json', 'w') as json_file:
#             # for item in job_data:
#             #     json_string = json.dumps(item)
#             #     json_file.write(json_string + '\n')
#             json.dump(job_data, json_file)

#         return job_data

        

#     except requests.exceptions.RequestException as e:
#         # Handle network-related errors
#         print("Request Exception:", e)
#         return []

#     except Exception as e:
#         # Handle other exceptions
#         print("An error occurred:", e)
#         return []

def scrape_jobs():
    try:
        from bs4 import BeautifulSoup
        import requests

        response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
        page = response1.text

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser")

        # Find all span elements with class "wrap-title seo_title"
        job_tags = soup.find_all(name="span", class_="wrap-title seo_title")

        education_tags = soup.find_all(name="span", class_="bold_elig")

        # Find all elements with class "loctext"
        location_tags = soup.find_all(name="span", class_="job-location display-block modal-open job-details-span")

        experieince_tags = soup.find_all(name="span", class_="experience job-details-span")

        # Initialize a list to store the scraped job data
        job_data = []

        # Determine the minimum length among the tag lists
        min_length = min(len(job_tags), len(education_tags), len(experieince_tags), len(location_tags))

        for i in range(min_length):
            job_title = job_tags[i].get_text() if job_tags and job_tags[i] else "N/A"
            education_criteria = education_tags[i].get_text() if education_tags and education_tags[i] else "N/A"
            experience = experieince_tags[i].get_text() if experieince_tags and experieince_tags[i] else "N/A"

            location_tag = location_tags[i] if location_tags else None
            location = "N/A"
            if location_tag:
                parent = location_tag.find_parent()
                bold_font = parent.find(class_="bold_font")
                if bold_font:
                    location = bold_font.get_text()

            job_data.append({
                'title': job_title,
                'education': education_criteria,
                'experience': experience,
                'location': location,
            })

        with open('job.json', 'w') as json_file:
            json.dump(job_data, json_file)

        return job_data

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print("Request Exception:", e)
        return []

    except Exception as e:
        # Handle other exceptions
        print("An error occurred:", e)
        return []

 



@app.route('/save_job', methods=['POST'])
def save_job():
    title = request.form.get('title')
    education=request.form.get('education')
    experience=request.form.get('experience')
    location = request.form.get('location')

    json_file = 'saved_jobs.json'

# Open the file in a context manager to ensure it's properly closed
    with open(json_file, mode='r+') as file:
    # Load existing data, if any
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []

    # Append the new job data
    data.append({'title': title, 'education': education, 'experience': experience, 'location': location})

# Write the updated data back to the JSON file (outside the 'with' block)
    with open(json_file, mode='w') as file:
        json.dump(data, file, indent=4)

    return redirect(url_for('job_listings'))


@app.route('/job_listings')
def job_listings():
    global job_data  

    # Check if job_data is empty, if so, scrape the data
    if not job_data:
        job_data = scrape_jobs()

    return render_template('index.html', job_data=job_data)


@app.route('/saved')
def saved():
    json_file = 'saved_jobs.json'
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []  # If the file doesn't exist or is empty

    return render_template('saved_jobs.html', jobs=data)

@app.route('/search', methods=['POST'])
def search_jobs():
    global job_data  # Declare job_data as a global variable

    search_query = request.form.get('search_query')

    if search_query:
        search_query = search_query.lower()  # Convert to lowercase for case-insensitive search

       
        if not job_data:
            job_data = scrape_jobs()

        # Filter jobs that have an exact match with the search query in any field
        search_results = [job for job in job_data if
                          search_query in job['title'].lower() or
                          search_query in job['education'].lower() or
                          search_query in job['experience'].lower() or
                          search_query in job['location'].lower()]

    else:
        search_results = []  

    return render_template('search_job.html', search_results=search_results)


def secure_filename(filename):
    # Remove any path information and keep only the filename
    filename = os.path.basename(filename)
    
    # Replace any non-alphanumeric characters with underscores
    filename = re.sub(r"[^a-zA-Z0-9.]", "_", filename)
    
    return filename

# @app.route('/profile')
# def profile():
#     # Retrieve user details, e.g., username, from your database
    
#     username = "Charmi "
#     email="charmi@gmail.com"
    
#     return render_template('profile.html', username=username,email=email)


# def set_current_user(username):
#     session['current_user'] = username

# # Function to retrieve the currently logged-in user
# def get_current_user():
#     return session.get('current_user', None)

# @app.route('/login', methods=['POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('text')  # Retrieve the username from a form field

#         if username:
#             # Set the currently logged-in user
#             set_current_user(username)
#             return f'Logged in as {username}'
#         else:
#             return 'Please provide a username in the form.'


# @app.route('/profile')
# def profile():
#     if 'username' in session:
#         username = session['username']
#         # Retrieve the user's profile and render the template
#         return render_template('profile.html', username=username)
#     else:
#         return 'Not logged in'

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        email = get_email_for_username(username)  # Function to retrieve the email

        if email:
            return render_template('profile.html', username=username, email=email)
        else:
            return 'Email not found for the user.'
    else:
        return 'Not logged in'

# Function to retrieve the email for a given username
def get_email_for_username(username):
    with open('registration.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return row[1]  # Email is in the second column (index 1) in the CSV
    return None  # Return None if email is not found
# Initialize the LoginManager


login_manager = LoginManager()
login_manager.init_app(app)

# Set the login view (the view that users are redirected to when they need to log in)
login_manager.login_view = '/login'  # Replace 'login' with the name of your login route

import csv

@login_manager.user_loader
def load_user(user_id):
    # Open the CSV file for reading
    with open('registration.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Search for a user with a matching username (user_id)
        for row in reader:
            if row['username'] == user_id:
                # You can create a User object or return the user data as a dictionary
                # Example: return User(username=row['username'], email=row['email'])
                return row

    # Return None if the user does not exist
    return None

# Logout route
@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('homepage'))

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic.filename != '' and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('profile'))
    return "Invalid file or upload failed."

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' in request.files:
        resume = request.files['resume']
    if resume.filename != '':
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    return render_template('main.html')

@app.route('/display_profile')
def display():
    return redirect(url_for('display_profile_pic.html'))

recommended_job_data = []



def generate_recommended_jobs():
    # Open the PDF file
    with open("uploads/resume.pdf", 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)  # Use PdfFileReader instead of PdfReader
    
    # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:  # Loop through pages directly
            text += page.extract_text()


    # Initialize a list to store recommended job listings
    recommended_jobs = []

    # Load job listings from job.json
    with open('job.json', 'r') as job_file:
        job_listings = json.load(job_file)

    # Match job_keywords with the extracted text and store in resume_keywords
    resume_keywords = []
    job_keywords = ["QA", "Content", "Full Stack", "Fullstack", "C", "Android", "Java", "Software", "Front-End",
                    "Technical", "Application", "Medical", "Customer", "Automation", "Business", "Finance"]

    for keyword in job_keywords:
        if keyword in text:
            resume_keywords.append(keyword)

    # Loop through the job listings and check if any keywords from `resume_keywords` are present in the job title
    for job in job_listings:
        title = job["title"]
        for keyword in resume_keywords:
            if keyword.lower() in title.lower():
                recommended_jobs.append(job)

    # Define the JSON file path to save recommended jobs
    json_file_path = 'recommended_jobs.json'

    # Save the recommended jobs to the JSON file
    if recommended_jobs:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(recommended_jobs, json_file, indent=4)

        print(f"Recommended jobs have been saved to {json_file_path}.")
    else:
        print("No recommended jobs found.")

    num_jobs = len(recommended_jobs)

    print(f"Number of recommended jobs in {json_file_path}: {num_jobs}")

    return recommended_jobs

# Example usage:
# recommended_job_data = generate_recommended_jobs('uploads/resume.pdf')

# Your existing code for scraping recommended jobs, extracting text from resumes, and matching keywords should be placed here

@app.route('/recommended_job_list')
def recommended_job_list():
    global recommended_job_data

    # Check if recommended_job_data is empty, if so, generate the recommended job data
    if not recommended_job_data:
        recommended_job_data = generate_recommended_jobs()  # Replace with your recommended job generation logic

    return render_template('recommended_jobs.html', recommended_job_data=recommended_job_data)

@app.route('/mail', methods=['POST'])
def mail():
    if 'username' in session:
        username = session['username']
        email = get_email_for_username(username)  # Get the email for the logged-in user
    else:
        return "User not logged in"

    smtp_port = 587
    smtp_server = "smtp.gmail.com"
    my_email = "shrestybohra1211@gmail.com"
    password = "mxkiqozrfhgvyqtr"

    from_email = my_email  # Set the "From" email address to your email

    # Ensure the 'uploads' directory exists
    uploads_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    attachment_path = None  # Initialize attachment path to None

    # Initialize the 'connection' variable outside the try block
    connection = None

    if 'attachment' in request.files:
        attachment = request.files['attachment']
        if attachment.filename != '':
            attachment_path = os.path.join(uploads_dir, attachment.filename)
            attachment.save(attachment_path)

    # Define a fixed subject
    subject = "Profile updated successfully"

    simple_email_context = ssl.create_default_context()  # Define simple_email_context

    # Define the 'message' variable as a MIMEMultipart object
    message = MIMEMultipart()

    # Define the message content
    full_message = f"Dear {username},\n\nWe are pleased to inform you that your profile on Job Finder has been successfully updated. Your profile now reflects the latest information and improvements you've made. This will enhance your chances of finding the perfect opportunity\n\nThank you for keeping your profile up to date. If you have any further updates or need any assistance, please don't hesitate to reach out.\n\nBest regards,\n[JOB FINDER]"


    # Set the message content in the email
    message.attach(MIMEText(full_message, "plain"))

    # ... your existing code ...

    try:
        connection = smtplib.SMTP(smtp_server, smtp_port)
        connection.starttls(context=simple_email_context)
        connection.login(my_email, password)
        connection.sendmail(my_email, [email], message.as_string())  # Use 'email' instead of 'to_email'
    except Exception as e:
        return f"Error sending email: {str(e)}"
    finally:
        if connection is not None:
            connection.quit()

    # If an attachment was added, remove the file
    if attachment_path and os.path.exists(attachment_path):

        os.remove(attachment_path)
    return render_template('profile.html')
    

if __name__ == '__main__':
    app.run(debug=True)
