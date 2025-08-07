import os
import numpy as np
import cv2
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from tensorflow.keras.models import load_model
from django.conf import settings
from dotenv import load_dotenv
from datetime import datetime
from .models import users, results_collection	
from .forms import SignupForm, LoginForm
from pymongo import MongoClient
import uuid
from bson import ObjectId


# Load environment variables
load_dotenv()

# Load Keras model
model = load_model(os.path.join(os.path.dirname(__file__), '../ml_model/pneumonia_model.keras'))
CLASS_NAMES = ['INVALID', 'NORMAL', 'PNEUMONIA']

# MongoDB client (Atlas still used)
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database(os.getenv("MONGO_DB"))

# Directory to save images locally
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Views

def index_view(request):
    return render(request, 'client/index.html')


def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        name = form.cleaned_data['name']
        password = form.cleaned_data['password']

        if users.find_one({'username': username}):
            messages.error(request, 'Username already taken.')
        elif users.find_one({'email': email}):
            messages.error(request, 'Email already registered.')
        else:
            users.insert_one({
                'name': name,
                'username': username,
                'email': email,
                'phone': phone,
                'password': password,
                'invalid_attempts': 0
            })
            messages.success(request, 'Signup successful. Please log in.')
            return redirect('login')
    return render(request, 'client/signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = users.find_one({
            'username': form.cleaned_data['username'],
            'password': form.cleaned_data['password']
        })
        if user:
            request.session['user_id'] = str(user['_id'])
            request.session['username'] = user['username']
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'client/login.html', {'form': form})

def dashboard_view(request):
    username = request.session.get('username')

    if request.method == 'POST' and request.FILES.get('xray'):
        xray_file = request.FILES['xray']
        result = "Invalid image"
        prob = "N/A"
        local_filename = None

        try:
            file_bytes = xray_file.read()

            # Save file locally
            unique_filename = f"{uuid.uuid4()}_{xray_file.name}"
            local_path = os.path.join(UPLOAD_DIR, unique_filename)
            with open(local_path, 'wb') as f:
                f.write(file_bytes)

            # Convert to OpenCV image
            nparr = np.frombuffer(file_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_cv is None or len(img_cv.shape) < 2:
                raise ValueError("Invalid image")

            # Resize and preprocess
            img_resized = cv2.resize(img_cv, (150, 150))
            img_normalized = img_resized.astype('float32') / 255.0
            img_array = np.expand_dims(img_normalized, axis=0)

            # Predict using trained model (3 classes)
            prediction = model.predict(img_array)  # Shape: (1, 3)
            class_index = np.argmax(prediction[0])
            confidence = round(100 * float(prediction[0][class_index]), 2)

            class_labels = ['INVALID', 'NORMAL', 'PNEUMONIA']
            result = class_labels[class_index]
            prob = confidence
            local_filename = unique_filename

        except Exception as e:
            print(f"[Error] {e}")
            users.update_one({"username": username}, {"$inc": {"invalid_attempts": 1}})

        # Save result to MongoDB
        results_collection.insert_one({
            "username": username,
            "result": result,
            "confidence": float(prob) if prob != "N/A" else None,
            "upload_time": datetime.now(),
            "filename": local_filename
        })

        user = users.find_one({'username': username})
        invalid_count = user.get('invalid_attempts', 0)

        return render(request, 'client/dashboard.html', {
            'username': username,
            'result': result,
            'prob': prob,
            'image_filename': local_filename if result != "Invalid image" else None,
            'invalid_count': invalid_count
        })

    return render(request, 'client/dashboard.html', {
        'username': username
    })


def get_image(request, filename):
    image_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    return HttpResponse("Image not found", status=404)


def logout_view(request):
    request.session.flush()
    return redirect('index')

#=============================admin views======================================
def admin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
            request.session['admin'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials.')
    return render(request, 'admin/login.html')

from datetime import datetime

def admin_dashboard(request):
    if not request.session.get('admin'):
        return redirect('admin_view')

    query = {}

    # Optional filters
    username = request.GET.get('username')
    if username:
        query['username'] = username

    date = request.GET.get('date')
    if date:
        try:
            date_obj = datetime.strptime(date, '%d-%m-%Y')
            start = datetime(date_obj.day, date_obj.month, date_obj.year)
            end = datetime(date_obj.day, date_obj.month, date_obj.year, 23, 59, 59)
            query['upload_time'] = {'$gte': start, '$lte': end}
        except ValueError:
            pass  # Skip if date format is invalid

    # Fetch results
    results = list(results_collection.find(query).sort('upload_time', -1))

    for r in results:
        r['id'] = str(r.get('_id'))
        r['upload_time'] = r.get('upload_time').strftime('%d-%m-%Y %H:%M:%S') if r.get('upload_time') else 'N/A'
        r['username'] = r.get('username', 'Unknown')
        r['result'] = r.get('result', 'N/A')
        r['confidence'] = r.get('confidence', 0.0)

    return render(request, 'admin/dashboard.html', {'results': results})





#users information 

from django.shortcuts import render, redirect
from django.contrib import messages
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Setup
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client['pneumoniaDB']
users_collection = db['users']
results_collection = db['results']

def manage_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('delete_user_id')
        if user_id:
            try:
                users_collection.delete_one({'_id': ObjectId(user_id)})
                messages.success(request, 'User deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('manage_users')

    user_list = []
    for user in users_collection.find():
        user_id = str(user['_id'])
        user['id'] = user_id  # For use in form hidden input

        username = user.get('username')
        user_results = results_collection.find({'username': username})  # Join by username

        user['result'] = list(user_results)  # Attach results list
        user_list.append(user)

    return render(request, 'admin/manage_users.html', {'users': user_list})

    
#-------------------------------------------------


def delete_result(request, id):
    if request.method == "POST":
        try:
            # Correct collection: results_collection, not users
            result = results_collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 1:
                return redirect('admin_dashboard')
            else:
                return HttpResponse("Result not found.", status=404)
        except Exception as e:
            return HttpResponse(f"Error deleting result: {e}", status=500)
    return HttpResponse("Invalid request method.", status=405)

  
   