from flask import Flask, request, jsonify, abort, send_from_directory
import csv
import os
from dotenv import load_dotenv
from functools import wraps
import jwt
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from flask_cors import CORS

# load .env file if present (allows specifying MONGO_URI, USE_MONGO, etc.)
load_dotenv()

USE_MONGO = os.getenv('USE_MONGO', 'false').lower() in ('1', 'true', 'yes')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)

# CSV file path (used when USE_MONGO is false)
data_file = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'events.csv')
users_file = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'users.csv')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ---------- User CSV helpers ----------
def read_users_csv():
    users = []
    if not os.path.exists(users_file):
        return users
    try:
        with open(users_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['id'] = int(row['id'])
                users.append(row)
    except:
        return []
    return users

def write_users_csv(users):
    fieldnames = ['id', 'email', 'password', 'name', 'title', 'role', 'avatar']
    with open(users_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow(user)

# ---------- Authentication helpers ----------
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(401, 'Token is missing')
        if token.startswith('Bearer '):
            token = token[7:]
        user_id = verify_token(token)
        if not user_id:
            abort(401, 'Token is invalid')
        return f(user_id, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(401, 'Token is missing')
        if token.startswith('Bearer '):
            token = token[7:]
        user_id = verify_token(token)
        if not user_id:
            abort(401, 'Token is invalid')
        
        # Check if user is admin
        users = read_users_csv()
        user = next((u for u in users if int(u['id']) == user_id), None)
        if not user or user.get('role') != 'admin':
            abort(403, 'Admin access required')
        
        return f(user_id, *args, **kwargs)
    return decorated

def send_verification_email(email, code):
    """Send verification code via email"""
    # If email credentials are not configured or are placeholder values, just log for development
    if (not SMTP_USERNAME or not SMTP_PASSWORD or
        SMTP_USERNAME == 'your-email@gmail.com' or
        SMTP_PASSWORD == 'your-app-password'):
        print(f"📧 [DEV MODE] Verification code for {email}: {code}")
        print("Configure SMTP credentials in .env file for production email sending")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = 'EventHub - Email Verification Code'

        body = f"""
        Welcome to EventHub!

        Your verification code is: {code}

        This code will expire in 10 minutes.

        If you didn't request this code, please ignore this email.

        Best regards,
        EventHub Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# ---------- CSV helpers ----------
def read_events_csv():
    events = []
    if not os.path.exists(data_file):
        return events
    with open(data_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            events.append(row)
    return events


def write_events_csv(events):
    fieldnames = ['id', 'title', 'description', 'date']
    with open(data_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ev in events:
            writer.writerow(ev)

# ---------- MongoDB helpers ----------
if USE_MONGO:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI)
    db = client.get_database('eventhub')
    events_col = db.get_collection('events')

    def read_events_mongo():
        docs = list(events_col.find({}, {'_id': 0}))
        # ensure id is int
        for d in docs:
            if 'id' in d:
                d['id'] = int(d['id'])
        return docs

    def create_event_mongo(body):
        # body expected to contain title/date/description
        # determine next id by max existing
        max_doc = events_col.find_one(sort=[('id', -1)])
        next_id = (max_doc['id'] if max_doc and 'id' in max_doc else 0) + 1
        new_event = {
            'id': next_id,
            'title': body.get('title', ''),
            'description': body.get('description', ''),
            'date': body.get('date', ''),
        }
        events_col.insert_one(new_event)
        return new_event

    def update_event_mongo(event_id, body):
        update = {}
        for key in ('title', 'description', 'date'):
            if key in body:
                update[key] = body[key]
        if not update:
            return None
        result = events_col.find_one_and_update({'id': event_id}, {'$set': update}, return_document=True, projection={'_id': 0})
        return result

    def delete_event_mongo(event_id):
        res = events_col.delete_one({'id': event_id})
        return res.deleted_count > 0

# ---------- unified routing ----------
def read_events():
    return read_events_mongo() if USE_MONGO else read_events_csv()

def create_event_data(body):
    return create_event_mongo(body) if USE_MONGO else _create_event_csv(body)

def _create_event_csv(body):
    events = read_events_csv()
    next_id = max((ev['id'] for ev in events), default=0) + 1
    new_event = {
        'id': next_id,
        'title': body.get('title', ''),
        'description': body.get('description', ''),
        'date': body.get('date', ''),
    }
    events.append(new_event)
    write_events_csv(events)
    return new_event

def update_event_data(event_id, body):
    if USE_MONGO:
        return update_event_mongo(event_id, body)
    events = read_events_csv()
    for ev in events:
        if ev['id'] == event_id:
            ev['title'] = body.get('title', ev['title'])
            ev['description'] = body.get('description', ev['description'])
            ev['date'] = body.get('date', ev['date'])
            write_events_csv(events)
            return ev
    return None

def delete_event_data(event_id):
    if USE_MONGO:
        return delete_event_mongo(event_id)
    events = read_events_csv()
    filtered = [ev for ev in events if ev['id'] != event_id]
    if len(filtered) == len(events):
        return False
    write_events_csv(filtered)
    return True

# ---------- Root route for frontend ----------
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

# ---------- Authentication routes ----------
@app.route('/send-verification', methods=['POST'])
def send_verification():
    data = request.get_json()
    if not data or 'email' not in data:
        abort(400, 'Email is required')

    email = data['email']

    # Basic email validation
    if not '@' in email or not '.' in email:
        abort(400, 'Invalid email format')

    # Generate verification code
    code = ''.join(random.choices(string.digits, k=6))

    # In a real app, you'd store this in a database with expiration
    # For now, we'll return it in the response for testing
    # In production, you'd store it securely and only send via email

    if send_verification_email(email, code):
        return jsonify({'message': 'Verification code sent', 'code': code})  # Remove 'code' in production
    else:
        abort(500, 'Failed to send email')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        abort(400, 'Email and password required')

    email = data['email']
    password = data['password']

    # Check against users.csv
    users = read_users_csv()
    user = next((u for u in users if u['email'] == email and u['password'] == password), None)
    
    if user:
        token = generate_token(user['id'])
        return jsonify({
            'token': token,
            'user': {
                'id': int(user['id']),
                'email': user['email'],
                'name': user['name'],
                'role': user.get('role', 'user'),
                'title': user.get('title', ''),
                'avatar': user.get('avatar', '')
            }
        })
    else:
        abort(401, 'Invalid credentials')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['email', 'password', 'first_name', 'last_name']
    
    if not data or not all(field in data for field in required_fields):
        abort(400, 'Missing required fields')

    email = data['email']
    password = data['password']
    first_name = data['first_name']
    last_name = data['last_name']
    
    # Check if email already exists
    users = read_users_csv()
    if any(u['email'] == email for u in users):
        abort(409, 'Email already exists')
    
    # Create new user
    new_id = max((int(u['id']) for u in users), default=0) + 1
    full_name = f'{first_name} {last_name}'
    avatar = (first_name[0] + last_name[0]).upper()
    
    new_user = {
        'id': new_id,
        'email': email,
        'password': password,
        'name': full_name,
        'title': 'New Member',
        'role': 'user',
        'avatar': avatar
    }
    
    users.append(new_user)
    write_users_csv(users)
    
    # Generate token and return
    token = generate_token(new_id)
    return jsonify({
        'token': token,
        'user': {
            'id': new_id,
            'email': email,
            'name': full_name,
            'role': 'user',
            'title': 'New Member',
            'avatar': avatar
        }
    }), 201

@app.route('/users', methods=['GET'])
@admin_required
def list_users(current_user_id):
    users = read_users_csv()
    # Return all user data for admin (including passwords for management)
    return jsonify(users)

@app.route('/users/download', methods=['GET'])
@admin_required
def download_users(current_user_id):
    users = read_users_csv()
    
    # Create CSV content
    import io
    output = io.StringIO()
    if users:
        fieldnames = users[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    csv_content = output.getvalue()
    output.close()
    
    # Return as downloadable file
    from flask import Response
    response = Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=users_data.csv',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )
    return response

@app.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    users = read_users_csv()
    user = next((u for u in users if int(u['id']) == user_id), None)
    if not user:
        abort(404, 'User not found')
    
    # Check if user is admin or accessing their own profile
    current_user = next((u for u in users if int(u['id']) == current_user_id), None)
    is_admin = current_user and current_user.get('role') == 'admin'
    
    if not is_admin and current_user_id != user_id:
        abort(403, 'Not authorized to view this user')
    
    # Return full data for admin, limited data for regular users
    if is_admin:
        user_data = dict(user)  # Full data including password
    else:
        user_data = {k: v for k, v in user.items() if k != 'password'}  # No password for regular users
    
    user_data['id'] = int(user_data['id'])
    return jsonify(user_data)

@app.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user_id, user_id):
    users = read_users_csv()
    current_user = next((u for u in users if int(u['id']) == current_user_id), None)
    is_admin = current_user and current_user.get('role') == 'admin'
    
    # Only allow updating own profile or admin updating others
    if not is_admin and current_user_id != user_id:
        abort(403, 'Not authorized to update this user')
    
    data = request.get_json() or {}
    user = next((u for u in users if int(u['id']) == user_id), None)
    if not user:
        abort(404, 'User not found')
    
    # Update allowed fields (admins can update more fields)
    if is_admin:
        updatable_fields = ['name', 'title', 'avatar', 'email', 'role']
    else:
        updatable_fields = ['name', 'title', 'avatar']
    
    for field in updatable_fields:
        if field in data:
            user[field] = data[field]
    
    write_users_csv(users)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    user_data['id'] = int(user_data['id'])
    return jsonify(user_data)

# ---------- Protected event routes ----------
@app.route('/events', methods=['GET'])
@token_required
def get_events(user_id):
    return jsonify(read_events())

@app.route('/events', methods=['POST'])
@token_required
def create_event(user_id):
    body = request.get_json()
    if not body or 'title' not in body or 'date' not in body:
        abort(400, 'missing title or date')
    new_ev = create_event_data(body)
    return jsonify(new_ev), 201

@app.route('/events/<int:event_id>', methods=['PUT'])
@token_required
def update_event(user_id, event_id):
    body = request.get_json() or {}
    updated = update_event_data(event_id, body)
    if updated is None:
        abort(404)
    return jsonify(updated)

@app.route('/events/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(user_id, event_id):
    ok = delete_event_data(event_id)
    if not ok:
        abort(404)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
