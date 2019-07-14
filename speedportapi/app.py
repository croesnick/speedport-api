import base64
import configparser
import logging
import os
import sys

from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort

from speedportapi.speedport import Speedport


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Disable `urllib3.connectionpool - DEBUG - ...`
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = Flask(__name__)
api = Api(app)


class Backup(Resource):
    def get(self):
        # password = request.form['password']
        # host = request.form['host']

        data = client.backup()
        if data is None:
            abort(500, message=u'Backup failed for some reason. ¯\\_(ツ)_/¯')

        data_base64 = base64.b64encode(data).decode("utf-8")
        return jsonify({'data': data_base64})


def read_config():
    config = configparser.ConfigParser()
    config.read_file(open('config/config.ini'))

    return config


api.add_resource(Backup, '/backup')

config = read_config()
host = config['DEFAULT'].get('host', os.environ.get('SPEEDPORT_HOST'))
password = config['DEFAULT'].get('password', os.environ.get('SPEEDPORT_ADMIN_PASSWORD'))

client = Speedport(host, password)
client.login()

if __name__ == "__main__":
    app.run(debug=True)
