from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime

app = Flask(__name__)

cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def generate_request_id():
    return str(uuid.uuid4())

def get_current_time():
    return datetime.now().isoformat()

##homepage
@app.route('/', methods = ['GET', 'POST'])
def homepage():
    return render_template('homepage.html')

##tenantrequestpage
@app.route('/request', methods=['GET', 'POST'])
def tenantrequestpage():
    if request.method == 'POST':
        try:
            request_id = generate_request_id()
            current_time = get_current_time()

            request_data = {
                'request_id': request_id,
                'apartment_number': request.form.get('aptNum'),
                'area': request.form.get('problemArea'),
                'description': request.form.get('desc'),
                'timestamp': current_time,
                'status': 'pending'
            }

            db.collection('maintenance_requests').document(request_id).set(request_data)
            return redirect(url_for('homepage'))  # Redirect after successful POST
        except Exception as e:
            print("Error:", e)  # Logging the error

    return render_template('tenantrequestpage.html')

##staffpage
@app.route('/view_requests', methods=['GET', 'POST'])
def staffpage():
    if request.method == 'POST':
        db.collection('maintenance_requests').document(request.form['mReqs']).update({'status': 'complete'})

    requests = db.collection('maintenance_requests').stream()
    data = [doc.to_dict() for doc in requests]
    return render_template('staffpage.html', data=data)

##managementpage
@app.route('/management', methods = ['GET', 'POST'])
def managementpage():
    return render_template('managementpage.html')

##managementaddpage
@app.route('/management_add', methods = ['GET', 'POST'])
def managementaddpage():
    if request.method == 'POST':
        try:
            tenantId = generate_request_id()
            currentTime = get_current_time()

            tenantData = {
                'tenantId': tenantId,
                'tenantName': request.form.get('name'),
                'phoneNum': request.form.get('phoneNum'),
                'email': request.form.get('email'),
                'apartment_number': request.form.get('aptNum'),
                'checkin': request.form.get('dateOfCheckIn'),
                'checkout': request.form.get('dateOfCheckOut')
            }

            db.collection('tenants').document(tenantId).set(tenantData)
            return redirect(url_for('managementpage'))  # Redirect after successful POST
        except Exception as e:
            print("Error:", e)  # Logging the error

    return render_template('managementaddpage.html')

##managementmovepage
@app.route('/management_move', methods = ['GET', 'POST'])
def managementmovepage():
    if request.method == 'POST':
        db.collection('tenants').document(request.form['tenants']).update({'apartment_number': request.form['apartmentNum']})
        return redirect(url_for('managementpage'))

    requests = db.collection('tenants').stream()
    data = [doc.to_dict() for doc in requests]
    return render_template('managementmovepage.html', data=data)

##managementdeletepage
@app.route('/management_delete', methods = ['GET', 'POST'])
def managementdeletepage():
    if request.method == 'POST':
        db.collection('tenants').document(request.form['tenants']).delete()
        return redirect(url_for('managementpage'))

    requests = db.collection('tenants').stream()
    data = [doc.to_dict() for doc in requests]
    return render_template('managementdeletepage.html', data=data)

if __name__ == '__main__':
    app.run()