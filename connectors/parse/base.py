import logging
import yaml
import json
import sys
import requests

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

class ParseWrapper:
    def __init__ (self, configfile=None):
        if configfile is None:
            self.configfile = '/opt/bernie/config.yml'
        else:
            self.configfile = configfile

        self.config = self.get_config()
        c = self.config['parse']

        self.headers = \
        {
            'X-Parse-Application-Id': c['parse_application_id'],
            'X-Parse-REST-API-Key': c['parse_rest_api_key'],
            'Content-Type': 'application/json'
        }
        self.default_channels = c['parse_default_channels']
        self.base_uri = 'https://api.parse.com/1'

    def push (self, alert, action, identifier):
        '''
        use `openNewsArticle` for both press releases and articles
        use `openVideo` for videos
        '''
        payload = \
        {
            "where": {},
            "data" : {
                "action": action,
                "aps": {
                    "alert": alert,
                    "sound": "default",
                },
                "identifier": identifier
            }
        }

        msg = "Sending {0}"
        logging.info(msg.format(alert))

        try:
            r = requests.post(self.base_uri + '/push', json=payload, headers=self.headers, timeout=30.0)
        except requests.exceptions.RequestException as e:
            logging.info(e)
            return False

        logging.info(r.text)
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
        alert = "I am target to Everyone hopefully"
        identifier = "e8021067-ece6-424e-acd8-5bd4d9b4f011"
        action = "openNewsArticle"
    	self.push(alert, action, identifier)

if __name__ == "__main__":
    bernie = ParseWrapper()
    bernie.test()
