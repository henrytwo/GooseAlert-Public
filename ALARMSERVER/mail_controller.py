import env
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import traceback

e = env.get_env()

def send_mail(subject, message, files):

    try:
        # Courtesy of https://stackoverflow.com/questions/3362600/how-to-send-email-attachments

        print('%s:%s' % (e['SMTP_ADDRESS'], e['SMTP_PORT']))
        server = smtplib.SMTP('%s:%s' % (e['SMTP_ADDRESS'], e['SMTP_PORT']))
        server.starttls()
        server.login(e['SMTP_USERNAME'], e['SMTP_PASSWORD'])

        msg = MIMEMultipart()
        msg['From'] = e['SMTP_CONTACT']
        msg['To'] = e['SMTP_RECIPIENT']
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(message))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        #print(msg)

        server.sendmail(e['SMTP_CONTACT'], e['SMTP_RECIPIENT'], msg.as_string())

        server.close()

    except:
        traceback.print_exc()
        print('Couldn\'t send mail!')