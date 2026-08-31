from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
import requests
import json

app = Flask(__name__)
app.secret_key = 'prakash_print_kiosk_secret_key'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STATUS_FILE = 'shop_status.txt'
NOTICE_FILE = 'shop_notice.txt'

# --- Google Apps Script Web App URL ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxFyfYjTV3F5MWDHKZLKQTop6sUP4-msknhe96aJPOKJsPWxw7JtCwtIrp3HOelC_9tOA/exec"

def get_shop_status():
    if not os.path.exists(STATUS_FILE):
        return True
    with open(STATUS_FILE, 'r') as f:
        return f.read().strip() == 'ON'

def get_shop_notice():
    if not os.path.exists(NOTICE_FILE):
        return "🙏 BHUARKARKA SERVICES में आपका स्वागत है! सभी प्रकार के ऑनलाइन फॉर्म व प्रिंटिंग यहाँ उपलब्ध हैं।"
    with open(NOTICE_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if filename.lower().endswith('.pdf'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/kiosk-image/<path:filename>')
def kiosk_image(filename):
    return send_from_directory('uploads', filename)

HTML_HOME = '''
<!DOCTYPE html>
<html>
<head>
    <title>BHUARKARKA SERVICES - स्मार्ट कियोस्क</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('/kiosk-image/bc.jpg') no-repeat center center fixed; 
            background-size: cover; 
            padding: 20px; 
            text-align: center; 
            min-height: 100vh;
        }
        .container { max-width: 600px; margin: auto; }
        h1 { font-family: 'Britannic Bold', Arial, sans-serif; color: white; text-shadow: 2px 2px 6px rgba(0,0,0,0.8); margin-bottom: 10px; }
        .notice-banner { background: rgba(255, 193, 7, 0.95); color: #333; padding: 10px 15px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 1px dashed #d39e00; }
        .shop-status { display: inline-flex; align-items: center; background: rgba(0, 0, 0, 0.75); padding: 8px 16px; border-radius: 30px; color: white; font-weight: bold; font-size: 14px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2); }
        .status-dot-online { height: 12px; width: 12px; background-color: #28a745; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #28a745; }
        .status-dot-offline { height: 12px; width: 12px; background-color: #d9534f; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #d9534f; }
        .app-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }
        .app-icon-card { background: rgba(255, 255, 255, 0.95); width: 130px; height: 130px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; color: #333; transition: transform 0.2s; border: 2px solid #ddd; }
        .app-icon-card:hover { transform: scale(1.08); border-color: #28a745; }
        .emoji { font-size: 35px; margin-bottom: 6px; }
        .title-text { font-family: 'Britannic Bold', Arial, sans-serif; font-size: 11px; text-align: center; padding: 0 4px; color: #2c3e50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖨️ BHUARKARKA SERVICES 🙏</h1>
        <div class="notice-banner">📢 {{ notice }}</div>
        <div class="shop-status">
            {% if is_online %}
                <span class="status-dot-online"></span> दुकान खुली है (ONLINE)
            {% else %}
                <span class="status-dot-offline"></span> दुकान बंद है (OFFLINE)
            {% endif %}
        </div>
        <p style="color: #fff; margin-bottom: 20px; font-weight: bold;">कृपया अपनी सेवा चुनें:</p>
        <div class="app-grid">
            <a href="/service/print" class="app-icon-card"><div class="emoji">📄</div><div class="title-text">SELF PRINT</div></a>
            <a href="/service/pan" class="app-icon-card"><div class="emoji">💳</div><div class="title-text">PAN CARD</div></a>
            <a href="/service/pvc_aadhar" class="app-icon-card"><div class="emoji">🪪</div><div class="title-text">PVC AADHAR</div></a>
            <a href="/service/bonafide" class="app-icon-card"><div class="emoji">📜</div><div class="title-text">मूल निवास</div></a>
            <a href="/service/caste" class="app-icon-card"><div class="emoji">📑</div><div class="title-text">जाति प्रमाण पत्र</div></a>
            <a href="/service/farmer" class="app-icon-card"><div class="emoji">🌽</div><div class="title-text">FARMER ID</div></a>
            <a href="/service/shramik" class="app-icon-card"><div class="emoji">👷</div><div class="title-text">SHRAMIK CARD</div></a>
            <a href="/service/jan_aadhaar" class="app-icon-card"><div class="emoji">🆔</div><div class="title-text">JAN AADHAAR</div></a>
            <a href="/service/ayushman" class="app-icon-card"><div class="emoji">🏥</div><div class="title-text">AYUSHMAN CARD</div></a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_HOME, is_online=get_shop_status(), notice=get_shop_notice())

@app.route('/service/<service_name>')
def service_page(service_name):
    # यहाँ आपकी सर्विस के फॉर्म रेंडर होंगे
    return redirect(url_for('home'))

@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        service_type = request.form.get('service_type', 'General')
        cust_name = request.form.get('cust_name', 'सामान्य ग्राहक')
        cust_mobile = request.form.get('cust_mobile', 'लागू नहीं')
        cust_email = request.form.get('cust_email', 'लागू नहीं')
        amount = request.form.get('amount', '0')
        filenames = request.form.get('filenames', 'कोई फाइल नहीं')
        
        # गूगल शीट पर डेटा भेजने के लिए पेलोड
        payload = {
            "sheetName": "New",
            "cust_name": cust_name,
            "cust_mobile": cust_mobile,
            "cust_email": cust_email,
            "service_type": service_type,
            "amount": amount,
            "filenames": filenames,
            "status": "Pending (पेंडिंग)"
        }

        # गूगल एप्स स्क्रिप्ट को डेटा भेजना
        requests.post(GOOGLE_SCRIPT_URL, json=payload)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.95); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#28a745; font-family:'Britannic Bold', Arial, sans-serif;">✅ REQUEST SUBMITTED!</h2>
                <p style="font-size:16px;">आपका डेटा सफलतापर्वूक ऑनलाइन गूगल शीट में दर्ज हो गया है।</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">HOME PAGE</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/'>वापस जाएं</a>"

@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
