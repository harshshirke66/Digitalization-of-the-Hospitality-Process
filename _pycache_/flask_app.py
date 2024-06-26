import os
import pandas as pd
from flask import Flask, request, redirect, url_for, render_template, flash

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'group_file' not in request.files or 'hostel_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    group_file = request.files['group_file']
    hostel_file = request.files['hostel_file']

    if group_file.filename == '' or hostel_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if group_file and allowed_file(group_file.filename) and hostel_file and allowed_file(hostel_file.filename):
        group_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'group_file.csv')
        hostel_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'hostel_file.csv')
        group_file.save(group_file_path)
        hostel_file.save(hostel_file_path)
        
        # Process the files and allocate rooms
        result = allocate_rooms(group_file_path, hostel_file_path)
        
        return render_template('index.html', result=result)

    flash('Invalid file format')
    return redirect(request.url)

def allocate_rooms(group_file_path, hostel_file_path):
    # Read the CSV files
    groups = pd.read_csv(group_file_path)
    hostels = pd.read_csv(hostel_file_path)
    
    allocation = []

    for hostel in hostels.itertuples():
        hostel_capacity = hostel.Capacity
        hostel_gender = hostel.Gender
        
        # Select students based on gender and availability
        allocated_students = groups[(groups['Gender'] == hostel_gender)].head(hostel_capacity)
        
        allocation.append({
            'Hostel': hostel.HostelName,
            'Allocated': allocated_students.to_dict('records')
        })
        
        # Remove allocated students from the group
        groups = groups[~groups['StudentID'].isin(allocated_students['StudentID'])]

    return allocation

if __name__ == '__main__':
    app.run()
