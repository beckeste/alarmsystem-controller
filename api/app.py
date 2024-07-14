from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_cors import CORS
from resources.sensors import SensorListResource, SensorResource
from resources.alarmsystem import AlarmSystemResource, ArmResource, DisarmResource, AlarmResource

app = Flask(__name__)
swagger = Swagger(app)
CORS(app, resources={r"/*": {"origins": "*"}})  # CORS für alle Routen und Ursprünge erlauben

api = Api(app)

api.add_resource(SensorListResource, '/sensors')
api.add_resource(SensorResource, '/sensors/<string:mac_address>')
api.add_resource(AlarmSystemResource, '/alarmsystem')
api.add_resource(ArmResource, '/alarmsystem/arm')
api.add_resource(DisarmResource, '/alarmsystem/disarm')
api.add_resource(AlarmResource, '/alarmsystem/alarm/<string:level>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)