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

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyCc_unuXdvpBqCieHmjYi-XPpPe5fw96Z4IjdBsGxYKmbPuhdO-Oa0u01mkjmUM9NUcw/exec"

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
    if filename.lower().endswith('.pdf'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/kiosk-image/<path:filename>')
def kiosk_image(filename):
    return send_from_directory('uploads', filename)

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
                        <th>फाइलें</th>
                        <th>स्टेटस</th>
                        <th>एक्शन (कार्यवाही)</th>
                    </tr>
                    {% if requests_list %}
                        {% for i in range(requests_list|length) %}
                        <tr>
                            <td>{{ requests_list[i][0] }}</td>
                            <td>{{ requests_list[i][1] }}</td>
                            <td>{{ requests_list[i][3] }}</td>
                            <td>
                                {% if requests_list[i][5] and requests_list[i][5] != 'कोई फाइल नहीं' %}
                                    {% for fname in requests_list[i][5].split(',') %}
                                        <a href="/uploads/{{ fname.strip() }}" target="_blank" style="display:block; color:#007BFF; text-decoration:underline; margin-bottom:3px;">📁 {{ fname.strip() }}</a>
                                    {% endfor %}
                                {% else %}
                                    कोई फाइल नहीं
                                {% endif %}
                            </td>
                            <td>{{ requests_list[i][6] }}</td>
                            <td>
                                <a href="/admin/move/New/Accepted/{{ i }}" class="btn btn-warning">👉 मंजूर करें (Sheet 2)</a>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="6" style="text-align:center;">अभी कोई नई सर्विस रिक्वेस्ट नहीं है।</td></tr>
                    {% endif %}
                </table>
            </div>
        </div>

        <!-- मंजूर किए गए आवेदन (Accepted / Sheet 2) -->
        <div class="card">
            <h3>📑 मंजूर किए गए आवेदन (Accepted / Sheet 2)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <tr>
                        <th>नाम</th>
                        <th>मोबाइल</th>
                        <th>सेवा</th>
                        <th>फाइलें</th>
                        <th>स्टेटस</th>
                        <th>एक्शन (कार्यवाही)</th>
                    </tr>
                    {% if accepted_list %}
                        {% for i in range(accepted_list|length) %}
                        <tr>
                            <td>{{ accepted_list[i][0] }}</td>
                            <td>{{ accepted_list[i][1] }}</td>
                            <td>{{ accepted_list[i][3] }}</td>
                            <td>
                                {% if accepted_list[i][5] and accepted_list[i][5] != 'कोई फाइल नहीं' %}
                                    {% for fname in accepted_list[i][5].split(',') %}
                                        <a href="/uploads/{{ fname.strip() }}" target="_blank" style="display:block; color:#007BFF; text-decoration:underline; margin-bottom:3px;">📁 {{ fname.strip() }}</a>
                                    {% endfor %}
                                {% else %}
                                    कोई फाइल नहीं
                                {% endif %}
                            </td>
                            <td>{{ accepted_list[i][6] }}</td>
                            <td>
                                <a href="/admin/move/Accepted/Completed/{{ i }}" class="btn">✅ पूर्ण करें (Sheet 3)</a>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="6" style="text-align:center;">कोई मंजूर किया गया आवेदन नहीं है।</td></tr>
                    {% endif %}
                </table>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/admin/logout" class="btn btn-danger" style="padding: 10px 20px; font-size: 15px;">🔒 LOGOUT</a>
        </div>
    </div>

    <!-- ऑटो-रिफ्रेश स्क्रिप्ट (हर 3 सेकंड) -->
    <script>
        setTimeout(function(){
            location.reload();
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_HOME, is_online=get_shop_status(), notice=get_shop_notice())

@app.route('/service/<service_name>')
def service_page(service_name):
    if service_name == 'print':
        form_html = '''
            <h2>📄 SELF PRINT SERVICE</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="print">
                <label>📁 डॉक्यूमेंट / फाइलें अपलोड करें (एक साथ कई फाइलें चुन सकते हैं):</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <label>⚙️ प्रिंट प्रकार:</label>
                <select name="print_type">
                    <option value="bw">ब्लैक एंड व्हाइट (सादी)</option>
                    <option value="color">कलर प्रिंट (रंगीन)</option>
                </select>
                <button type="submit">🚀 प्रिंट के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'pan':
        form_html = '''
            <h2>💳 PAN CARD APPLICATION</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pan">
                <label>👤 आवेदक का पूरा नाम (आधार के अनुसार):</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज अपलोड करें (एक या अधिक फाइलें चुनें):</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 ₹200 का भुगतान करें व आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'pvc_aadhar':
        form_html = '''
            <h2>🪪 PVC AADHAR CARD (ओरिजिनल)</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pvc_aadhar">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर (आधार लिंक्ड - OTP हेतु):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 आधार कार्ड अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 ₹100 का भुगतान करें व आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'bonafide':
        form_html = '''
            <h2>📜 मूल निवास प्रमाण पत्र (Bonafide)</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="bonafide">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 सभी जरूरी दस्तावेज एक साथ चुनें (आवेदन, आधार, जन आधार आदि):</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 मूल निवास प्रमाण पत्र हेतु आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'caste':
        form_html = '''
            <h2>📑 जाति प्रमाण पत्र (Caste Certificate)</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="caste">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 सभी जरूरी दस्तावेज एक साथ चुनें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 जाति प्रमाण पत्र हेतु आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'farmer':
        form_html = '''
            <h2>🌽 FARMER ID APPLICATION</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="farmer">
                <label>👤 किसान का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज अपलोड करें (आधार, जमाबंदी आदि):</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 FARMER ID के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'shramik':
        form_html = '''
            <h2>👷 SHRAMIK CARD (ई-श्रम)</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="shramik">
                <label>👤 श्रमिक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 SHRAMIK CARD के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'jan_aadhaar':
        form_html = '''
            <h2>🆔 JAN AADHAAR CARD</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="jan_aadhaar">
                <label>👤 मुखिया का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 आधार कार्ड व अन्य दस्तावेज:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 JAN AADHAAR के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'ayushman':
        form_html = '''
            <h2>🏥 AYUSHMAN CARD</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="ayushman">
                <label>👤 लाभार्थी का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 आधार कार्ड अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                <button type="submit">🚀 AYUSHMAN CARD के लिए आगे बढ़ें</button>
            </form>
        '''
    else:
        return redirect(url_for('home'))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BHUARKARKA SERVICES</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('/kiosk-image/bc.jpg') no-repeat center center fixed; background-size: cover; padding: 20px; text-align: center; min-height: 100vh;}
            .card { background: rgba(255, 255, 255, 0.96); max-width: 450px; margin: auto; padding: 20px; border-radius: 12px; box-shadow: 0px 0px 15px rgba(0,0,0,0.3); text-align: left;}
            input[type="text"], input[type="file"], select, button { width: 100%; padding: 10px; margin: 8px 0; font-size: 15px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; background: #fff; }
            button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 15px; font-family: 'Britannic Bold', Arial, sans-serif;}
            label { font-weight: bold; color: #333; font-size: 13px; }
            h2 { font-family: 'Britannic Bold', Arial, sans-serif; color: #2c3e50; margin-top: 0; border-bottom: 2px solid #28a745; padding-bottom: 8px; text-align: center; }
            .back-link { display: block; text-align: center; margin-top: 15px; color: #007BFF; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            ''' + form_html + '''
            <a href="/" class="back-link">⬅️ होम पेज पर वापस जाएं</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        service_type = request.form.get('service_type', 'General')
        cust_name = request.form.get('cust_name', 'सामान्य ग्राहक')
        cust_mobile = request.form.get('cust_mobile', 'लागू नहीं')
        cust_email = request.form.get('cust_email', 'लागू नहीं')
        
        uploaded_files = []
        # यहाँ सभी फॉर्म्स के लिए 'files' नाम से मल्टीपल फाइलों को कैच किया गया है
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                uploaded_files.append(filename)
        
        filenames_str = ", ".join(uploaded_files) if uploaded_files else 'कोई फाइल नहीं'
        
        payload = {
            "sheetName": "New",
            "cust_name": cust_name,
            "cust_mobile": cust_mobile,
            "cust_email": cust_email,
            "service_type": service_type,
            "amount": "50",
            "filenames": filenames_str,
            "status": "Pending (पेंडिंग)"
        }

        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.95); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#28a745; font-family:'Britannic Bold', Arial, sans-serif;">✅ REQUEST SUBMITTED!</h2>
                <p style="font-size:16px;">आपका डेटा और फाइलें सफलतापर्वूक अपलोड हो गई हैं।</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">HOME PAGE</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/'>वापस जाएं</a>"

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
        payload = {
            "action": "moveRow",
            "sourceSheet": source_sheet,
            "targetSheet": target_sheet,
            "rowIndex": row_index
        }
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
        writer.writerow(['Name', 'Mobile', 'Email', 'Service', 'Amount', 'Files', 'Status'])
        for row in data:
            writer.writerow(row)
        
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={sheet_name}_Report.csv"}
        )
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
