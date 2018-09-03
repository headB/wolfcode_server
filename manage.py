from flask import Flask
from network_service.v_1_0 import network_api,register_api,postman_api

app = Flask(__name__)

app.register_blueprint(network_api,url_prefix="/network")

if __name__ == "__main__":

    app.run(debug=True)