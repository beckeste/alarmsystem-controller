import requests
import threading
import time
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.orm import sessionmaker
from models import Sensor, engine
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()

def initialize_sensor(ip_address):
    time.sleep(2)  # 2 Sekunden warten, bevor der Sensor initialisiert wird
    try:
        response = requests.get(f'http://{ip_address}/initsensor')
        if response.status_code != 200:
            print(f'Failed to initialize sensor at {ip_address}')
    except requests.exceptions.RequestException as e:
        print(f'Exception occurred while initializing sensor at {ip_address}: {str(e)}')

class SensorListResource(Resource):
    def get(self):
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
            }
        } for sensor in sensors], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('mac_address', required=True)
        parser.add_argument('name', required=False)
        parser.add_argument('ip_address', required=True)  # IP-Adresse als Parameter hinzufügen
        parser.add_argument('capabilities', type=dict, required=False, location='json')  # Fähigkeiten als Parameter hinzufügen
        args = parser.parse_args()
        mac_address = args['mac_address']
        ip_address = args['ip_address']

        # Überprüfen, ob die MAC-Adresse bereits vorhanden ist
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
            siren=args['capabilities'].get('siren', False)
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
            }
        }, 201

class SensorResource(Resource):
    def get(self, mac_address):
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
                }
            }, 200
        return {'message': 'Sensor not found'}, 404

    def put(self, mac_address):
        parser = reqparse.RequestParser()
        parser.add_argument('ip_address', required=True)  # IP-Adresse als erforderlichen Parameter hinzufügen
        parser.add_argument('name', required=False)
        parser.add_argument('capabilities', type=dict, required=False, location='json')
        args = parser.parse_args()
        sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if sensor:
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
            session.commit()

            # Starte die Initialisierung des Sensors in einem separaten Thread mit Verzögerung
            threading.Thread(target=initialize_sensor, args=(sensor.ip_address,)).start()

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
                }
            }, 200
        return {'message': 'Sensor not found'}, 404

    def delete(self, mac_address):
        sensor = session.query(Sensor).filter(Sensor.mac_address == mac_address).first()
        if sensor:
            session.delete(sensor)
            session.commit()
            return '', 204
        return {'message': 'Sensor not found'}, 404