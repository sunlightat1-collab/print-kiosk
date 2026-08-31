@app.route('/service/<service_name>')
def service_page(service_name):
    if not get_shop_status():
        return '''
            <div style="text-align:center; font-family:Arial; margin-top:50px; padding:30px; background:#fff; max-width:400px; margin:50px auto; border-radius:10px; box-shadow:0 0 15px rgba(0,0,0,0.3);">
                <h2 style="color:#d9534f;">❌ दुकान अभी बंद है!</h2>
                <p>फिलहाल यह सेवा उपलब्ध नहीं है। कृपया दुकान खुलने का इंतजार करें।</p>
                <br><a href="/" style="padding:10px 20px; background:#007BFF; color:white; text-decoration:none; border-radius:5px;">मुख्य पृष्ठ पर जाएं</a>
            </div>
        '''
    
    # यहाँ हर सर्विस के फॉर्म का डिजाइन/पेज खुलेगा
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{service_name.upper()} - BHUARKARKA SERVICES</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f7f6; padding: 20px; text-align: center; }}
            .form-box {{ max-width: 500px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: left; }}
            input, select {{ width: 100%%; padding: 10px; margin: 8px 0 15px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }}
            label {{ font-weight: bold; color: #333; font-size: 14px; }}
            .btn-submit {{ background: #28a745; color: white; padding: 12px; border: none; width: 100%%; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .btn-back {{ display: inline-block; margin-top: 15px; color: #007BFF; text-decoration: none; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="form-box">
            <h2 style="text-align: center; color: #2c3e50; text-transform: uppercase;">📄 {service_name} Form</h2>
            <form action="/submit-request" method="POST">
                <input type="hidden" name="service_type" value="{service_name}">
                
                <label>पूरा नाम (Full Name):</label>
                <input type="text" name="cust_name" placeholder="अपना नाम लिखें" required>
                
                <label>मोबाइल नंबर (Mobile Number):</label>
                <input type="text" name="cust_mobile" placeholder="10 अंकों का मोबाइल नंबर" required>
                
                <label>ईमेल (Email - वैकल्पिक):</label>
                <input type="email" name="cust_email" value="kiosk@bhuarkarka.com">
                
                <label>शुल्क / राशि (Amount in ₹):</label>
                <input type="number" name="amount" value="50" required>
                
                <label>फाइल का नाम / विवरण (File Details):</label>
                <input type="text" name="filenames" placeholder="दस्तावेज़ का नाम दर्ज करें" required>
                
                <button type="submit" class="btn-submit">🚀 फॉर्म सबमिट करें</button>
            </form>
            <div style="text-align: center;">
                <a href="/" class="btn-back">⬅ होमपेज पर वापस जाएं</a>
            </div>
        </div>
    </body>
    </html>
    '''
