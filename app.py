from flask import Flask
from flask_restx import Api
from views import ns

app = Flask(__name__)
api = Api(app)
api.add_namespace(ns)

if __name__ == '__main__':
    app.run(debug=True)
