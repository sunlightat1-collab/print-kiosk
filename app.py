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
            max-width: 500px;
            margin: auto;
        }
        h1 {
            color: white;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            margin-bottom: 25px;
        }
        .app-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }
        .app-icon-card {
            background: rgba(255, 255, 255, 0.95);
            width: 130px;
            height: 130px;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #333;
            transition: transform 0.2s, background 0.2s;
            cursor: pointer;
            border: 2px solid #ddd;
        }
        .app-icon-card:hover {
            transform: scale(1.08);
            background: #ffffff;
            border-color: #28a745;
        }
        .emoji {
            font-size: 40px;
            margin-bottom: 8px;
        }
        .title-text {
            font-size: 13px;
            font-weight: bold;
            text-align: center;
            padding: 0 5px;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖨️ BHUARKARKA SERVICES 🙏</h1>
        <p style="color: #fff; margin-bottom: 20px; font-weight: bold;">कृपया अपनी सेवा चुनें:</p>
        
        <div class="app-grid">
            <a href="/service/print" class="app-icon-card">
                <div class="emoji">📄</div>
                <div class="title-text">सेल्फ प्रिंट</div>
            </a>

            <a href="/service/pan" class="app-icon-card">
                <div class="emoji">💳</div>
                <div class="title-text">पैन कार्ड आवेदन</div>
            </a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_HOME)


@app.route('/service/<service_name>')
def service_page(service_name):
    if service_name == 'print':
        form_html = '''
            <h2>📄 सेल्फ प्रिंट सेवा</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="print">
                
                <label>📁 डॉक्यूमेंट / फाइल अपलोड करें:</label>
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
            <h2>💳 पैन कार्ड आवेदन</h2>
            <div class="note">
                <b>📌 जरूरी दस्तावेज:</b><br>
                1. आधार कार्ड (मुख्य पहचान)<br>
                2. अन्य आईडी (जैसे: 10वीं मार्कशीट / वोटर आईडी आदि)
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pan">
                
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>

                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>

                <label>📁 कॉलम 1: आधार कार्ड अपलोड करें:</label>
                <input type="file" name="file_aadhar" accept=".pdf,.jpg,.jpeg,.jfif" required>

                <label>📁 कॉलम 2: अन्य जरूरी आईडी अपलोड करें:</label>
                <input type="file" name="file_other" accept=".pdf,.jpg,.jpeg,.jfif" required>

                <button type="submit">🚀 पैन कार्ड के लिए आगे बढ़ें</button>
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
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('/kiosk-image/bc.jpg') no-repeat center center fixed; 
                background-size: cover; 
                padding: 20px; 
                text-align: center; 
                min-height: 100vh;
            }
            .card { 
                background: linear-gradient(rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.96)); 
                max-width: 450px; 
                margin: auto; 
                padding: 20px; 
                border-radius: 12px; 
                box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
                text-align: left;
            }
            input[type="text"], input[type="file"], select, button { 
                width: 100%; padding: 10px; margin: 8px 0; font-size: 15px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; background: #fff; 
            }
            button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 15px; }
            button:hover { background-color: #218838; }
            .note { font-size: 13px; color: #b22222; margin-bottom: 15px; background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; line-height: 1.5; }
            label { font-weight: bold; color: #333; font-size: 13px; }
            h2 { color: #2c3e50; margin-top: 0; border-bottom: 2px solid #28a745; padding-bottom: 8px; text-align: center; }
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
        service_type = request.form.get('service_type')
        saved_file_filenames = []
        
        if service_type == 'print':
            uploaded_files = request.files.getlist('files')
            if not uploaded_files or uploaded_files[0].filename == '':
                return "कोई फाइल नहीं चुनी गई! <a href='/service/print'>वापस जाएं</a>"
            for file in uploaded_files:
                if file and file.filename != '':
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(file_path)
                    saved_file_filenames.append(file.filename)
            
            cust_name = "सामान्य ग्राहक (सेल्फ प्रिंट)"
            cust_mobile = "लागू नहीं"
            cust_email = "लागू नहीं"
            amount = 10 * len(saved_file_filenames)

        elif service_type == 'pan':
            cust_name = request.form.get('cust_name')
            cust_mobile = request.form.get('cust_mobile')
            cust_email = request.form.get('cust_email')
            
            file_aadhar = request.files.get('file_aadhar')
            file_other = request.files.get('file_other')
            
            if not file_aadhar or file_aadhar.filename == '' or not file_other or file_other.filename == '':
                return "कृपया दोनों दस्तावेज (आधार और अन्य आईडी) अपलोड करें! <a href='/service/pan'>वापस जाएं</a>"
            
            for file in [file_aadhar, file_other]:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_file_filenames.append(file.filename)
                
            amount = 30  # पैन कार्ड सेवा शुल्क

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
                    background: rgba(255, 255, 255, 0.95); 
                    max-width: 400px; 
                    margin: auto; 
                    padding: 20px; 
                    border-radius: 12px; 
                    box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
                }
                .btn-wait { background-color: #ffc107; color: #333; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; width: 100%; margin-top: 15px; font-weight: bold; cursor: pointer;}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>💳 QR स्कैन करके रुपये भेजें</h2>
                <p><b>सेवा:</b> <span style="text-transform:uppercase; color:#007BFF;">{{ service_type }}</span></p>
                {% if cust_name != "सामान्य ग्राहक (सेल्फ प्रिंट)" %}
                <p><b>आवेदक:</b> {{ cust_name }}</p>
                <p><b>मोबाइल:</b> {{ cust_mobile }}</p>
                <p><b>जीमेल:</b> {{ cust_email }}</p>
                {% endif %}
                <p><b>कुल राशि:</b> <span style="font-size: 26px; color: #d9534f;">₹{{ amount }}</span></p>
                
                <img src="{{ qr_url }}" alt="UPI QR Code" style="border: 2px solid #ddd; border-radius: 8px; padding: 5px; background: white;">
                
                <form action="/submit-request" method="POST">
                    <input type="hidden" name="filenames" value="{{ filenames_string }}">
                    <input type="hidden" name="amount" value="{{ amount }}">
                    <input type="hidden" name="service_type" value="{{ service_type }}">
                    <input type="hidden" name="cust_name" value="{{ cust_name }}">
                    <input type="hidden" name="cust_mobile" value="{{ cust_mobile }}">
                    <input type="hidden" name="cust_email" value="{{ cust_email }}">
                    <button type="submit" class="btn-wait">⏳ मैंने पेमेंट कर दिया है, सूचना भेजें</button>
                </form>
            </div>
        </body>
        </html>
        ''', amount=amount, qr_url=qr_api_url, filenames_string=filenames_string, service_type=service_type, cust_name=cust_name, cust_mobile=cust_mobile, cust_email=cust_email)
    except Exception as e:
        return f"<h3>त्रुटि: {e}</h3><a href='/'>होम पेज जाएं</a>"


@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        filenames_string = request.form.get('filenames')
        amount = request.form.get('amount')
        service_type = request.form.get('service_type')
        cust_name = request.form.get('cust_name')
        cust_mobile = request.form.get('cust_mobile')
        cust_email = request.form.get('cust_email')
        
        req_id = len(pending_requests) + 1
        request_data = {
            'id': req_id, 
            'filenames': filenames_string, 
            'amount': amount,
            'service_type': service_type,
            'cust_name': cust_name,
            'cust_mobile': cust_mobile,
            'cust_email': cust_email
        }
        pending_requests.append(request_data)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.95); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#d9534f;">⏳ पैमेंट की सूचना दुकानदार को पहुँच गई है!</h2>
                <p style="font-size:18px;">आपकी रिक्वेस्ट एडमिन पैनल पर भेज दी गई है। काम जल्दी ही शुरू किया जाएगा...</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">होम पेज पर वापस जाएं</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/'>वापस जाएं</a>"


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
            
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>दुकानदार लॉगिन</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; background: #222; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-card { background: #333; padding: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.5); width: 300px; text-align: center; }
                input { width: 100%; padding: 10px; margin: 15px 0; font-size: 16px; border-radius: 5px; border: none; box-sizing: border-box; }
                button { width: 100%; padding: 10px; background: #28a745; color: white; border: none; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; }
                .error { color: #ff6b6b; font-size: 14px; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div class="login-card">
                <h2>🔐 BHUARKARKA LOGIN</h2>
                <div class="error">''' + error_msg + '''</div>
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
                files_list = req['filenames'].split(',')
                download_links = ""
                for i, f in enumerate(files_list, 1):
                    download_links += f'<a href="/uploads/{f.strip()}" download style="color:#00bcd4; margin-right:10px; text-decoration:underline;">📥 फाइल {i} डाउनलोड करें</a><br>'

                cust_info_block = ""
                if req['service_type'] == 'pan':
                    cust_info_block = f'''
                        <p><b>आवेदक का नाम:</b> <span style="color:#00e676; font-size:17px;">{req['cust_name']}</span></p>
                        <p><b>मोबाइल नंबर:</b> <span style="color:#ffeb3b;">{req['cust_mobile']}</span></p>
                        <p><b>जीमेल:</b> <span style="color:#ff9800;">{req['cust_email']}</span></p>
                    '''

                cards_html += f'''
                    <div style="background: rgba(0, 0, 0, 0.85); padding: 15px; margin: 15px auto; max-width: 450px; border-radius: 10px; border-left: 5px solid #28a745; text-align: left;">
                        <p><b>रिक्वेस्ट नंबर:</b> #{req['id']}</p>
                        <p><b>सेवा प्रकार:</b> <span style="color:#ffeb3b; text-transform:uppercase; font-weight:bold;">{req['service_type']}</span></p>
                        {cust_info_block}
                        <p><b>रुपया प्राप्त:</b> <span style="color:#4cd137;">₹{req['amount']}</span></p>
                        <p><b>दस्तावेज़ फाइलें:</b><br>{download_links}</p>
                        <form action="/approve-print" method="POST">
                            <input type="hidden" name="req_index" value="{idx}">
                            <button type="submit" style="background: #28a745; color: white; border: none; padding: 10px 15px; font-size: 15px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px;">✅ काम पूरा हुआ / अप्रूव करें</button>
                        </form>
                    </div>
                '''

        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>BHUARKARKA - एडमिन पैनल</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="refresh" content="3">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('/kiosk-image/prakash 2.jfif') no-repeat center center fixed; 
                    background-size: cover; 
                    color: #fff; 
                    padding: 15px; 
                    text-align: center; 
                    min-height: 100vh;
                }
            </style>
        </head>
        <body>
            <h2>🛡️ BHUARKARKA SERVICES - लाइव रिक्वेस्ट पैनल</h2>
            ''' + cards_html + '''
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