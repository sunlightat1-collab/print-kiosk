@app.route('/service/<service_name>')
def service_page(service_name):
    # अब यहाँ से दुकान की स्थिति (status) की चेकिंग हटा दी गई है, 
    # ताकि दुकान बंद होने पर भी सभी सर्विसेज हमेशा चालू (ON) रहें।

    if service_name == 'print':
        form_html = '''
            <h2>📄 SELF PRINT SERVICE</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="print">
                <label>📁 डॉक्यूमेंट / फाइल अपलोड करें (केवल PDF या इमेज):</label>
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
            <div class="note">
                <b>📌 जरूरी नियम व दस्तावेज:</b><br>
                1. <b>आधार कार्ड</b> (मुख्य पहचान)<br>
                2. <b>अन्य आईडी</b> (जैसे: 10वीं मार्कशीट / वोटर आईडी आदि)<br>
                <span style="color: #d9534f; font-weight: bold;">⚠️ ध्यान दें: अन्य दस्तावेज में दर्ज आपका नाम और विवरण पूरी तरह से आधार कार्ड के अनुसार ही होना चाहिए।</span>
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pan">
                <label>👤 आवेदक का पूरा नाम (आधार के अनुसार):</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 कॉलम 1: आधार कार्ड अपलोड करें (PDF/Image):</label>
                <input type="file" name="file_aadhar" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 कॉलम 2: अन्य जरूरी आईडी अपलोड करें (PDF/Image):</label>
                <input type="file" name="file_other" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <button type="submit">🚀 ₹200 का भुगतान करें व आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'pvc_aadhar':
        form_html = '''
            <h2>🪪 PVC AADHAR CARD (ओरिजिनल)</h2>
            <div class="note">
                <b>📌 जरूरी नियम व जानकारी:</b><br>
                1. आधार कार्ड या आधार नंबर आवश्यक।<br>
                2. आधार कार्ड से लिंक मोबाइल नंबर पर <b>OTP</b> आएगा।<br>
                3. कुल शुल्क: <b>₹100</b>
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="pvc_aadhar">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर (आधार लिंक्ड - OTP हेतु):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 आधार कार्ड अपलोड करें (PDF/Image):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <button type="submit">🚀 ₹100 का भुगतान करें व आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'bonafide':
        form_html = '''
            <h2>📜 मूल निवास प्रमाण पत्र (Bonafide)</h2>
            <div class="note">
                <b>📌 जरूरी दस्तावेज व नियम:</b><br>
                1. आधार स्वयं एवं पिता का आधार<br>
                2. जन आधार एवं राशन कार्ड<br>
                3. पिता का पहचान पत्र / वोटर लिस्ट<br>
                4. नीचे दिए गए लिंक से **मूलनिवास आवेदन पत्र (Bonafide Form)** डाउनलोड करें, भरकर गवाहों से सत्यापित करवाएं:<br>
                <div style="margin-top: 10px; background: #fff; padding: 8px; border-radius: 4px; text-align: center; border: 1px dashed #007BFF;">
                    📥 <a href="https://raw.githubusercontent.com/sunlightat1-collab/print-kiosk/main/Bonafide-1.pdf" target="_blank" style="color: #007BFF; font-weight: bold; text-decoration: none;">मूलनिवास आवेदन पत्र (फॉर्म PDF) डाउनलोड करें</a>
                </div>
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="bonafide">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 फाइल 1: भरा हुआ मूलनिवास आवेदन पत्र:</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 2: स्वयं व पिता का आधार कार्ड:</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 3: जन आधार व राशन कार्ड:</label>
                <input type="file" name="file_col3" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 4: पिता का पहचान पत्र व वोटर लिस्ट सबूत:</label>
                <input type="file" name="file_col4" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <button type="submit">🚀 मूल निवास प्रमाण पत्र हेतु आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'caste':
        form_html = '''
            <h2>📑 जाति प्रमाण पत्र (Caste Certificate)</h2>
            <div class="note">
                <b>📌 जरूरी दस्तावेज व नियम:</b><br>
                1. आवेदक का आधार कार्ड एवं पिता का आधार कार्ड<br>
                2. जन आधार कार्ड एवं राशन कार्ड<br>
                3. पिता का पहचान पत्र (Voter ID)<br>
                4. पुराना जाति प्रमाण पत्र या जाति प्रूफ (न होने पर सक्षम अधिकारी से रिपोर्ट)<br>
                5. 1993 या 1980 की वोटर लिस्ट, फॉर्म-16 (यदि लागू हो)<br>
                6. नीचे दिए गए लिंक से **जाति प्रमाण पत्र आवेदन फॉर्म** डाउनलोड करें, **2 उत्तरदायी गवाहों के हस्ताक्षर** करवाएं और **पटवारी रिपोर्ट** करवाना सुनिश्चित करें:<br>
                <div style="margin-top: 10px; background: #fff; padding: 8px; border-radius: 4px; text-align: center; border: 1px dashed #007BFF;">
                    📥 <a href="https://raw.githubusercontent.com/sunlightat1-collab/print-kiosk/main/OBC-CASTE.pdf" target="_blank" style="color: #007BFF; font-weight: bold; text-decoration: none;">जाति प्रमाण पत्र आवेदन फॉर्म (PDF) डाउनलोड करें</a>
                </div>
            </div>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="caste">
                <label>👤 आवेदक का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 फाइल 1: भरा हुआ जाति आवेदन पत्र (गवाह व पटवारी रिपोर्ट सहित):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 2: स्वयं व पिता का आधार कार्ड:</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 3: जन आधार व राशन कार्ड:</label>
                <input type="file" name="file_col3" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 फाइल 4: पिता का वोटर आईडी व पुराना जाति प्रमाण पत्र / वोटर लिस्ट (1993/1980):</label>
                <input type="file" name="file_col4" accept=".pdf,.jpg,.jpeg,.jfif" required>
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
                <label>📱 मोबाइल नंबर (आधार लिंक्ड):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज़ 1 (आधार कार्ड):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 दस्तावेज़ 2 (जमाबंदी):</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 दस्तावेज़ 3 (जन आधार):</label>
                <input type="file" name="file_col3" accept=".pdf,.jpg,.jpeg,.jfif" required>
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
                <label>📱 मोबाइल नंबर (आधार लिंक्ड):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज़ 1 (आधार कार्ड):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 दस्तावेज़ 2 (बैंक पासबुक):</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <button type="submit">🚀 SHRAMIK CARD के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'jan_aadhaar':
        form_html = '''
            <h2>🆔 JAN AADHAAR CARD</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="jan_aadhaar">
                <label>👤 मुखिया / आवेदक का नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर:</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज़ 1 (आधार कार्ड):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 दस्तावेज़ 2 (अन्य सहायक दस्तावेज):</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <button type="submit">🚀 JAN AADHAAR के लिए आगे बढ़ें</button>
            </form>
        '''
    elif service_name == 'ayushman':
        form_html = '''
            <h2>🏥 AYUSHMAN CARD (स्वास्थ्य कार्ड)</h2>
            <form action="/checkout" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="service_type" value="ayushman">
                <label>👤 लाभार्थी का पूरा नाम:</label>
                <input type="text" name="cust_name" placeholder="पूरा नाम दर्ज करें" required>
                <label>📱 मोबाइल नंबर (आधार लिंक्ड):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" pattern="[0-9]{10}" required>
                <label>📧 जीमेल (Gmail) पता:</label>
                <input type="text" name="cust_email" placeholder="example@gmail.com" required>
                <label>📁 दस्तावेज़ 1 (आधार कार्ड):</label>
                <input type="file" name="file_col1" accept=".pdf,.jpg,.jpeg,.jfif" required>
                <label>📁 दस्तावेज़ 2 (राशन कार्ड / सूची):</label>
                <input type="file" name="file_col2" accept=".pdf,.jpg,.jpeg,.jfif" required>
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
            button { background-color: #28a745; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 15px; font-family: 'Britannic Bold', Arial, sans-serif; letter-spacing: 0.5px;}
            button:hover { background-color: #218838; }
            .note { font-size: 13px; color: #b22222; margin-bottom: 15px; background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; line-height: 1.5; }
            label { font-weight: bold; color: #333; font-size: 13px; }
            h2 { font-family: 'Britannic Bold', Arial, sans-serif; color: #2c3e50; margin-top: 0; border-bottom: 2px solid #28a745; padding-bottom: 8px; text-align: center; letter-spacing: 0.5px; }
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

