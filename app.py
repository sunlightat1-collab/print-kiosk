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

# ⚠️ गूगल एप्स स्क्रिप्ट URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyCc_unuXdvpBqCieHmjYi-XPpPe5fw96Z4IjdBsGxYKmbPuhdO-Oa0u01mkjmUM9NUcw/exec"

# 🟢 आपकी UPI आईडी
OWNER_UPI_ID = "Q508475385@ybl" 
OWNER_NAME = "BHUARKARKA SERVICES"

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
    
    # 1. सीधा सर्च
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], clean_req_name)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], clean_req_name, as_attachment=clean_req_name.lower().endswith('.pdf'))
    
    # 2. स्पेस को अंडरस्कोर से बदलकर सर्च
    alt_name1 = clean_req_name.replace(' ', '_')
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], alt_name1)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], alt_name1, as_attachment=alt_name1.lower().endswith('.pdf'))

    # 3. यदि नाम कौमा/स्पेस से टूटा हुआ है तो UPLOAD फोल्डर में सबसे नजदीकी फाइल ढूंढना
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files_in_dir = os.listdir(app.config['UPLOAD_FOLDER'])
        req_slug = re.sub(r'[^a-zA-Z0-9]', '', clean_req_name.lower())
        
        if len(req_slug) > 3:
            for existing_file in files_in_dir:
                file_slug = re.sub(r'[^a-zA-Z0-9]', '', existing_file.lower())
                if req_slug in file_slug or file_slug in req_slug:
                    return send_from_directory(app.config['UPLOAD_FOLDER'], existing_file, as_attachment=existing_file.lower().endswith('.pdf'))

    return f'''
    <div style="text-align:center; font-family:Arial; margin-top:50px;">
        <h3 style="color:#c0392b;">⚠️ फाइल सर्वर पर नहीं मिली</h3>
        <p>मांगी गई फाइल <b>"{clean_req_name}"</b> अपलोड फोल्डर में उपलब्ध नहीं है।</p>
        <a href="/admin-panel" style="padding:8px 15px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">🔙 एडमिन पैनल पर लौटें</a>
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
                <span class="status-dot-offline"></span> दुकान बंद है (OFFLINE - फॉर्म चालू हैं)
            {% endif %}
        </div>
        <p style="color: #fff; margin-bottom: 20px; font-weight: bold;">कृपया अपनी सेवा चुनें:</p>
        <div class="app-grid">
            <a href="/service/print" class="app-icon-card"><div class="emoji">📄</div><div class="title-text">SELF PRINT</div></a>
            <a href="/service/pan" class="app-icon-card"><div class="emoji">💳</div><div class="title-text">PAN CARD (₹200)</div></a>
            <a href="/service/pvc_aadhar" class="app-icon-card"><div class="emoji">🪪</div><div class="title-text">PVC AADHAR (₹100)</div></a>
            <a href="/service/voter" class="app-icon-card"><div class="emoji">🗳️</div><div class="title-text">VOTER CARD (₹100)</div></a>
            <a href="/service/bonafide" class="app-icon-card"><div class="emoji">📜</div><div class="title-text">मूल निवास प्रमाण पत्र</div></a>
            <a href="/service/caste" class="app-icon-card"><div class="emoji">📑</div><div class="title-text">जाति प्रमाण पत्र</div></a>
            <a href="/service/farmer" class="app-icon-card"><div class="emoji">🌽</div><div class="title-text">FARMER ID (₹100)</div></a>
            <a href="/service/shramik" class="app-icon-card"><div class="emoji">👷</div><div class="title-text">SHRAMIK CARD (₹200)</div></a>
            <a href="/service/jan_aadhaar" class="app-icon-card"><div class="emoji">🆔</div><div class="title-text">JAN AADHAAR (₹50)</div></a>
            <a href="/service/jan_aadhaar_pvc" class="app-icon-card"><div class="emoji">🪪</div><div class="title-text">JAN AADHAAR PVC (₹100)</div></a>
            <a href="/service/ayushman" class="app-icon-card"><div class="emoji">🏥</div><div class="title-text">AYUSHMAN CARD (₹100)</div></a>
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
        .container { max-width: 900px; margin: auto; }
        h2 { text-align: center; color: #f1c40f; }
        .card { background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .btn { display: inline-block; padding: 6px 12px; background: #27ae60; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; border: none; cursor: pointer; margin: 3px 2px; font-size: 12px; }
        .btn-danger { background: #c0392b; }
        .btn-info { background: #2980b9; }
        .btn-warning { background: #d35400; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background: #fff; color: #333; border-radius: 5px; overflow: hidden; }
        th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        th { background: #2980b9; color: white; }
        textarea { width: 100%; height: 60px; padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-top: 5px; box-sizing: border-box; }
        .download-section { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛡️ BHUARKARKA SERVICES - ADMIN PANEL 🛡️</h2>
        
        <div class="card">
            <h3>🎛️ दुकान का स्टेटस (Indicator):</h3>
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
                <button type="submit" class="btn btn-info" style="margin-top: 8px; padding: 8px 15px;">💾 नोट सेव करें व लाइव करें</button>
            </form>
        </div>

        <div class="card" style="text-align: center;">
            <h3>📥 एक्सेल रिपोर्ट डाउनलोड करें</h3>
            <div class="download-section">
                <a href="/admin/download/New" class="btn btn-info">📄 नए आवेदन डाउनलोड करें</a>
                <a href="/admin/download/Accepted" class="btn btn-warning">📑 मंजूर आवेदन डाउनलोड करें</a>
                <a href="/admin/download/Completed" class="btn">✅ पूर्ण कार्य डाउनलोड करें</a>
            </div>
        </div>

        <div class="card">
            <h3>⏳ ग्राहक पेंडिंग रिक्वेस्ट (New / Sheet 1)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <tr>
                        <th>नाम</th>
                        <th>मोबाइल</th>
                        <th>सेवा</th>
                        <th>फीस / UTR</th>
                        <th>फाइलें / विवरण</th>
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
                            <td>{{ requests_list[i][5] | render_file_links | safe }}</td>
                            <td>{{ requests_list[i][6] }}</td>
                            <td>
                                <a href="/admin/move/New/Accepted/{{ i }}" class="btn btn-warning">👉 मंजूर करें</a>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="7" style="text-align:center;">अभी कोई नई सर्विस रिक्वेस्ट नहीं है।</td></tr>
                    {% endif %}
                </table>
            </div>
        </div>

        <div class="card">
            <h3>📑 मंजूर किए गए आवेदन (Accepted / Sheet 2)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <tr>
                        <th>नाम</th>
                        <th>मोबाइल</th>
                        <th>सेवा</th>
                        <th>फीस / UTR</th>
                        <th>फाइलें / विवरण</th>
                        <th>स्टेटस</th>
                        <th>एक्शन</th>
                    </tr>
                    {% if accepted_list %}
                        {% for i in range(accepted_list|length) %}
                        <tr>
                            <td>{{ accepted_list[i][0] }}</td>
                            <td>{{ accepted_list[i][1] }}</td>
                            <td>{{ accepted_list[i][3] }}</td>
                            <td><b>₹{{ accepted_list[i][4] }}</b></td>
                            <td>{{ accepted_list[i][5] | render_file_links | safe }}</td>
                            <td>{{ accepted_list[i][6] }}</td>
                            <td>
                                <a href="/admin/move/Accepted/Completed/{{ i }}" class="btn">✅ पूर्ण करें</a>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="7" style="text-align:center;">कोई मंजूर किया गया आवेदन नहीं है।</td></tr>
                    {% endif %}
                </table>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/admin/logout" class="btn btn-danger" style="padding: 10px 20px; font-size: 15px;">🔒 LOGOUT</a>
        </div>
    </div>
    <script>
        setTimeout(function(){ location.reload(); }, 5000);
    </script>
</body>
</html>
"""

@app.template_filter('render_file_links')
def render_file_links(file_text):
    if not file_text or file_text == 'कोई फाइल नहीं' or 'ई-मित्र' in file_text:
        return file_text
    
    extra_prefix = ""
    target_files = file_text
    if " | फाइलें: " in file_text:
        parts = file_text.split(" | फाइलें: ")
        extra_prefix = f"<div style='margin-bottom:4px;'><b>{parts[0]}</b></div>"
        target_files = parts[1]
    
    items = [x.strip() for x in target_files.split(',') if x.strip()]
    
    html_out = extra_prefix
    for fname in items:
        encoded_url = urllib.parse.quote(fname)
        html_out += f'<a href="/uploads/{encoded_url}" target="_blank" style="display:block; color:#007BFF; text-decoration:underline; margin-bottom:3px;">📁 {fname}</a>'
    
    return html_out

@app.route('/')
def home():
    return render_template_string(HTML_HOME, is_online=get_shop_status(), notice=get_shop_notice())

@app.route('/service/<service_name>')
def service_page(service_name):
    if service_name == 'print':
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>SELF PRINT</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial; background:#f4f4f4; padding:20px; text-align:center;">
            <div style="max-width:400px; margin:auto; background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); text-align:left;">
                <h2 style="color:#2c3e50; text-align:center;">📄 SELF PRINT</h2>
                <p style="font-size:13px; color:#555;">इसमें आवेदक JPG, JPEG, PDF जैसी फाइलें upload कर सकता है तथा अपनी Request submit कर सकता है (बिना पेमेंट किए)।</p>
                <form action="/submit-service" method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="service_type" value="Self Print">
                    <input type="hidden" name="amount" value="0">
                    <label><b>नाम:</b></label>
                    <input type="text" name="cust_name" placeholder="आपका नाम" style="width:100%; padding:8px; margin:5px 0 10px 0;" required>
                    <label><b>मोबाइल नंबर:</b></label>
                    <input type="text" name="cust_mobile" placeholder="मोबाइल नंबर" style="width:100%; padding:8px; margin:5px 0 10px 0;" required>
                    <input type="hidden" name="cust_email" value="NA">
                    <label><b>दस्तावेज़ (मल्टीपल फाइलें चुनें):</b></label>
                    <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required style="width:100%; margin:5px 0 15px 0;">
                    <button type="submit" style="width:100%; padding:10px; background:#28a745; color:white; border:none; font-weight:bold; border-radius:5px; cursor:pointer;">🚀 प्रिंट के लिए भेजें</button>
                </form>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#007BFF; text-decoration:none;">⬅️ होम पेज</a>
            </div>
        </body>
        </html>
        ''')
    
    if service_name == 'bonafide':
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>मूल निवास प्रमाण पत्र</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; text-align: center; }
                .card { max-width: 440px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: left; }
                .info-box { background: #eef9ff; border: 1px solid #bce8f1; padding: 12px; border-radius: 5px; font-size: 13px; margin-bottom: 15px; color: #31708f; line-height: 1.5; }
                .btn-download { display: block; background: #2980b9; color: white; text-align: center; padding: 10px; text-decoration: none; font-weight: bold; border-radius: 5px; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2 style="color: #2c3e50; text-align: center; margin-top:0;">📜 मूल निवास प्रमाण पत्र</h2>
                <div class="info-box">
                    <b>📌 नियम व जरूरी दस्तावेज़:</b>
                    <ul style="padding-left:15px; margin:5px 0;">
                        <li>आधार कार्ड (आवेदक व पिता का)</li>
                        <li>जन आधार कार्ड</li>
                        <li>राशन कार्ड या बिजली बिल (निवास प्रमाण)</li>
                        <li>स्व-घोषणा पत्र (Form)</li>
                    </ul>
                    <p style="margin:8px 0 0 0; color:#d9534f; font-weight:bold;">⚠️ सभी दस्तावेज़ लेकर नजदीकी ई-मित्र पर संपर्क करें।</p>
                </div>
                <a href="/uploads/Bonafide-1.pdf" class="btn-download" target="_blank">📥 मूल निवास फॉर्म डाउनलोड करें (PDF)</a>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#007BFF; text-decoration:none;">⬅️ होम पेज</a>
            </div>
        </body>
        </html>
        ''')
        
    if service_name == 'caste':
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>जाति प्रमाण पत्र</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; text-align: center; }
                .card { max-width: 440px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: left; }
                .info-box { background: #eef9ff; border: 1px solid #bce8f1; padding: 12px; border-radius: 5px; font-size: 13px; margin-bottom: 15px; color: #31708f; line-height: 1.5; }
                .btn-download { display: block; background: #2980b9; color: white; text-align: center; padding: 10px; text-decoration: none; font-weight: bold; border-radius: 5px; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2 style="color: #2c3e50; text-align: center; margin-top:0;">📑 जाति प्रमाण पत्र</h2>
                <div class="info-box">
                    <b>📌 नियम व जरूरी दस्तावेज़:</b>
                    <ul style="padding-left:15px; margin:5px 0;">
                        <li>आधार कार्ड व जन आधार कार्ड</li>
                        <li>पुराना जाति प्रमाण पत्र / मूल निवास</li>
                        <li>सत्यापित आवेदन पत्र / शपथ पत्र</li>
                    </ul>
                    <p style="margin:8px 0 0 0; color:#d9534f; font-weight:bold;">⚠️ सभी दस्तावेज़ लेकर नजदीकी ई-मित्र पर संपर्क करें।</p>
                </div>
                <a href="/uploads/OBC-CASTE.pdf" class="btn-download" target="_blank">📥 जाति प्रमाण पत्र फॉर्म डाउनलोड करें (PDF)</a>
                <a href="/" style="display:block; text-align:center; margin-top:15px; color:#007BFF; text-decoration:none;">⬅️ होम पेज</a>
            </div>
        </body>
        </html>
        ''')

    fees_mapping = {
        'pan': ('PAN Card Application', 200, True),
        'pvc_aadhar': ('PVC Aadhar Card', 100, True),
        'voter': ('Voter Card', 100, True),
        'farmer': ('Farmer ID', 100, True),
        'shramik': ('Shramik Card', 200, True),
        'jan_aadhaar': ('Jan Aadhar Card', 50, True),
        'jan_aadhaar_pvc': ('Jan Aadhar PVC Card', 100, True),
        'ayushman': ('Ayushman Card', 100, True)
    }
    
    if service_name not in fees_mapping:
        return redirect(url_for('home'))
        
    s_title, s_fee, has_file_upload = fees_mapping[service_name]
    
    extra_field_html = ""
    note_html = ""
    
    if service_name == 'pan':
        note_html = """
        <div style="background: #eef9ff; border: 1px solid #bce8f1; padding: 10px; border-radius: 5px; font-size: 13px; margin-bottom: 12px; color: #31708f;">
            <b>📌 पैन कार्ड आवेदन के लिए निर्देश:</b><br>
            आवेदक का <b>आधार कार्ड</b>, <b>10वीं मार्कशीट जरूरी है</b>।
        </div>
        """
        extra_field_html = """
        <label><b>आधार नंबर / अन्य जानकारी:</b></label>
        <input type="text" name="extra_info" placeholder="विवरण दर्ज करें" required>
        """
    elif service_name == 'voter':
        note_html = """
        <div style="background: #eef9ff; border: 1px solid #bce8f1; padding: 10px; border-radius: 5px; font-size: 13px; margin-bottom: 12px; color: #31708f;">
            <b>📌 वोटर कार्ड हेतु निर्देश:</b> आवश्यक दस्तावेज अपलोड करें।
        </div>
        """
        extra_field_html = """
        <label><b>Epic नंबर / विवरण:</b></label>
        <input type="text" name="extra_info" placeholder="पुराना वोटर नंबर या विवरण">
        """
    else:
        extra_field_html = """
        <label><b>आवश्यक जानकारी / नंबर:</b></label>
        <input type="text" name="extra_info" placeholder="जरूरी जानकारी दर्ज करें">
        """

    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{s_title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; text-align: center; }}
            .card {{ max-width: 440px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: left; }}
            input, select, button {{ width: 100%; padding: 10px; margin: 6px 0 12px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }}
            button {{ background: #28a745; color: white; font-weight: bold; border: none; cursor: pointer; }}
            .fee-box {{ background: #e8f5e9; color: #2e7d32; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="color: #2c3e50; text-align: center; margin-top:0;">{s_title}</h2>
            {note_html}
            <div class="fee-box">देय फीस (Fee): ₹{s_fee}</div>
            <form action="/pay-and-submit" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="{s_title}">
                <input type="hidden" name="amount" value="{s_fee}">
                
                <label><b>आवेदक का पूरा नाम:</b></label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label><b>मोबाइल नंबर:</b></label>
                <input type="text" name="cust_mobile" placeholder="मोबाइल नंबर दर्ज करें" required>
                
                <label><b>जीमेल (Email):</b></label>
                <input type="text" name="cust_email" placeholder="email@gmail.com" required>

                {extra_field_html}
                
                <label><b>दस्तावेज अपलोड करें (मल्टीपल फाइलें):</b></label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                
                <hr style="border:0; border-top:1px dashed #ddd; margin:15px 0;">
                
                <div style="text-align:center;">
                    <p style="margin:5px 0; font-size:13px; font-weight:bold; color:#555;">नीचे दिए गए QR कोड को स्कैन करके ₹{s_fee} भुगतान करें:</p>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=upi://pay?pa={OWNER_UPI_ID}&pn={OWNER_NAME}&am={s_fee}&cu=INR" alt="UPI QR Code" style="border:1px solid #ddd; padding:5px; border-radius:5px; background:white;">
                    <p style="font-size:12px; color:#666; margin:5px 0;">UPI ID: <b>{OWNER_UPI_ID}</b></p>
                </div>
                
                <label><b>UPI ट्रांजैक्शन / UTR नंबर दर्ज करें:</b></label>
                <input type="text" name="utr_number" placeholder="जैसे: 4321xxxxxxxx" required style="background:#fffde7; font-weight:bold;">
                
                <button type="submit">🚀 भुगतान सत्यापित करें व फॉर्म जमा करें</button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:10px; color:#007BFF; text-decoration:none;">⬅️ होम पेज पर जाएं</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/submit-service', methods=['POST'])
@app.route('/pay-and-submit', methods=['POST'])
def submit_service():
    try:
        service_type = request.form.get('service_type', 'General')
        amount = request.form.get('amount', '0')
        cust_name = request.form.get('cust_name', 'सामान्य ग्राहक')
        cust_mobile = request.form.get('cust_mobile', 'लागू नहीं')
        cust_email = request.form.get('cust_email', 'लागू नहीं')
        extra_info = request.form.get('extra_info', '')
        utr_number = request.form.get('utr_number', 'Direct / N/A')
        
        uploaded_files = []
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename != '':
                # फाइल के नाम से स्पेस, कौमा और स्पेशल कैरेक्टर हटाकर सुरक्षित बनाएं
                clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
                clean_filename = re.sub(r'_+', '_', clean_filename)
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_filename))
                uploaded_files.append(clean_filename)
                
        filenames_str = ", ".join(uploaded_files) if uploaded_files else 'कोई फाइल नहीं'
        
        if extra_info:
            filenames_str = f"विवरण: {extra_info} | फाइलें: {filenames_str}"

        payload = {
            "sheetName": "New",
            "cust_name": cust_name,
            "cust_mobile": cust_mobile,
            "cust_email": cust_email,
            "service_type": service_type,
            "amount": amount,
            "filenames": filenames_str,
            "utr": utr_number,
            "status": "Pending (पेंडिंग)"
        }

        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:25px; background:white; max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 15px rgba(0,0,0,0.2);">
                <h2 style="color:#28a745;">✅ आवेदन सफलतापूर्वक जमा हो गया!</h2>
                <p style="font-size:15px; color:#333;">आपका डेटा और फाइलें Admin पैनल में सुरक्षित पहुंच गई हैं।</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">🏠 होम पेज पर जाएं</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर आया: {e}</h3><a href='/'>वापस जाएं</a>"

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('logged_in'):
        if request.method == 'POST':
            if request.form.get('password') == '7610':
                session['logged_in'] = True
                return redirect(url_for('admin_panel'))
            else:
                return '''<script>alert("गलत पासवर्ड!"); window.location="/admin-panel";</script>'''
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="background:#2c3e50; color:white; font-family:Arial; text-align:center; padding-top:100px;">
            <h2>🔐 BHUARKARKA ADMIN LOGIN</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="पासवर्ड दर्ज करें" style="padding:10px; font-size:16px; border-radius:5px; border:none; text-align:center;" required><br><br>
                <button type="submit" style="padding:10px 20px; background:#27ae60; color:white; border:none; font-size:16px; border-radius:5px; cursor:pointer;">LOGIN</button>
            </form>
        </body>
        </html>
        '''
    
    requests_list = []
    accepted_list = []
    
    try:
        res1 = requests.get(GOOGLE_SCRIPT_URL + "?action=get_data&sheetName=New", timeout=10)
        if res1.status_code == 200:
            requests_list = res1.json()
            
        res2 = requests.get(GOOGLE_SCRIPT_URL + "?action=get_data&sheetName=Accepted", timeout=10)
        if res2.status_code == 200:
            accepted_list = res2.json()
    except Exception as e:
        print(f"Fetch Error: {e}")

    return render_template_string(HTML_ADMIN, is_online=get_shop_status(), notice=get_shop_notice(), requests_list=requests_list, accepted_list=accepted_list)

@app.route('/admin/move/<source_sheet>/<target_sheet>/<int:row_index>')
def move_row(source_sheet, target_sheet, row_index):
    if not session.get('logged_in'):
        return redirect(url_for('admin_panel'))
    try:
        payload = {"action": "moveRow", "sourceSheet": source_sheet, "targetSheet": target_sheet, "rowIndex": row_index}
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Move Error: {e}")
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle-status')
def toggle_status():
    if session.get('logged_in'):
        set_shop_status(not get_shop_status())
    return redirect(url_for('admin_panel'))

@app.route('/admin/update-notice', methods=['POST'])
def update_notice():
    if session.get('logged_in'):
        set_shop_notice(request.form.get('notice', ''))
    return redirect(url_for('admin_panel'))

@app.route('/admin/download/<sheet_name>')
def download_report(sheet_name):
    if not session.get('logged_in'):
        return redirect(url_for('admin_panel'))
    try:
        res = requests.get(GOOGLE_SCRIPT_URL + f"?action=get_data&sheetName={sheet_name}", timeout=10)
        data = res.json() if res.status_code == 200 else []
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Mobile', 'Email', 'Service', 'Amount', 'Files', 'Status', 'UTR'])
        for row in data:
            writer.writerow(row)
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
