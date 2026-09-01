from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, session, Response
import os
import requests
import json
import csv
import io

app = Flask(__name__)
app.secret_key = 'prakash_print_kiosk_secret_key'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STATUS_FILE = 'shop_status.txt'
NOTICE_FILE = 'shop_notice.txt'

# ⚠️ यहाँ अपनी सही Google Apps Script URL डालें
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
    # पहले uploads फोल्डर में चेक करें, अगर वहाँ न हो तो मेन रूट फोल्डर से भेजें
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        if filename.lower().endswith('.pdf'):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        # अगर फाइल मेन रूट में है
        if os.path.exists(filename):
            if filename.lower().endswith('.pdf'):
                return send_from_directory('.', filename, as_attachment=True)
            return send_from_directory('.', filename)
    return redirect(url_for('home'))

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
                            <td>
                                {% if requests_list[i][5] and requests_list[i][5] != 'कोई फाइल नहीं' and 'ई-मित्र' not in requests_list[i][5] %}
                                    {% for fname in requests_list[i][5].split(',') %}
                                        <a href="/uploads/{{ fname.strip() }}" target="_blank" style="display:block; color:#007BFF; text-decoration:underline; margin-bottom:3px;">📁 {{ fname.strip() }}</a>
                                    {% endfor %}
                                {% else %}
                                    {{ requests_list[i][5] }}यह 'BHUARKARKA SERVICES' स्मार्ट कियोस्क के लिए तैयार किया गया एक बेहतरीन और उपयोगी **Flask वेब एप्लीकेशन** है। यह ग्राहकों को विभिन्न ई-मित्र सेवाओं (जैसे PAN कार्ड, वोटर कार्ड, सेल्फ प्रिंट) के लिए फॉर्म भरने, दस्तावेज़ अपलोड करने और UPI के माध्यम से सीधे भुगतान करने की सुविधा देता है।

**इस कोड की मुख्य विशेषताएं:**
* **डायनामिक सर्विस कियोस्क:** होम पेज पर दुकान का ऑनलाइन/ऑफलाइन स्टेटस और लाइव नोटिस दिखाने की सुविधा है।
* **UPI पेमेंट इंटीग्रेशन:** Google QR API का उपयोग करके ग्राहक के चुने गए फॉर्म की फीस के अनुसार आटोमेटिक QR कोड जनरेट होता है।
* **गूगल शीट्स डेटाबेस (Google Apps Script):** सबमिट किया गया डेटा और UTR नंबर सीधे Google Sheets में सेव हो रहा है, जिससे अलग से डेटाबेस (जैसे MySQL या SQLite) सेटअप करने की जरूरत नहीं पड़ती।
* **एडमिन पैनल (`/admin-panel`):** पासवर्ड (7610) द्वारा सुरक्षित एक डैशबोर्ड, जहां से नई रिक्वेस्ट को मंजूर (Accept) या पूरा (Complete) किया जा सकता है, होमपेज का नोटिस बदला जा सकता है, और एक्सेल (CSV) रिपोर्ट डाउनलोड की जा सकती है।

**सुरक्षा और परफॉरमेंस के लिए कुछ महत्वपूर्ण सुझाव (Best Practices):**

* **हार्डकोडेड पासवर्ड और सीक्रेट की:** 
  कोड में एडमिन पासवर्ड (`7610`) और Flask Secret Key (`prakash_print_kiosk_secret_key`) सीधे लिखे हुए हैं। अगर यह कोड पब्लिक रिपॉजिटरी (जैसे GitHub) पर जाता है, तो यह सुरक्षित नहीं है। इन्हें Environment Variables (जैसे `os.environ.get('ADMIN_PASS')`) में रखना बेहतर होगा।
* **लोकल फाइल स्टोरेज (Uploads):** 
  दस्तावेज़ `uploads/` फोल्डर में सेव हो रहे हैं। यदि आप इस ऐप को Render, Heroku या Railway जैसे क्लाउड प्लेटफॉर्म पर डिप्लॉय करते हैं, तो सर्वर रीस्टार्ट होने पर अपलोड की गई फाइलें डिलीट हो सकती हैं (क्योंकि वे ephemeral storage का उपयोग करते हैं)। स्थायी स्टोरेज के लिए Google Drive API, AWS S3, या Cloudinary का उपयोग करने पर विचार करें।
* **फाइल पाथ सिक्योरिटी:** 
  `/uploads/<path:filename>` रूट में `os.path.exists(filename)` का सीधा उपयोग किया गया है। इसे थोड़ा और सुरक्षित (Sanitize) करना चाहिए ताकि कोई बाहरी व्यक्ति Directory Traversal (`../`) का उपयोग करके सर्वर की अन्य संवेदनशील फाइलें न पढ़ सके। `werkzeug.utils.secure_filename` का उपयोग करना अपलोड्स के लिए एक अच्छा विकल्प रहेगा।

क्या आप इस एप्लीकेशन को इंटरनेट पर लाइव (Deploy) करने में मदद चाहते हैं, या इसके UI/डिज़ाइन में कोई नया बदलाव करना चाहते हैं?
