from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, session
import os
import pypdf
import socket

app = Flask(__name__)
app.secret_key = 'prakash_print_kiosk_secret_key'  # सत्र (Session) चालू रखने के लिए जरूरी है

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPI_ID = "Q508475385@ybl"
MERCHANT_NAME = "Print Kiosk"

pending_requests = []
print_queue = []  # लोकल एजेंट के लिए प्रिंट कतार

# फोल्डर से फाइल दिखाने के लिए रूट
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
    <title>राजस्थानी स्मार्ट प्रिंट कियोस्क</title>
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
            background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('/kiosk-image/card.jpg') no-repeat center center; 
            background-size: cover;
            max-width: 420px; 
            margin: auto; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3); 
        }
        select, input[type="file"], button { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; background: rgba(255,255,255,0.9); }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #218838; }
        .price-box { font-size: 18px; color: #333; margin: 10px 0; text-align: left; background: rgba(238, 242, 243, 0.9); padding: 12px; border-radius: 5px;}
        .note { font-size: 13px; color: #444; text-align: left; margin-top: -5px; margin-bottom: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🖨️ खम्मा घणी सा🙏</h2>
        <form action="/checkout" method="POST" enctype="multipart/form-data">
            
            <label style="float:left; font-weight:bold;">📁 थारो डॉक्यूमेंट लगाओ... (ज्यादा सू ज्यादा 5):</label>
            <input type="file" name="files" id="fileInput" accept=".pdf,.jpg,.jpeg,.jfif" multiple required onchange="updateInfo()">
            <div class="note">💡 ध्यान राखोजे: आप एकसाथ पाँच फोटू या पीडीएफ लगा सको हो!</div>
            
            <label style="float:left; font-weight:bold; margin-top:5px;">⚙️ किस्यो कै प्रिंट चहीजै:</label>
            <select name="print_type" id="print_type" onchange="updateInfo()">
                <option value="bw">📄 ब्लैक एंड व्हाइट (काली)</option>             
            </select>

            <div class="price-box" id="priceDisplay">
                <b>रुपया:</b> आगे बढ़ो फेर पिसा बता स्याँ🙌
            </div>

            <button type="submit">🚀 आगे बड़ों</button>
        </form>
    </div>

    <script>
        function updateInfo() {
            var fileInput = document.getElementById("fileInput");
            var count = fileInput.files.length;
            if (count > 5) {
                alert("⚠️ खम्मा घणी सा! एक बार में सिर्फ 5 फाइल ही चुन सको हो!");
                fileInput.value = ""; 
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
        print_type = request.form.get('print_type')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            return "कोई फाइल कोनी चुणी! <a href='/'>पाछा जाओ</a>"
        
        saved_file_filenames = []
        total_pages = 0
        is_photo_upload = False

        for file in uploaded_files:
            if file and file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_file_filenames.append(file.filename)
                
                filename_lower = file.filename.lower()
                if filename_lower.endswith(('.jpg', '.jpeg', '.png', '.jfif')):
                    is_photo_upload = True
                elif filename_lower.endswith('.pdf'):
                    try:
                        reader = pypdf.PdfReader(file_path)
                        total_pages += len(reader.pages)
                    except:
                        total_pages += 1

        if print_type == 'photos' or is_photo_upload:
            amount = len(saved_file_filenames) * 10
        elif print_type == 'color':
            amount = max(1, total_pages) * 10
        elif print_type == 'aadhaar':
            amount = len(saved_file_filenames) * 10
        elif print_type == 'bw':
            if total_pages <= 3: amount = 10
            elif total_pages <= 5: amount = 20
            elif total_pages <= 10: amount = 30
            else: amount = 30 + (total_pages - 10) * 3
        else:
            amount = 10

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
                    background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('/kiosk-image/card.jpg') no-repeat center center; 
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
                    <button type="submit" class="btn-wait">⏳ मैं पैमेंट कर दियो है, दुकानदार ने सूचणा भेजो</button>
                </form>
            </div>
        </body>
        </html>
        ''', amount=amount, qr_url=qr_api_url, filenames_string=filenames_string)
    except Exception as e:
        return f"<h3>काई गलती है: {e}</h3><a href='/'>पाछा जाओ</a>"


@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        filenames_string = request.form.get('filenames')
        amount = request.form.get('amount')
        
        req_id = len(pending_requests) + 1
        request_data = {'id': req_id, 'filenames': filenames_string, 'amount': amount}
        pending_requests.append(request_data)

        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:20px; background:rgba(255,255,255,0.9); max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.3);">
                <h2 style="color:#d9534f;">⏳ पैमेंट री सूचणा दुकानदारा कन्ने पुग गी है!</h2>
                <p style="font-size:18px;">थारो पैमेंट चेक हो रिया है। थोड़ी देर में प्रिंट निकल जावेलो...</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">होम पेज पाछा जाओ</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर: {e}</h3><a href='/'>पाछा जाओ</a>"


# 1. एडमिन लॉगिन पेज
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error_msg = ""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '1234':  # आप चाहें तो यहाँ '1234' की जगह अपना कोई दूसरा पासवर्ड रख सकते हैं
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
                button:hover {{ background: #218838; }}
                .error {{ color: #ff6b6b; font-size: 14px; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="login-card">
                <h2>🔐 दुकानदार लॉगिन</h2>
                <div class="error">{error_msg}</div>
                <form method="POST">
                    <input type="password" name="password" placeholder="पासवर्ड दर्ज करें" required autofocus>
                    <button type="submit">लॉगिन करें</button>
                </form>
            </div>
        </body>
        </html>
    '''


# 2. मुख्य एडमिन पैनल (अब इस पर पासवर्ड का ताला लग चुका है)
@app.route('/admin-panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    try:
        cards_html = ""
        has_requests = "false"
        
        if not pending_requests:
            cards_html = "<p style='color: #ddd;'>अभी कोई नई रिक्वेस्ट कोनी है...</p>"
        else:
            has_requests = "true"
            for idx, req in enumerate(pending_requests):
                cards_html += f'''
                    <div style="background: rgba(0, 0, 0, 0.85); padding: 15px; margin: 10px auto; max-width: 400px; border-radius: 8px; border-left: 5px solid #28a745; text-align: left;">
                        <p><b>रिक्वेस्ट नंबर:</b> #{req['id']}</p>
                        <p><b>रुपया आया:</b> <span style="color:#4cd137;">₹{req['amount']}</span></p>
                        <form action="/approve-print" method="POST">
                            <input type="hidden" name="req_index" value="{idx}">
                            <button type="submit" style="background: #28a745; color: white; border: none; padding: 10px 15px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px;">✅ पैमेंट पक्को कर ने प्रिंट चालू करो</button>
                        </form>
                    </div>
                '''

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>दुकानदार एडमिन पैनल</title>
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
            <script>
                function playBeep() {{
                    try {{
                        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const oscillator = audioCtx.createOscillator();
                        const gainNode = audioCtx.createGain();
                        oscillator.type = 'sine';
                        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
                        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
                        oscillator.connect(gainNode);
                        gainNode.connect(audioCtx.destination);
                        oscillator.start();
                        oscillator.stop(audioCtx.currentTime + 0.3);
                    }} catch(e) {{}}
                }}

                window.onload = function() {{
                    var hasReq = {has_requests};
                    var lastCount = localStorage.getItem('reqCount') || 0;
                    var currentCount = {len(pending_requests)};

                    if (currentCount > lastCount) {{
                        playBeep();
                    }}
                    localStorage.setItem('reqCount', currentCount);
                }};
            </script>
        </head>
        <body>
            <h2>🛡️ लाइव प्रिंट रिक्वेस्ट (राजस्थानी)</h2>
            <p>पेंडिंग अप्रूवल:</p>
            {cards_html}
            <br>
            <a href="/admin-logout" style="color: #ff6b6b; text-decoration: none; background: rgba(0,0,0,0.7); padding: 8px 15px; border-radius: 5px; font-weight: bold;">🔒 लॉगआउट (बाहर निकलें)</a>
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
            
            return "<h3 style='color:green; text-align:center; margin-top:50px; background:white; padding:20px; max-width:400px; margin:50px auto; border-radius:10px;'>🎉 प्रिंट कमांड कतार में भेज दी है! <a href='/admin-panel' style='color:#007BFF;'>पाछा एडमिन पैनल में जाओ</a></h3>"
        
        return "रिक्वेस्ट पहिले ही पूरी हो चुकी है! <a href='/admin-panel'>पाछा जाओ</a>"
    except Exception as e:
        return f"<h3>प्रिंटिंग एरर: {e}</h3><a href='/admin-panel'>पाछा जाओ</a>"


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