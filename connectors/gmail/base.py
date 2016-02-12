import logging
import yaml
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

class GmailWrapper:
    def __init__ (self, configfile=None):
        if configfile is None:
            self.configfile = '/opt/bernie/config.yml'
        else:
            self.configfile = configfile

        self.config = self.get_config()
        c = self.config['gmail']

    def send_mail(self, subject, body):
        c = self.config['gmail']
        recipients = c['recipients']

        mmsg = MIMEMultipart()

        if isinstance(recipients, list):
            mmsg['To'] = ", ".join(recipients)
        else:
            mmsg['To'] = recipients
            recipients = [recipients]

        mmsg['From'] = c['email']
        mmsg['Subject'] = subject
        mmsg.attach(MIMEText(body, 'plain'))
        try:
            conn = smtplib.SMTP(c['server'], c['port'])
            conn.starttls()
            conn.login(c['email'], c['password'])
            conn.sendmail(c['email'], recipients, mmsg.as_string())
            conn.quit()
            msg = "Successfully sent email: {0}"
            logging.info(msg.format(mmsg['Subject']))
        except smtplib.SMTPException as e:
            msg = "Error sending email: {0} {1}"
            logging.info(msg.format(mmsg['Subject']), e)
            return False

        return True

    def get_config(self):
        try:
            with open(self.configfile, 'r') as f:
                conf = yaml.load(f)
        except IOError:
            msg = "Could not open config file: {0}"
            logging.info(msg.format(self.configfile))
            sys.exit(1)
        else:
            return conf


    def test(self):
        self.send_mail('subject!', 'whats up self, here is a link http://www.google.com')

if __name__ == "__main__":
    bernie = GmailWrapper()
    bernie.test()
