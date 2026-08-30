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
        .card { 
            background: linear-gradient(rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.94)), url('/kiosk-image/card.jpg') no-repeat center center; 
            background-size: cover;
            max-width: 450px; 
            margin: auto; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
            text-align: left;
        }
        select, input[type="file"], button { width: 100%; padding: 10px; margin: 8px 0; font-size: 15px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; background: rgba(255,255,255,0.95); }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 15px; }
        button:hover { background-color: #218838; }
        .note { font-size: 13px; color: #b22222; margin-top: 5px; font-weight: bold; background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; line-height: 1.5; }
        label { font-weight: bold; color: #333; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="text-align:center; color:#2c3e50;">🖨️ BHUARKARKA SERVICES 🙏</h2>
        <form action="/checkout" method="POST" enctype="multipart/form-data">
            
            <label>📌 काम/सेवा चुणो:</label>
            <select name="service_type" id="serviceType" onchange="updateServiceRequirements()">
                <option value="print">📄 सामान्य प्रिंट / डॉक्यूमेंट</option>
                <option value="vivah">📜 विवाह प्रमाण पत्र</option>
                <option value="aadhaar_update">🆔 आधार अड्रेस अपडेट</option>
                <option value="pan">💳 पैन कार्ड (PAN Card)</option>
                <option value="noc">📄 NOC प्रमाण पत्र</option>
                <option value="jati">📜 जाति प्रमाण पत्र</option>
                <option value="mool">🏠 मूल निवास प्रमाण पत्र</option>
            </select>

            <div id="docInstructions" class="note" style="display:none;"></div>
            <br>

            <label id="fileLabel">📁 थारो डॉक्यूमेंट / फोटो लगाओ:</label>
            <input type="file" name="files" id="fileInput" accept=".pdf,.jpg,.jpeg,.jfif" multiple required>
            <div style="font-size: 12px; color: #555; margin-top: -4px;">💡 आप एकसाथ एक या ज्यादा फोटो/पीडीएफ चुन सको हो!</div>
            
            <div style="margin-top: 10px;">
                <label>⚙️ प्रिंट/कार्य प्रकार:</label>
                <select name="print_type">
                    <option value="bw">ब्लैक एंड व्हाइट (सादी)</option>
                    <option value="color">कलर प्रिंट (रंगीन)</option>
                </select>
            </div>

            <button type="submit">🚀 आगे बड़ों & पेमेंट करो</button>
        </form>
    </div>

    <script>
        function updateServiceRequirements() {
            var service = document.getElementById("serviceType").value;
            var box = document.getElementById("docInstructions");
            
            if (service === 'vivah') {
                box.style.display = "block";
                box.innerHTML = "📝 <b>विवाह प्रमाण पत्र के लिए जरूरी दस्तावेज:</b><br>• आधार वर का + 4 पासपोर्ट साइज फोटो<br>• आधार वधू का + 4 पासपोर्ट साइज फोटो<br>• आधार वर के पिता/माता का + 1 पासपोर्ट साइज फोटो<br>• आधार वधू के पिता/माता का + 1 पासपोर्ट साइज फोटो<br>• आधार वर पक्ष गवाह का + 1 पासपोर्ट साइज फोटो<br>• आधार वधू पक्ष गवाह का + 1 पासपोर्ट साइज फोटो<br>• आधार पंडित/मौल्वी/पाथी का + 1 पासपोर्ट साइज फोटो<br>• वर वधू की संयुक्त फोटो 4x6 साइज में";
            } else if (service === 'aadhaar_update') {
                box.style.display = "block";
                box.innerHTML = "📝 <b>आधार अड्रेस अपडेट के लिए जरूरी:</b><br>• पहचान पत्र / राशन कार्ड / जाति प्रमाण पत्र / बैंक पासबुक फोटो उक्त, जिसमें जानकारी मिल हो।";
            } else if (service === 'pan') {
                box.style.display = "block";
                box.innerHTML = "📝 <b>पैन कार्ड के लिए जरूरी दस्तावेज:</b><br>• आधार कार्ड<br>• 10वीं मार्कशीट / पहचान पत्र जिसमें जानकारी मिल हो।";
            } else if (service === 'noc') {
                box.style.display = "block";
                box.innerHTML = "📝 <b>NOC प्रमाण पत्र के लिए:</b> संबंधित दस्तावेज अपलोड करें।";
            } else if (service === 'jati' || service === 'mool') {
                box.style.display = "block";
                box.innerHTML = "📝 <b>जाति / मूल निवास प्रमाण पत्र के लिए जरूरी:</b><br>• आधार स्वयं, पिता का आधार, जन आधार कार्ड, राशन कार्ड, पिता का पहचान पत्र<br>• जमाबंदी या जाति का प्रूफ / 1993 या 1980 की वोटर लिस्ट (जाति के लिए)<br>• 2008, 2013, 2017, 2026 की वोटर लिस्ट (मूल निवास के लिए)";
            } else {
                box.style.display = "none";
            }
        }
    </script>
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
        print_type = request.form.get('print_type')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            return "कोई फाइल कोनी चुणी! <a href='/'>पाछा जाओ</a>"
        
        saved_file_filenames = []
        total_pages = 0

        for file in uploaded_files:
            if file and file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_file_filenames.append(file.filename)
                
                if file.filename.lower().endswith('.pdf'):
                    try:
                        reader = pypdf.PdfReader(file_path)
                        total_pages += len(reader.pages)
                    except:
                        total_pages += 1

        # सेवा के आधार पर फीस तय करना (आप अपने हिसाब से राशि बदल सकते हैं)
        if service_type in ['vivah', 'jati', 'mool']:
            amount = 50
        elif service_type in ['pan', 'aadhaar_update', 'noc']:
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
            <title>स्कैन कर ने पेमेंट करो</title>
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
                    background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('/kiosk-image/prakash.jfif') no-repeat center center; 
                    background-size: cover;
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
                <h2>💳 QR स्कैन कर ने रूप्या भेजो</h2>
                <p><b>कुल रुपया:</b> <span style="font-size: 26px; color: #d9534f;">₹{{ amount }}</span></p>
                <p style="font-size: 14px; color: #222; font-weight: bold;">कूँण से भी UPI ॲप सू स्कैन करो:</p>
                
                <img src="{{ qr_url }}" alt="UPI QR Code" style="border: 2px solid #ddd; border-radius: 8px; padding: 5px; background: white;">
                
                <form action="/submit-request" method="POST">
                    <input type="hidden" name="filenames" value="{{ filenames_string }}">
                    <input type="hidden" name="amount" value="{{ amount }}">
                    <input type="hidden" name="service_type" value="{{ service_type }}">
                    <button type="submit" class="btn-wait">⏳ मैं पैमेंट कर दियो है, दुकानदार ने सूचणा भेजो</button>
                </form>
            </div>
        </body>
        </html>
        ''', amount=amount, qr_url=qr_api_url, filenames_string=filenames_string, service_type=service_type)
    except Exception as e:
        return f"<h3>काई गलती है: {e}</h3><a href='/'>पाछा जाओ</a>"


@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        filenames_string = request.form.get('filenames')
        amount = request.form.get('amount')
        service_type = request.form.get('service_type')
        
        req_id = len(pending_requests) + 1
        request_data = {
            'id': req_id, 
            'filenames': filenames_string, 
            'amount': amount,
            'service_type': service_type
        }
        pending_requests.append(request_data)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.9); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#d9534f;">⏳ पैमेंट री सूचणा दुकानदारा कन्ने पुग गी है!</h2>
                <p style="font-size:18px;">थारी रिक्वेस्ट एडमिन पैनल पर भेज दी है। काम जल्दी ही शुरू हो जावेलो...</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">होम पेज पाछा जाओ</a>
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
        has_requests = "false"
        
        if not pending_requests:
            cards_html = "<p style='color: #ddd;'>अभी कोई नई सर्विस रिक्वेस्ट कोनी है...</p>"
        else:
            has_requests = "true"
            for idx, req in enumerate(pending_requests):
                cards_html += f'''
                    <div style="background: rgba(0, 0, 0, 0.85); padding: 15px; margin: 10px auto; max-width: 400px; border-radius: 8px; border-left: 5px solid #28a745; text-align: left;">
                        <p><b>रिक्वेस्ट नंबर:</b> #{req['id']}</p>
                        <p><b>सेवा का नाम:</b> <span style="color:#ffeb3b; text-transform:uppercase;">{req['service_type']}</span></p>
                        <p><b>रुपया आया:</b> <span style="color:#4cd137;">₹{req['amount']}</span></p>
                        <p><b>फाइलें:</b> <a href="/uploads/{req['filenames']}" target="_blank" style="color:#00bcd4;">फाइल देखें</a></p>
                        <form action="/approve-print" method="POST">
                            <input type="hidden" name="req_index" value="{idx}">
                            <button type="submit" style="background: #28a745; color: white; border: none; padding: 10px 15px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px;">✅ पेमेंट पक्का, काम शुरू करो</button>
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
            <h2>🛡️ BHUARKARKA SERVICES - लाइव रिक्वेस्ट</h2>
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
            
            return "<h3 style='color:green; text-align:center; margin-top:50px; background:white; padding:20px; max-width:400px; margin:50px auto; border-radius:10px;'>🎉 रिक्वेस्ट अप्रूव कर दी है! <a href='/admin-panel' style='color:#007BFF;'>पाछा एडमिन पैनल में जाओ</a></h3>"
        
        return "रिक्वेस्ट पहिले ही पूरी हो चुकी है! <a href='/admin-panel'>पाछा जाओ</a>"
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/admin-panel'>पाछा जाओ</a>"


@app.route('/get-next-print', methods=['GET'])
def get_next_print():
    if print_queue:
        job = print_queue.pop(0)
        return {
            'status': 'success',
            'filenames': job['filenames'],
            'amount': job['amount']
        }
    return {'status': 'empty'}


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n👉 ग्राहक लिंक: http://{local_ip}:5000")
    print(f"👉 मोबाइल एडमिन पैनल लिंक: http://{local_ip}:5000/admin-panel (पासवर्ड: 1234)\n")
    app.run(host='0.0.0.0', port=5000)