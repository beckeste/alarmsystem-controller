from flask_restful import Resource, reqparse

sensors = {}

class SensorListResource(Resource):
    def get(self):
        """
        Get list of all sensors
        ---
        responses:
          200:
            description: A list of sensors
        """
        return sensors, 200

    def post(self):
        """
        Add a new sensor
        ---
        parameters:
          - name: sensor_id
            in: body
            type: string
            required: true
            description: The sensor ID
        responses:
          201:
            description: Sensor created
        """
        parser = reqparse.RequestParser()
        parser.add_argument('sensor_id', required=True)
        args = parser.parse_args()
        sensor_id = args['sensor_id']
        sensors[sensor_id] = {'status': 'inactive'}
        return sensors[sensor_id], 201

class SensorResource(Resource):
    def get(self, sensor_id):
        """
        Get a specific sensor
        ---
        parameters:
          - name: sensor_id
            in: path
            type: string
            required: true
            description: The sensor ID
        responses:
          200:
            description: A specific sensor
        """
        if sensor_id in sensors:
            return sensors[sensor_id], 200
        return {'message': 'Sensor not found'}, 404

    def put(self, sensor_id):
        """
        Update a specific sensor
        ---
        parameters:
          - name: sensor_id
            in: path
            type: string
            required: true
            description: The sensor ID
          - name: status
            in: body
            type: string
            required: true
            description: The sensor status
        responses:
          200:
            description: Sensor updated
        """
        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True)
        args = parser.parse_args()
        if sensor_id in sensors:
            sensors[sensor_id]['status'] = args['status']
            return sensors[sensor_id], 200
        return {'message': 'Sensor not found'}, 404

    def delete(self, sensor_id):
        """
        Delete a specific sensor
        ---
        parameters:
          - name: sensor_id
            in: path
            type: string
            required: true
            description: The sensor ID
        responses:
          200:
            description: Sensor deleted
        """
        if sensor_id in sensors:
            del sensors[sensor_id]
            return '', 204
        return {'message': 'Sensor not found'}, 404