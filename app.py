from flask import Flask
from application.database import db
from flask_restful import Resource, Api


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydata.sqlite3'
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api

app, api = create_app()


from application.controllers import *
from application.api import myAPI, listAPI, flagAPI

api.add_resource(myAPI, '/api/data')
api.add_resource(listAPI, '/api/<string:type>')
api.add_resource(flagAPI, '/api/flaglist', '/api/action/<string:action>/<int:id>')






if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)