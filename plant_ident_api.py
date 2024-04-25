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
        
        api_keys = ['isHfA6zuJa5VH8K8jXICjeYLb0GsA4RnEfVPf6EAUOjqOGSCk3', 'rqf8HRSDf6EUdKXDpgkGfh6p4PAmTHduywl0Q9yMxbmX2FzL2C']
        url = 'https://plant.id/api/v3/identification'
        
        for api_key in api_keys:
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
                break  # If successful, break out of the loop

        if response.status_code == 201:
            response_json = response.json()
            access_token = response_json.get("access_token")
            url_details = "https://plant.id/api/v3/identification/{}?details=common_names,url,description,taxonomy,image".format(access_token)
            response_details = requests.get(url_details, headers=headers)
            input_image_url = response_details.json().get("input").get("images")[0]
            first_suggestion = response_details.json().get("result").get("classification").get("suggestions")[0]
            first_sugg_details = first_suggestion.get("details")
            first_common_name = first_sugg_details.get("common_names")[0]
            first_sugg_tax = first_sugg_details.get("taxonomy")
            first_sugg_desc = first_sugg_details.get("description")
            first_sugg_similar_image = first_sugg_details.get("image")
            

            
            # Construct the URL of the uploaded image
            image_url = url_for('uploaded_file', filename=filename, _external=True)
            
            # Redirect to the result page with the image URL and names as query parameters
#             return render_template('display_image.html', image_url=input_image_url)
            return render_template('result.html', 
                                   input_image_url=details.get("image", {}).get("value"),
                                   first_common_name=','.join(details.get("common_names", [])),
                                   first_sugg_tax=details.get("taxonomy", {}),
                                   first_sugg_desc=details.get("description", {}).get("value", ""),
                                   first_sugg_similar_image=details.get("image", {}).get("value", ""))
        else:
            return f"Error: {response.status_code} - {response.reason}"

if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=False)


# In[ ]:




