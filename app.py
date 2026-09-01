from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, session, Response
import os
import requests
import json
import csv
import io
import urllib.parse
import re

app = Flask(__name__)
app.secret_key = 'prakash_print_kiosk_secret_key'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STATUS_FILE = 'shop_status.txt'
NOTICE_FILE = 'shop_notice.txt'
SERVICES_FILE = 'services.json'

# ⚠️ आपका गूगल एप्स स्क्रिप्ट URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxhS3RSwbTUv16Q_NE2fyEAt8KNXaDLuM9VcIsCiKfmC7qK7zBxLrcNlTI7efhE541n/exec"

OWNER_UPI_ID = "Q508475385@ybl" 
OWNER_NAME = "BHUARKARKA SERVICES"

DEFAULT_SERVICES = [
    {"id": "print", "title": "SELF PRINT", "service_name": "Self Print", "fee": 0, "emoji": "📄", "note": "इसमें आवेदक JPG, JPEG, PDF जैसी फाइलें upload कर सकता है", "extra_label": "प्रिंट विवरण", "pdf_file": ""},
    {"id": "bonafide", "title": "मूल निवास प्रमाण पत्र", "service_name": "Bonafide Certificate", "fee": 0, "emoji": "📜", "note": "सभी दस्तावेज़ लेकर नजदीकी ई-मित्र पर संपर्क करें।", "extra_label": "विवरण", "pdf_file": "Bonafide-1.pdf"},
    {"id": "caste", "title": "जाति प्रमाण पत्र", "service_name": "Caste Certificate", "fee": 0, "emoji": "📑", "note": "सभी दस्तावेज़ लेकर नजदीकी ई-मित्र पर संपर्क करें।", "extra_label": "विवरण", "pdf_file": "OBC-CASTE.pdf"},
    {"id": "pan", "title": "PAN CARD (₹200)", "service_name": "PAN Card Application", "fee": 200, "emoji": "💳", "note": "आवेदक का आधार कार्ड, 10वीं मार्कशीट जरूरी है।", "extra_label": "आधार नंबर / अन्य जानकारी", "pdf_file": ""},
    {"id": "pvc_aadhar", "title": "PVC AADHAR (₹100)", "service_name": "PVC Aadhar Card", "fee": 100, "emoji": "🪪", "note": "आवश्यक विवरण दर्ज करें।", "extra_label": "आधार नंबर", "pdf_file": ""},
    {"id": "voter", "title": "VOTER CARD (₹100)", "service_name": "Voter Card", "fee": 100, "emoji": "🗳️", "note": "वोटर कार्ड हेतु आवश्यक दस्तावेज अपलोड करें।", "extra_label": "Epic नंबर / विवरण", "pdf_file": ""},
    {"id": "farmer", "title": "FARMER ID (₹100)", "service_name": "Farmer ID", "fee": 100, "emoji": "🌽", "note": "", "extra_label": "किसान आईडी विवरण", "pdf_file": ""},
    {"id": "shramik", "title": "SHRAMIK CARD (₹200)", "service_name": "Shramik Card", "fee": 200, "emoji": "👷", "note": "", "extra_label": "श्रमिक कार्ड विवरण", "pdf_file": ""},
    {"id": "jan_aadhaar", "title": "JAN AADHAAR (₹50)", "service_name": "Jan Aadhar Card", "fee": 50, "emoji": "🆔", "note": "", "extra_label": "जन आधार नंबर", "pdf_file": ""},
    {"id": "jan_aadhaar_pvc", "title": "JAN AADHAAR PVC (₹100)", "service_name": "Jan Aadhar PVC Card", "fee": 100, "emoji": "🪪", "note": "", "extra_label": "जन आधार नंबर", "pdf_file": ""},
    {"id": "ayushman", "title": "AYUSHMAN CARD (₹100)", "service_name": "Ayushman Card", "fee": 100, "emoji": "🏥", "note": "", "extra_label": "आयुष्मान कार्ड विवरण", "pdf_file": ""}
]

def get_services():
    try:
        res = requests.get(GOOGLE_SCRIPT_URL + "?action=get_services", timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                return data
    except Exception as e:
        print(f"Sheet fetch error, using local/default: {e}")
    
    # लोकल फॉಲ್‌बैक
    if not os.path.exists(SERVICES_FILE):
        with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SERVICES, f, ensure_ascii=False, indent=4)
        return DEFAULT_SERVICES
    try:
        with open(SERVICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_SERVICES

def get_shop_status():
    if not os.path.exists(STATUS_FILE):
        return True
    with open(STATUS_FILE, 'r') as f:
        return f.read().strip() == 'ON'

def set_shop_status(status):
    with open(STATUS_FILE, 'w') as f:
        f.write('ON' if status else 'OFF')

def get_shop_notice():
    if not os.path.exists(NOTICE_FILE):
        return "🙏 BHUARKARKA SERVICES में आपका स्वागत है! सभी प्रकार के ऑनलाइन फॉर्म व प्रिंटिंग यहाँ उपलब्ध हैं।"
    with open(NOTICE_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def set_shop_notice(notice):
    with open(NOTICE_FILE, 'w', encoding='utf-8') as f:
        f.write(notice)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    clean_req_name = urllib.parse.unquote(filename).strip()
    file_path_uploads = os.path.join(app.config['UPLOAD_FOLDER'], clean_req_name)
    if os.path.exists(file_path_uploads):
        return send_from_directory(app.config['UPLOAD_FOLDER'], clean_req_name, as_attachment=clean_req_name.lower().endswith('.pdf'))
    return f'''
    <div style="text-align:center; font-family:Arial; margin-top:50px;">
        <h3 style="color:#c0392b;">⚠️ फाइल सर्वर पर नहीं मिली</h3>
        <p>मांगी गई फाइल <b>"{clean_req_name}"</b> उपलब्ध नहीं है।</p>
        <a href="/" style="padding:8px 15px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">🔙 होम पेज पर जाएं</a>
    </div>
    ''', 404

@app.route('/kiosk-image/<path:filename>')
def kiosk_image(filename):
    if os.path.exists(os.path.join('uploads', filename)):
        return send_from_directory('uploads', filename)
    elif os.path.exists(filename):
        return send_from_directory('.', filename)
    return redirect(url_for('home'))

HTML_HOME = """
<!DOCTYPE html>
<html>
<head>
    <title>BHUARKARKA SERVICES - स्मार्ट कियोस्क</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('/kiosk-image/bc.jpg') no-repeat center center fixed; background-size: cover; padding: 20px; text-align: center; min-height: 100vh; }
        .container { max-width: 800px; margin: auto; }
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
                <span class="status-dot-offline"></span> दुकान बंद है (OFFLINE - फॉर्म चालू हैं)
            {% endif %}
        </div>
        <p style="color: #fff; margin-bottom: 20px; font-weight: bold;">कृपया अपनी सेवा चुनें:</p>
        <div class="app-grid">
            {% for card in dynamic_services %}
            <a href="/service/{{ card.id }}" class="app-icon-card">
                <div class="emoji">{{ card.emoji }}</div>
                <div class="title-text">{{ card.title }}</div>
            </a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <title>BHUARKARKA - एडमिन पैनल</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #2c3e50; color: #fff; padding: 15px; margin: 0; }
        .container { max-width: 1050px; margin: auto; }
        h2 { text-align: center; color: #f1c40f; }
        .card { background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .btn { display: inline-block; padding: 6px 12px; background: #27ae60; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; border: none; cursor: pointer; margin: 3px 2px; font-size: 12px; }
        .btn-danger { background: #c0392b; }
        .btn-info { background: #2980b9; }
        .btn-warning { background: #d35400; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background: #fff; color: #333; border-radius: 5px; overflow: hidden; }
        th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        th { background: #2980b9; color: white; }
        textarea, input[type="text"], input[type="number"], input[type="file"] { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-top: 4px; margin-bottom: 10px; box-sizing: border-box; background: white; color: #333; }
        .download-section { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 15px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media(max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛡️ BHUARKARKA SERVICES - ADMIN PANEL 🛡️</h2>
        
        <div class="card">
            <h3>🎛️ दुकान का स्टेटस:</h3>
            {% if is_online %}
                <p style="color: #2ecc71; font-weight: bold;">स्थिति: खुली है (ONLINE)</p>
                <a href="/admin/toggle-status" class="btn btn-danger">🔴 इसे बंद (OFFLINE) दिखाएं</a>
            {% else %}
                <p style="color: #e74c3c; font-weight: bold;">स्थिति: बंद है (OFFLINE)</p>
                <a href="/admin/toggle-status" class="btn">🟢 इसे चालू (ONLINE) दिखाएं</a>
            {% endif %}
        </div>

        <div class="card">
            <h3>📢 होमपेज नोटिस अपडेट करें:</h3>
            <form method="POST" action="/admin/update-notice">
                <textarea name="notice">{{ notice }}</textarea>
                <button type="submit" class="btn btn-info" style="margin-top: 8px; padding: 8px 15px;">💾 नोट सेव करें</button>
            </form>
        </div>

        <div class="card">
            <h3>➕ नया सर्विस कार्ड जोड़ें (Add New Card):</h3>
            <form method="POST" action="/admin/add-service" enctype="multipart/form-data">
                <div class="form-grid">
                    <div>
                        <label>इमोजी (Emoji):</label>
                        <input type="text" name="emoji" placeholder="जैसे: 💳, 🪪" required>
                    </div>
                    <div>
                        <label>कार्ड टाइटल (होमपेज हेतु):</label>
                        <input type="text" name="title" placeholder="जैसे: E-SHRAM CARD (₹100)" required>
                    </div>
                    <div>
                        <label>सर्विस नाम:</label>
                        <input type="text" name="service_name" placeholder="जैसे: E-Shram Card Application" required>
                    </div>
                    <div>
                        <label>फीस राशि (₹):</label>
                        <input type="number" name="fee" value="0" placeholder="0 यदि फ्री है">
                    </div>
                </div>
                <label>निर्देश / नोट:</label>
                <input type="text" name="note" placeholder="जैसे: आधार कार्ड अनिवार्य है">
                
                <label>अतिरिक्त फील्ड लेबल:</label>
                <input type="text" name="extra_label" placeholder="जैसे: आधार नंबर" required>

                <label>📁 फॉर्म/PDF अपलोड करें (ऐच्छिक):</label>
                <input type="file" name="pdf_file" accept=".pdf,.jpg,.jpeg,.png">

                <button type="submit" class="btn" style="padding: 10px 18px; font-size: 14px; margin-top: 5px;">✨ नया कार्ड जोड़ें</button>
            </form>

            <h4 style="margin-top:20px; color:#f1c40f;">📋 मौजूदा सर्विस कार्ड्स (कुल: {{ dynamic_services|length }}):</h4>
            <div style="overflow-x: auto;">
                <table>
                    <tr>
                        <th>इमोजी</th>
                        <th>टाइटल</th>
                        <th>फीस</th>
                        <th>इनपुट लेबल</th>
                        <th>फाइल</th>
                        <th>एक्शन</th>
                    </tr>
                    {% for card in dynamic_services %}
                    <tr>
                        <td>{{ card.emoji }}</td>
                        <td><b>{{ card.title }}</b></td>
                        <td>₹{{ card.fee }}</td>
                        <td>{{ card.extra_label }}</td>
                        <td>{{ card.pdf_file if card.pdf_file else 'कोई नहीं' }}</td>
                        <td style="white-space: nowrap;">
                            <a href="/admin/edit-service/{{ card.id }}" class="btn btn-warning">✏️ एडिट</a>
                            <a href="/admin/delete-service/{{ card.id }}" class="btn btn-danger" onclick="return confirm('डिलीट करना चाहते हैं?');">🗑️ डिलीट</a>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <div class="card" style="text-align: center;">
            <h3>📥 एक्सेल रिपोर्ट डाउनलोड करें</h3>
            <div class="download-section">
                <a href="/admin/download/New" class="btn btn-info">📄 नए आवेदन डाउनलोड</a>
                <a href="/admin/download/Accepted" class="btn btn-warning">📑 मंजूर आवेदन</a>
                <a href="/admin/download/Completed" class="btn">✅ पूर्ण कार्य</a>
            </div>
        </div>

        <div class="card">
            <h3>⏳ ग्राहक पेंडिंग रिक्वेस्ट (New)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <tr>
                        <th>नाम</th>
                        <th>मोबाइल</th>
                        <th>सेवा</th>
                        <th>फीस / UTR</th>
                        <th>फाइलें</th>
                        <th>स्टेटस</th>
                        <th>एक्शन</th>
                    </tr>
                    {% if requests_list %}
                        {% for i in range(requests_list|length) %}
                        <tr>
                            <td>{{ requests_list[i][0] }}</td>
                            <td>{{ requests_list[i][1] }}</td>
                            <td>{{ requests_list[i][3] }}</td>
                            <td><b>₹{{ requests_list[i][4] }}</b><br><small>UTR: {{ requests_list[i][7] if requests_list[i]|length > 7 else 'N/A' }}</small></td>
                            <td>{{ requests_list[i][5] | safe }}</td>
                            <td>{{ requests_list[i][6] }}</td>
                            <td><a href="/admin/move/New/Accepted/{{ i }}" class="btn btn-warning">👉 मंजूर करें</a></td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="7" style="text-align:center;">कोई नई रिक्वेस्ट नहीं है।</td></tr>
                    {% endif %}
                </table>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/admin/logout" class="btn btn-danger" style="padding: 10px 20px;">🔒 LOGOUT</a>
        </div>
    </div>
</body>
</html>
"""

HTML_EDIT_CARD = """
<!DOCTYPE html>
<html>
<head>
    <title>सर्विस एडिट करें</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #2c3e50; color: #fff; padding: 20px; }
        .card { max-width: 500px; margin: auto; background: #34495e; padding: 20px; border-radius: 8px; }
        input[type="text"], input[type="number"], input[type="file"] { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-top: 4px; margin-bottom: 12px; background: white; color: #333; box-sizing: border-box; }
        .btn { padding: 10px 18px; background: #27ae60; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #f1c40f; margin-top:0;">✏️ सर्विस कार्ड एडिट करें</h2>
        <form method="POST" enctype="multipart/form-data">
            <label>इमोजी:</label>
            <input type="text" name="emoji" value="{{ card.emoji }}" required>
            <label>कार्ड टाइटल:</label>
            <input type="text" name="title" value="{{ card.title }}" required>
            <label>सर्विस नाम:</label>
            <input type="text" name="service_name" value="{{ card.service_name }}" required>
            <label>फीस (₹):</label>
            <input type="number" name="fee" value="{{ card.fee }}">
            <label>निर्देश / नोट:</label>
            <input type="text" name="note" value="{{ card.note }}">
            <label>अतिरिक्त फील्ड लेबल:</label>
            <input type="text" name="extra_label" value="{{ card.extra_label }}" required>
            <label>📁 नई फाइल बदलें (ऐच्छिक):</label>
            <input type="file" name="pdf_file" accept=".pdf,.jpg,.jpeg,.png">
            <button type="submit" class="btn">💾 अपडेट व सेव करें</button>
            <a href="/admin-panel" style="color:white; margin-left:15px; text-decoration:none;">रद्द करें</a>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_HOME, is_online=get_shop_status(), notice=get_shop_notice(), dynamic_services=get_services())

@app.route('/service/<service_id>')
def service_page(service_id):
    if service_id == 'print':
        return render_template_string('''
        <!DOCTYPE html>
        <html><head><title>SELF PRINT</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial; background:#f4f4f4; padding:20px; text-align:center;">
            <div style="max-width:400px; margin:auto; background:white; padding:20px; border-radius:10px; text-align:left;">
                <h2 style="color:#2c3e50; text-align:center;">📄 SELF PRINT</h2>
                <form action="/submit-service" method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="service_type" value="Self Print">
                    <input type="hidden" name="amount" value="0">
                    <label><b>नाम:</b></label><input type="text" name="cust_name" style="width:100%; padding:8px; margin:5px 0 10px 0;" required>
                    <label><b>मोबाइल नंबर:</b></label><input type="text" name="cust_mobile" style="width:100%; padding:8px; margin:5px 0 10px 0;" required>
                    <input type="hidden" name="cust_email" value="NA">
                    <label><b>दस्तावेज़ चुनें:</b></label><input type="file" name="files" multiple required style="width:100%; margin:5px 0 15px 0;">
                    <button type="submit" style="width:100%; padding:10px; background:#28a745; color:white; border:none; font-weight:bold; border-radius:5px;">🚀 भेजें</button>
                </form>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#007BFF;">⬅️ होम पेज</a>
            </div>
        </body></html>
        ''')

    services = get_services()
    target_card = next((c for c in services if c['id'] == service_id), None)
    if not target_card:
        return redirect(url_for('home'))
        
    s_title = target_card['service_name']
    try:
        s_fee = int(target_card.get('fee', 0))
    except:
        s_fee = 0
    is_paid = s_fee > 0

    note_html = f'<div style="background: #eef9ff; border: 1px solid #bce8f1; padding: 10px; border-radius: 5px; font-size: 13px; margin-bottom: 12px; color: #31708f;"><b>📌 निर्देश:</b> {target_card.get("note")}</div>' if target_card.get('note') else ''
    file_html = f'<a href="/uploads/{target_card.get("pdf_file")}" target="_blank" style="display:block; background:#2980b9; color:white; text-align:center; padding:10px; font-weight:bold; border-radius:5px; text-decoration:none; margin-bottom:15px;">📥 फॉर्म डाउनलोड करें</a>' if target_card.get('pdf_file') else ''

    payment_section = f'''
    <hr style="border:0; border-top:1px dashed #ddd; margin:15px 0;">
    <div style="text-align:center;">
        <p style="font-size:13px; font-weight:bold; color:#555;">QR कोड स्कैन करके ₹{s_fee} भुगतान करें:</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=upi://pay?pa={OWNER_UPI_ID}&pn={OWNER_NAME}&am={s_fee}&cu=INR" style="border:1px solid #ddd; padding:5px; background:white;">
    </div>
    <label><b>UTR नंबर दर्ज करें:</b></label>
    <input type="text" name="utr_number" placeholder="जैसे: 4321xxxxxxxx" required style="background:#fffde7; font-weight:bold;">
    ''' if is_paid else '<input type="hidden" name="utr_number" value="FREE">'

    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head><title>{s_title}</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial; background:#f4f4f4; padding:20px; text-align:center;">
        <div style="max-width:440px; margin:auto; background:white; padding:20px; border-radius:10px; text-align:left; box-shadow:0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color:#2c3e50; text-align:center; margin-top:0;">{s_title}</h2>
            {note_html} {file_html}
            <form action="/pay-and-submit" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="{s_title}">
                <input type="hidden" name="amount" value="{s_fee}">
                <label><b>पूरा नाम:</b></label><input type="text" name="cust_name" required style="width:100%; padding:8px; margin:5px 0;">
                <label><b>मोबाइल नंबर:</b></label><input type="text" name="cust_mobile" required style="width:100%; padding:8px; margin:5px 0;">
                <label><b>ईमेल:</b></label><input type="text" name="cust_email" required style="width:100%; padding:8px; margin:5px 0;">
                <label><b>{target_card.get('extra_label', 'विवरण')}:</b></label><input type="text" name="extra_info" required style="width:100%; padding:8px; margin:5px 0;">
                <label><b>दस्तावेज अपलोड करें:</b></label><input type="file" name="files" multiple required style="width:100%; margin:5px 0 10px 0;">
                {payment_section}
                <button type="submit" style="width:100%; padding:10px; background:#28a745; color:white; border:none; font-weight:bold; border-radius:5px; margin-top:10px; cursor:pointer;">🚀 फॉर्म सबमिट करें</button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:15px; color:#007BFF; text-decoration:none;">⬅️ होम पेज</a>
        </div>
    </body></html>
    ''')

@app.route('/submit-service', methods=['POST'])
@app.route('/pay-and-submit', methods=['POST'])
def submit_service():
    try:
        service_type = request.form.get('service_type', 'General')
        amount = request.form.get('amount', '0')
        cust_name = request.form.get('cust_name', 'ग्राहक')
        cust_mobile = request.form.get('cust_mobile', 'N/A')
        cust_email = request.form.get('cust_email', 'N/A')
        extra_info = request.form.get('extra_info', '')
        utr_number = request.form.get('utr_number', 'FREE')
        
        uploaded_files = []
        for file in request.files.getlist('files'):
            if file and file.filename != '':
                clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_name))
                uploaded_files.append(clean_name)
                
        filenames_str = ", ".join(uploaded_files) if uploaded_files else 'कोई फाइल नहीं'
        if extra_info:
            filenames_str = f"विवरण: {extra_info} | फाइलें: {filenames_str}" if filenames_str != 'कोई फाइल नहीं' else f"विवरण: {extra_info}"

        payload = {
            "sheetName": "New",
            "cust_name": cust_name, "cust_mobile": cust_mobile, "cust_email": cust_email,
            "service_type": service_type, "amount": amount, "filenames": filenames_str,
            "status": "Pending", "utr": utr_number
        }
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        return '<div style="text-align:center; font-family:Arial; margin-top:50px;"><h2>✅ आवेदन सफलतापूर्वक जमा हो गया!</h2><a href="/">होम पेज जाएं</a></div>'
    except Exception as e:
        return f"एरर: {e}"

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('logged_in'):
        if request.method == 'POST':
            if request.form.get('password') == '7610':
                session['logged_in'] = True
                return redirect(url_for('admin_panel'))
            return '<script>alert("गलत पासवर्ड!"); window.location="/admin-panel";</script>'
        return '<body style="background:#2c3e50; color:white; font-family:Arial; text-align:center; padding-top:100px;"><h2>🔐 ADMIN LOGIN</h2><form method="POST"><input type="password" name="password" placeholder="पासवर्ड" style="padding:10px; text-align:center;" required><br><br><button type="submit" style="padding:10px 20px; background:#27ae60; color:white; border:none;">LOGIN</button></form></body>'
    
    requests_list, accepted_list = [], []
    try:
        r1 = requests.get(GOOGLE_SCRIPT_URL + "?action=get_data&sheetName=New", timeout=5)
        if r1.status_code == 200: requests_list = r1.json()
        r2 = requests.get(GOOGLE_SCRIPT_URL + "?action=get_data&sheetName=Accepted", timeout=5)
        if r2.status_code == 200: accepted_list = r2.json()
    except:
        pass

    return render_template_string(HTML_ADMIN, is_online=get_shop_status(), notice=get_shop_notice(), requests_list=requests_list, dynamic_services=get_services())

@app.route('/admin/add-service', methods=['POST'])
def add_service():
    if session.get('logged_in'):
        title = request.form.get('title')
        service_name = request.form.get('service_name')
        fee = int(request.form.get('fee', 0) or 0)
        emoji = request.form.get('emoji', '📄')
        note = request.form.get('note', '')
        extra_label = request.form.get('extra_label', 'विवरण')
        
        pdf_filename = ""
        file = request.files.get('pdf_file')
        if file and file.filename != '':
            pdf_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

        payload = {
            "action": "add_service",
            "title": title, "service_name": service_name, "fee": fee,
            "emoji": emoji, "note": note, "extra_label": extra_label, "pdf_file": pdf_filename
        }
        try:
            requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        except Exception as e:
            print(f"Add Service Error: {e}")
            
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit-service/<card_id>', methods=['GET', 'POST'])
def edit_service(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_panel'))
    services = get_services()
    target_card = next((c for c in services if c['id'] == card_id), None)
    if not target_card:
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        target_card['title'] = request.form.get('title')
        target_card['service_name'] = request.form.get('service_name')
        target_card['fee'] = int(request.form.get('fee', 0) or 0)
        target_card['emoji'] = request.form.get('emoji', '📄')
        target_card['note'] = request.form.get('note', '')
        target_card['extra_label'] = request.form.get('extra_label', 'विवरण')
        
        file = request.files.get('pdf_file')
        if file and file.filename != '':
            clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_name))
            target_card['pdf_file'] = clean_name

        payload = {"action": "edit_service", **target_card}
        try:
            requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        except:
            pass
        return redirect(url_for('admin_panel'))

    return render_template_string(HTML_EDIT_CARD, card=target_card)

@app.route('/admin/delete-service/<card_id>')
def delete_service(card_id):
    if session.get('logged_in'):
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={"action": "delete_service", "id": card_id}, timeout=10)
        except:
            pass
    return redirect(url_for('admin_panel'))

@app.route('/admin/move/<source_sheet>/<target_sheet>/<int:row_index>')
def move_row(source_sheet, target_sheet, row_index):
    if session.get('logged_in'):
        try:
            requests.post(GOOGLE_SCRIPT_URL, json={"action": "moveRow", "sourceSheet": source_sheet, "targetSheet": target_sheet, "rowIndex": row_index}, timeout=10)
        except:
            pass
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle-status')
def toggle_status():
    if session.get('logged_in'): set_shop_status(not get_shop_status())
    return redirect(url_for('admin_panel'))

@app.route('/admin/update-notice', methods=['POST'])
def update_notice():
    if session.get('logged_in'): set_shop_notice(request.form.get('notice', ''))
    return redirect(url_for('admin_panel'))

@app.route('/admin/download/<sheet_name>')
def download_report(sheet_name):
    if not session.get('logged_in'): return redirect(url_for('admin_panel'))
    try:
        res = requests.get(GOOGLE_SCRIPT_URL + f"?action=get_data&sheetName={sheet_name}", timeout=5)
        data = res.json() if res.status_code == 200 else []
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Mobile', 'Email', 'Service', 'Amount', 'Files', 'Status', 'UTR'])
        for row in data: writer.writerow(row)
        output.seek(0)
        return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={sheet_name}_Report.csv"})
    except Exception as e:
        return f"Download Error: {e}"

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
