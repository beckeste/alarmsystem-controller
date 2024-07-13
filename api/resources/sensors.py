from flask import request
from flask_restful import Resource, reqparse
from datetime import datetime

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
          - name: mac_address
            in: body
            type: string
            required: true
            description: The sensor MAC address
        responses:
          201:
            description: Sensor created
        """
        parser = reqparse.RequestParser()
        parser.add_argument('mac_address', required=True)
        args = parser.parse_args()
        mac_address = args['mac_address']
        ip_address = request.remote_addr
        sensors[mac_address] = {'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'ip_address': ip_address}
        return sensors[mac_address], 201

class SensorResource(Resource):
    def get(self, mac_address):
        """
        Get a specific sensor
        ---
        parameters:
          - name: mac_address
            in: path
            type: string
            required: true
            description: The sensor MAC address
        responses:
          200:
            description: A specific sensor
        """
        if mac_address in sensors:
            return sensors[mac_address], 200
        return {'message': 'Sensor not found'}, 404

    def put(self, mac_address):
        """
        Update a specific sensor
        ---
        parameters:
          - name: mac_address
            in: path
            type: string
            required: true
            description: The sensor MAC address
        responses:
          200:
            description: Sensor updated
        """
        if mac_address in sensors:
            sensors[mac_address]['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            sensors[mac_address]['ip_address'] = request.remote_addr  # Update the IP address if needed
            return sensors[mac_address], 200
        return {'message': 'Sensor not found'}, 404

    def delete(self, mac_address):
        """
        Delete a specific sensor
        ---
        parameters:
          - name: mac_address
            in: path
            type: string
            required: true
            description: The sensor MAC address
        responses:
          200:
            description: Sensor deleted
        """
        if mac_address in sensors:
            del sensors[mac_address]
            return '', 204
        return {'message': 'Sensor not found'}, 404