from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, session
import os
import pypdf
import socket

app = Flask(__name__)
app.secret_key = 'prakash_print_kiosk_secret_key'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPI_ID = "Q508475385@ybl"
MERCHANT_NAME = "BHUARKARKA SERVICES"

pending_requests = []
print_queue = []

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
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
        .container {
            max-width: 600px;
            margin: auto;
        }
        .card { 
            background: linear-gradient(rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95)), url('/kiosk-image/card.jpg') no-repeat center center; 
            background-size: cover;
            margin: 15px auto; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
            text-align: left;
        }
        input[type="text"], input[type="file"], select, button { 
            width: 100%; padding: 10px; margin: 8px 0; font-size: 15px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; background: rgba(255,255,255,0.95); 
        }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background-color: #218838; }
        .note { font-size: 13px; color: #b22222; margin-top: 5px; font-weight: bold; background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; line-height: 1.4; }
        label { font-weight: bold; color: #333; font-size: 14px; }
        h3 { color: #2c3e50; margin-top: 0; border-bottom: 2px solid #28a745; padding-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); margin-bottom: 20px;">🖨️ BHUARKARKA SERVICES 🙏</h1>

        <!-- कार्ड 1: सामान्य प्रिंट सर्विस -->
        <div class="card">
            <h3>📄 1. सामान्य प्रिंट / डॉक्यूमेंट</h3>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="print">
                
                <label>👤 आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📁 डॉक्यूमेंट / फोटो अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
                
                <label>⚙️ प्रिंट प्रकार:</label>
                <select name="print_type">
                    <option value="bw">ब्लैक एंड व्हाइट (सादी)</option>
                    <option value="color">कलर प्रिंट (रंगीन)</option>
                </select>

                <button type="submit">🚀 प्रिंट के लिए पेमेंट करें</button>
            </form>
        </div>

        <!-- कार्ड 2: पैन कार्ड सर्विस -->
        <div class="card">
            <h3>💳 2. पैन कार्ड (PAN Card)</h3>
            <div class="note">
                <b>📌 जरूरी दस्तावेज:</b><br>
                • आधार कार्ड<br>
                • 10वीं मार्कशीट / पहचान पत्र (जिसमें जानकारी मेल खाती हो)
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pan">
                
                <label>👤 आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📁 दस्तावेज अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>

                <button type="submit">🚀 पैन कार्ड के लिए पेमेंट करें</button>
            </form>
        </div>

        <!-- कार्ड 3: विवाह प्रमाण पत्र -->
        <div class="card">
            <h3>📜 3. विवाह प्रमाण पत्र</h3>
            <div class="note">
                <b>📌 जरूरी दस्तावेज:</b><br>
                • आधार वर का + 4 पासपोर्ट फोटो<br>
                • आधार वधू का + 4 पासपोर्ट फोटो<br>
                • माता-पिता व गवाहों के आधार और फोटो<br>
                • वर-वधू की संयुक्त फोटो (4x6 साइज)
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="vivah">
                
                <label>👤 आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📁 सभी दस्तावेज अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>

                <button type="submit">🚀 विवाह प्रमाण पत्र के लिए पेमेंट करें</button>
            </form>
        </div>

        <!-- कार्ड 4: आधार अड्रेस अपडेट -->
        <div class="card">
            <h3>🆔 4. आधार अड्रेस अपडेट</h3>
            <div class="note">
                <b>📌 जरूरी दस्तावेज:</b><br>
                • पहचान पत्र / राशन कार्ड / जाति प्रमाण पत्र / बैंक पासबुक (जिसमें सही पता हो)
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="aadhaar_update">
                
                <label>👤 आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📁 दस्तावेज अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>

                <button type="submit">🚀 अड्रेस अपडेट के लिए पेमेंट करें</button>
            </form>
        </div>

        <!-- कार्ड 5: जाति एवं मूल निवास प्रमाण पत्र -->
        <div class="card">
            <h3>🏠 5. जाति / मूल निवास प्रमाण पत्र</h3>
            <div class="note">
                <b>📌 जरूरी दस्तावेज:</b><br>
                • स्वयं व पिता का आधार, जन आधार, राशन कार्ड<br>
                • पुराना पहचान पत्र व वोटर लिस्ट (जाति के लिए 1993/1980, मूल निवास के लिए पुराने साल)
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="jati_mool">
                
                <label>👤 आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📁 दस्तावेज अपलोड करें:</label>
                <input type="file" name="files" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>

                <button type="submit">🚀 प्रमाण पत्र के लिए पेमेंट करें</button>
            </form>
        </div>

    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_HOME)


@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        uploaded_files = request.files.getlist('files')
        service_type = request.form.get('service_type')
        cust_name = request.form.get('cust_name')
        cust_mobile = request.form.get('cust_mobile')
        print_type = request.form.get('print_type', 'bw')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            return "कोई फाइल कोनी चुणी! <a href='/'>पाछा जाओ</a>"
        
        saved_file_filenames = []
        for file in uploaded_files:
            if file and file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_file_filenames.append(file.filename)

        # सेवा के आधार पर फीस राशि
        if service_type in ['vivah', 'jati_mool']:
            amount = 50
        elif service_type in ['pan', 'aadhaar_update']:
            amount = 30
        else:
            amount = 10 * len(saved_file_filenames)

        upi_link = f"upi://pay?pa={UPI_ID}&pn={MERCHANT_NAME}&am={amount}&cu=INR"
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={upi_link}"
        filenames_string = ",".join(saved_file_filenames)

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>स्कैन करके पेमेंट करें</title>
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
                .card { 
                    background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)); 
                    max-width: 400px; 
                    margin: auto; 
                    padding: 20px; 
                    border-radius: 10px; 
                    box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
                }
                .btn-wait { background-color: #ffc107; color: #333; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; width: 100%; margin-top: 15px; font-weight: bold; cursor: pointer;}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>💳 QR स्कैन करके रुपये भेजें</h2>
                <p><b>आवेदक:</b> {{ cust_name }} ({{ cust_mobile }})</p>
                <p><b>कुल रुपया:</b> <span style="font-size: 26px; color: #d9534f;">₹{{ amount }}</span></p>
                
                <img src="{{ qr_url }}" alt="UPI QR Code" style="border: 2px solid #ddd; border-radius: 8px; padding: 5px; background: white;">
                
                <form action="/submit-request" method="POST">
                    <input type="hidden" name="filenames" value="{{ filenames_string }}">
                    <input type="hidden" name="amount" value="{{ amount }}">
                    <input type="hidden" name="service_type" value="{{ service_type }}">
                    <input type="hidden" name="cust_name" value="{{ cust_name }}">
                    <input type="hidden" name="cust_mobile" value="{{ cust_mobile }}">
                    <button type="submit" class="btn-wait">⏳ मैंने पेमेंट कर दिया है, सूचना भेजें</button>
                </form>
            </div>
        </body>
        </html>
        ''', amount=amount, qr_url=qr_api_url, filenames_string=filenames_string, service_type=service_type, cust_name=cust_name, cust_mobile=cust_mobile)
    except Exception as e:
        return f"<h3>काई गलती है: {e}</h3><a href='/'>पाछा जाओ</a>"


@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        filenames_string = request.form.get('filenames')
        amount = request.form.get('amount')
        service_type = request.form.get('service_type')
        cust_name = request.form.get('cust_name')
        cust_mobile = request.form.get('cust_mobile')
        
        req_id = len(pending_requests) + 1
        request_data = {
            'id': req_id, 
            'filenames': filenames_string, 
            'amount': amount,
            'service_type': service_type,
            'cust_name': cust_name,
            'cust_mobile': cust_mobile
        }
        pending_requests.append(request_data)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.9); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#d9534f;">⏳ पेमेंट की सूचना दुकानदार को पहुँच गई है!</h2>
                <p style="font-size:18px;">आपकी रिक्वेस्ट एडमिन पैनल पर भेज दी गई है। काम जल्दी शुरू होगा...</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">होम पेज पर वापस जाएं</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/'>पाछा जाओ</a>"


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error_msg = ""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '1234': 
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            error_msg = "❌ गलत पासवर्ड! दोबारा कोशिश करें।"
            
    return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>दुकानदार लॉगिन</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; background: #222; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .login-card {{ background: #333; padding: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.5); width: 300px; text-align: center; }}
                input {{ width: 100%; padding: 10px; margin: 15px 0; font-size: 16px; border-radius: 5px; border: none; box-sizing: border-box; }}
                button {{ width: 100%; padding: 10px; background: #28a745; color: white; border: none; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; }}
                .error {{ color: #ff6b6b; font-size: 14px; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="login-card">
                <h2>🔐 BHUARKARKA LOGIN</h2>
                <div class="error">{error_msg}</div>
                <form method="POST">
                    <input type="password" name="password" placeholder="पासवर्ड दर्ज करें" required autofocus>
                    <button type="submit">लॉगिन करें</button>
                </form>
            </div>
        </body>
        </html>
    '''


@app.route('/admin-panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    try:
        cards_html = ""
        if not pending_requests:
            cards_html = "<p style='color: #ddd;'>अभी कोई नई सर्विस रिक्वेस्ट नहीं है...</p>"
        else:
            for idx, req in enumerate(pending_requests):
                # एकाधिक फाइलों के लिए डाउनलोड लिंक तैयार करना
                files_list = req['filenames'].split(',')
                download_links = ""
                for f in files_list:
                    download_links += f'<a href="/uploads/{f.strip()}" download style="color:#00bcd4; margin-right:10px; text-decoration:underline;">📥 {f.strip()} डाउनलोड करें</a><br>'

                cards_html += f'''
                    <div style="background: rgba(0, 0, 0, 0.85); padding: 15px; margin: 15px auto; max-width: 450px; border-radius: 8px; border-left: 5px solid #28a745; text-align: left;">
                        <p><b>रिक्वेस्ट नंबर:</b> #{req['id']}</p>
                        <p><b>आवेदक का नाम:</b> <span style="color:#00e676; font-size:17px;">{req['cust_name']}</span></p>
                        <p><b>मोबाइल नंबर:</b> <span style="color:#ffeb3b;">{req['cust_mobile']}</span></p>
                        <p><b>सेवा का नाम:</b> <span style="color:#ff9800; text-transform:uppercase;">{req['service_type']}</span></p>
                        <p><b>रुपया प्राप्त:</b> <span style="color:#4cd137;">₹{req['amount']}</span></p>
                        <p><b>दस्तावेज़ फाइलें:</b><br>{download_links}</p>
                        <form action="/approve-print" method="POST">
                            <input type="hidden" name="req_index" value="{idx}">
                            <button type="submit" style="background: #28a745; color: white; border: none; padding: 10px 15px; font-size: 15px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px;">✅ काम पूरा हुआ / अप्रूव करें</button>
                        </form>
                    </div>
                '''

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>BHUARKARKA - एडमिन पैनल</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="refresh" content="3">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('/kiosk-image/prakash 2.jfif') no-repeat center center fixed; 
                    background-size: cover; 
                    color: #fff; 
                    padding: 15px; 
                    text-align: center; 
                    min-height: 100vh;
                }}
            </style>
        </head>
        <body>
            <h2>🛡️ BHUARKARKA SERVICES - लाइव रिक्वेस्ट पैनल</h2>
            {cards_html}
            <br>
            <a href="/admin-logout" style="color: #ff6b6b; text-decoration: none; background: rgba(0,0,0,0.7); padding: 8px 15px; border-radius: 5px; font-weight: bold;">🔒 लॉगआउट</a>
        </body>
        </html>
        '''
    except Exception as e:
        return f"एडमिन पैनल एरर: {e}"


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/approve-print', methods=['POST'])
def approve_print():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    try:
        req_index = int(request.form.get('req_index'))
        if 0 <= req_index < len(pending_requests):
            req = pending_requests.pop(req_index)
            print_queue.append(req)
            return "<h3 style='color:green; text-align:center; margin-top:50px; background:white; padding:20px; max-width:400px; margin:50px auto; border-radius:10px;'>🎉 रिक्वेस्ट पूरी कर दी गई है! <a href='/admin-panel' style='color:#007BFF;'>पाछा एडमिन पैनल में जाओ</a></h3>"
        return "रिक्वेस्ट पहले ही हटाई जा चुकी है! <a href='/admin-panel'>पाछा जाओ</a>"
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/admin-panel'>पाछा जाओ</a>"


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n👉 ग्राहक लिंक: http://{local_ip}:5000")
    print(f"👉 मोबाइल एडमिन पैनल लिंक: http://{local_ip}:5000/admin-panel (पासवर्ड: 1234)\n")
    app.run(host='0.0.0.0', port=5000)