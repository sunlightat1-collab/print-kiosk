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
                # फाइल के नाम से स्पेस और कौमा (,) हटाकर अंडरस्कोर (_) लगाना
                safe_filename = file.filename.replace(' ', '_').replace(',', '_')
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], safe_filename))
                uploaded_files.append(safe_filename)
                
        filenames_str = ",".join(uploaded_files) if uploaded_files else 'कोई फाइल नहीं'
        
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
                <h2 style="color:#28a745;">✅ आवेदन सफलतापर्वूक जमा हो गया!</h2>
                <p style="font-size:15px; color:#333;">आपका डेटा और पेमेंट UTR नंबर हमारे पास सुरक्षित पहुंच गया है। सबमिट की गई फाइल Admin पैनल में सेव हो गई है। जल्द ही आपका काम कर दिया जाएगा।</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">🏠 होम पेज पर वापस जाएं</a>
            </div>
        '''
    except Exception as e:
        return f"<h3>एरर आया: {e}</h3><a href='/'>वापस जाएं</a>"
