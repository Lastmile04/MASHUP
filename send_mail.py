from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

def send_mail(to, filename):
    email_address = "mashupdivyam@gmail.com"
    email_password = "ABCDefgh123"

    # create email
    msg = MIMEMultipart()
    msg['Subject'] = "Mashup File"
    msg['From'] = email_address
    msg['To'] = to 

    with open(filename,'rb') as file:
        # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name='Mashup.zip'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)