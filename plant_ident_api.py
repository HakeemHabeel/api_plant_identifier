#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import requests
import base64
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        url = 'https://plant.id/api/v3/identification'
        api_key = 'isHfA6zuJa5VH8K8jXICjeYLb0GsA4RnEfVPf6EAUOjqOGSCk3'
        headers = {
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        request_data = {
            "images": base64_image,
            "latitude": 49.207,
            "longitude": 16.608,
            "similar_images": True
        }
        
        response = requests.post(url, headers=headers, json=request_data)
        
        if response.status_code == 201:
            response_json = response.json()
            result = response_json.get('result', {})
            classification = result.get('classification', {})
            suggestions = classification.get('suggestions', [])
            
            names = [suggestion.get('name', 'Unknown') for suggestion in suggestions]
            
            # Save the uploaded file with a secure filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Construct the URL of the uploaded image
            image_url = url_for('uploaded_file', filename=filename, _external=True)
            
            # Redirect to the result page with the image URL and names as query parameters
            return redirect(url_for('show_result', image_url=image_url, names=names))
        else:
            return f"Error: {response.status_code} - {response.reason}"

@app.route('/result')
def show_result():
    # Retrieve the image URL and names from the query parameters
    image_url = request.args.get('image_url', '')
    names = request.args.get('names', '').split(',')  # Split the names string into a list
    
    return render_template('result.html', image_url=image_url, names=names)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=False)


# In[ ]:




