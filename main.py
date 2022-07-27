""" Startup file for Google Cloud deployment or local webserver"""
from flathunter.idmaintainer import IdMaintainer
from flathunter.googlecloud_idmaintainer import GoogleCloudIdMaintainer
from flathunter.web_hunter import WebHunter
from flathunter.config import Config

from flathunter.web import app

config = Config()

if __name__ == '__main__':
    # Use the SQLite DB file if we are running locally
    id_watch = IdMaintainer(f'{config.database_location()}/processed_ids.db')
else:
    # Use Google Cloud DB if we run on the cloud
    id_watch = GoogleCloudIdMaintainer()

hunter = WebHunter(config, id_watch)

app.config["HUNTER"] = hunter
if 'website' in config:
    app.secret_key = config['website']['session_key']
    app.config["DOMAIN"] = config['website']['domain']
    app.config["BOT_NAME"] = config['website']['bot_name']
else:
    app.secret_key = b'Not a secret'

notifiers = config["notifiers"]
if "telegram" in notifiers:
    app.config["BOT_TOKEN"] = config['telegram']['bot_token']
if "mattermost" in notifiers:
    app.config["MM_WEBHOOK_URL"] = config['mattermost']['webhook_url']

if __name__ == '__main__':
    if 'website' in config:
        listen = config['website']['listen']
        app.run(host=listen['host'], port=listen['port'], debug=True)
    else:
        app.run(debug=True)
