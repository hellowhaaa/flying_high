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


@app.route('/send', methods=['POST'])
def send_email():
    print("1")
    try:
        print("x")
        msg = Message(subject="Hello",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[test_recipients], # replace with your email for testing
                    body="This is a test email I sent with Gmail and Python!222")
        mail.send(msg)
        return 'hi'
    except Exception as e:
        print('3')
        print(str(e))
        

if __name__ == '__main__':
    app.run(debug=True, port=9000)


