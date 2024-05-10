import os
from flask import Flask, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
env_path = os.path.join(os.getcwd(), 'server', '.env')
load_dotenv(env_path)

mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
test_recipients = os.getenv('TEST_RECIPIENTS')
print(mail_password)
print(test_recipients)

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": mail_username,
    "MAIL_PASSWORD": mail_password
}
app.config.update(mail_settings)
mail = Mail(app)


@app.route('/send_email', methods=['POST'])
def send_email():
    print("1")
    try:
        email = request.form.get('email')
        scheduled_depart_time = request.form.get('scheduled_depart_time')
        status = request.form.get('status')
        airline_code = request.form.get('airline_code')
        username = request.form.get('username')
        print("data", (email, scheduled_depart_time, status))
        print("x")
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],  # replace with your email for testing
                      body=f"Hi! {username}  your flight {airline_code} 's time has been changed. \
                      Your flight's scheduled_depart_time {scheduled_depart_time} which status is now {status}. ")
        mail.send(msg)
        response_data = {
            "status": "Success"}
        return response_data
    except Exception as e:
        print('3')
        print(str(e))
        

if __name__ == '__main__':
    app.run(debug=True)


