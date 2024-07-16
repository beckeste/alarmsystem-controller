import requests
import threading
import time
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.orm import sessionmaker
from models import Sensor, engine
from datetime import datetime
from shared import alarm_system_status, ALARM_LEVELS
from resources.alarmsystem import update_alarm_status

Session = sessionmaker(bind=engine)
session = Session()

def trigger_sensor(sensor, endpoint):
    time.sleep(2)
    try:
        response = requests.get(f'http://{sensor.ip_address}{endpoint}')
        if response.status_code != 200:
            print(f'Failed to trigger sensor at {sensor.ip_address} with endpoint {endpoint}')
    except requests.exceptions.RequestException as e:
        print(f'Exception occurred while triggering sensor at {sensor.ip_address} with endpoint {endpoint}: {str(e)}')

class SensorListResource(Resource):
    def get(self):
        """
        Get the list of all sensors
        ---
        responses:
          200:
            description: A list of sensors
        """
        sensors = session.query(Sensor).all()
        return [{
            'mac_address': sensor.mac_address,
            'name': sensor.name,
            'last_updated': sensor.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': sensor.ip_address,
            'capabilities': {
                'buzzer': sensor.buzzer,
                'door_sensor': sensor.door_sensor,
                'shutter_sensor': sensor.shutter_sensor,
                'motion_sensor': sensor.motion_sensor,
                'siren': sensor.siren
            },
            'states': {
                'door_open': sensor.door_open,
                'shutter_open': sensor.shutter_open,
                'motion_detected': sensor.motion_detected,
                'siren_on': sensor.siren_on,
                'buzzer_on': sensor.buzzer_on,
                'armed': sensor.armed
            }
        } for sensor in sensors], 200

    def post(self):
        """
        Add a new sensor
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - mac_address
                - ip_address
              properties:
                mac_address:
                  type: string
                name:
                  type: string
                ip_address:
                  type: string
                capabilities:
                  type: object
                  properties:
                    buzzer:
                      type: boolean
                    door_sensor:
                      type: boolean
                    shutter_sensor:
                      type: boolean
                    motion_sensor:
                      type: boolean
                    siren:
                      type: boolean
                states:
                  type: object
                  properties:
                    door_open:
                      type: boolean
                    shutter_open:
                      type: boolean
                    motion_detected:
                      type: boolean
                    siren_on:
                      type: boolean
                    buzzer_on:
                      type: boolean
                    armed:
                      type: boolean
        responses:
          201:
            description: Sensor created successfully
          409:
            description: Sensor with the given MAC address already exists
        """
        parser = reqparse.RequestParser()
        parser.add_argument('mac_address', required=True)
        parser.add_argument('name', required=False)
        parser.add_argument('ip_address', required=True)
        parser.add_argument('capabilities', type=dict, required=False, location='json')
        parser.add_argument('states', type=dict, required=False, location='json')
        args = parser.parse_args()
        mac_address = args['mac_address']
        ip_address = args['ip_address']

        # Default leeres Wörterbuch für states, falls nicht bereitgestellt
        states = args['states'] or {}

        existing_sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if existing_sensor:
            return {'message': f'Sensor with MAC address {mac_address} already exists'}, 409

        new_sensor = Sensor(
            mac_address=mac_address,
            name=args['name'] or '',
            ip_address=ip_address,
            buzzer=args['capabilities'].get('buzzer', False),
            door_sensor=args['capabilities'].get('door_sensor', False),
            shutter_sensor=args['capabilities'].get('shutter_sensor', False),
            motion_sensor=args['capabilities'].get('motion_sensor', False),
            siren=args['capabilities'].get('siren', False),
            door_open=states.get('door_open', False),
            shutter_open=states.get('shutter_open', False),
            motion_detected=states.get('motion_detected', False),
            siren_on=states.get('siren_on', False),
            buzzer_on=states.get('buzzer_on', False),
            armed=states.get('armed', False)
        )
        session.add(new_sensor)
        session.commit()
        return {
            'mac_address': new_sensor.mac_address,
            'name': new_sensor.name,
            'last_updated': new_sensor.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': new_sensor.ip_address,
            'capabilities': {
                'buzzer': new_sensor.buzzer,
                'door_sensor': new_sensor.door_sensor,
                'shutter_sensor': new_sensor.shutter_sensor,
                'motion_sensor': new_sensor.motion_sensor,
                'siren': new_sensor.siren
            },
            'states': {
                'door_open': new_sensor.door_open,
                'shutter_open': new_sensor.shutter_open,
                'motion_detected': new_sensor.motion_detected,
                'siren_on': new_sensor.siren_on,
                'buzzer_on': new_sensor.buzzer_on,
                'armed': new_sensor.armed
            }
        }, 201
    
class SensorResource(Resource):
    def get(self, mac_address):
        """
        Get a sensor by MAC address
        ---
        parameters:
          - name: mac_address
            in: path
            type: string
            required: true
        responses:
          200:
            description: Sensor data
            schema:
              $ref: '#/definitions/Sensor'
          404:
            description: Sensor not found
        """
        sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if sensor:
            return {
                'mac_address': sensor.mac_address,
                'name': sensor.name,
                'last_updated': sensor.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': sensor.ip_address,
                'capabilities': {
                    'buzzer': sensor.buzzer,
                    'door_sensor': sensor.door_sensor,
                    'shutter_sensor': sensor.shutter_sensor,
                    'motion_sensor': sensor.motion_sensor,
                    'siren': sensor.siren
                },
                'states': {
                    'door_open': sensor.door_open,
                    'shutter_open': sensor.shutter_open,
                    'motion_detected': sensor.motion_detected,
                    'siren_on': sensor.siren_on,
                    'buzzer_on': sensor.buzzer_on,
                    'armed': sensor.armed
                }
            }, 200
        return {'message': 'Sensor not found'}, 404

    def put(self, mac_address):
        """
        Update a sensor by MAC address
        ---
        parameters:
          - name: mac_address
            in: path
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                name:
                  type: string
                ip_address:
                  type: string
                capabilities:
                  type: object
                  properties:
                    buzzer:
                      type: boolean
                    door_sensor:
                      type: boolean
                    shutter_sensor:
                      type: boolean
                    motion_sensor:
                      type: boolean
                    siren:
                      type: boolean
                states:
                  type: object
                  properties:
                    door_open:
                      type: boolean
                    shutter_open:
                      type: boolean
                    motion_detected:
                      type: boolean
                    siren_on:
                      type: boolean
                    buzzer_on:
                      type: boolean
                    armed:
                      type: boolean
        responses:
          200:
            description: Sensor updated successfully
          404:
            description: Sensor not found
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ip_address', required=True)
        parser.add_argument('name', required=False)
        parser.add_argument('capabilities', type=dict, required=False, location='json')
        parser.add_argument('states', type=dict, required=False, location='json')
        args = parser.parse_args()
        sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if sensor:
            tmp_door_open = sensor.door_open
            tmp_shutter_open = sensor.shutter_open
            tmp_motion_detected = sensor.motion_detected

            sensor.last_updated = datetime.utcnow()
            sensor.ip_address = args['ip_address']
            if args['name'] is not None:
                sensor.name = args['name']
            if args['capabilities'] is not None:
                sensor.buzzer = args['capabilities'].get('buzzer', sensor.buzzer)
                sensor.door_sensor = args['capabilities'].get('door_sensor', sensor.door_sensor)
                sensor.shutter_sensor = args['capabilities'].get('shutter_sensor', sensor.shutter_sensor)
                sensor.motion_sensor = args['capabilities'].get('motion_sensor', sensor.motion_sensor)
                sensor.siren = args['capabilities'].get('siren', sensor.siren)
            if args['states'] is not None:
                sensor.door_open = args['states'].get('door_open', sensor.door_open)
                sensor.shutter_open = args['states'].get('shutter_open', sensor.shutter_open)
                sensor.motion_detected = args['states'].get('motion_detected', sensor.motion_detected)
                sensor.siren_on = args['states'].get('siren_on', sensor.siren_on)
                sensor.buzzer_on = args['states'].get('buzzer_on', sensor.buzzer_on)
                sensor.armed = args['states'].get('armed', sensor.armed)
            session.commit()


            #TODO Wenn der Sensor gemeldet hat, shutter_open, dann alarm bei allen Sensoren auslösen
            alarmed = False
            if alarm_system_status["status"] == "armed":
              door_opened = sensor.door_open and not tmp_door_open
              shutter_opened = sensor.shutter_open and not tmp_shutter_open
              motion_detected = sensor.motion_detected and not tmp_motion_detected
              if door_opened or shutter_opened:
                update_alarm_status("medium")
                alarmed = True
              elif motion_detected:
                update_alarm_status("low")
                alarmed = True

            if not alarmed:
              threading.Thread(target=trigger_sensor, args=(sensor, '/initsensor')).start()
            

            return {
                'mac_address': sensor.mac_address,
                'name': sensor.name,
                'last_updated': sensor.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': sensor.ip_address,
                'capabilities': {
                    'buzzer': sensor.buzzer,
                    'door_sensor': sensor.door_sensor,
                    'shutter_sensor': sensor.shutter_sensor,
                    'motion_sensor': sensor.motion_sensor,
                    'siren': sensor.siren
                },
                'states': {
                    'door_open': sensor.door_open,
                    'shutter_open': sensor.shutter_open,
                    'motion_detected': sensor.motion_detected,
                    'siren_on': sensor.siren_on,
                    'buzzer_on': sensor.buzzer_on,
                    'armed': sensor.armed
                }
            }, 200
        return {'message': 'Sensor not found'}, 404

    def delete(self, mac_address):
        """
        Delete a sensor by MAC address
        ---
        parameters:
            - name: mac_address
              in: path
              type: string
              required: true
        responses:
            204:
                description: Sensor deleted successfully
            404:
                description: Sensor not found
        """
        sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if sensor:
            session.delete(sensor)
            session.commit()
            return '', 204
        return {'message': 'Sensor not found'}, 404