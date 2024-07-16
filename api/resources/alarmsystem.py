import requests
import threading
from flask_restful import Resource
from sqlalchemy.orm import sessionmaker
from models import Sensor, engine
from shared import alarm_system_status, ALARM_LEVELS

Session = sessionmaker(bind=engine)
session = Session()

def update_alarm_status(level):
    """
    Update the alarm status based on the provided level
    """
    if level not in ALARM_LEVELS:
        raise ValueError('Invalid alarm level')

    current_level = alarm_system_status['alarm_level']
    if ALARM_LEVELS[level] > ALARM_LEVELS[current_level]:
        alarm_system_status['status'] = 'alarming'
        alarm_system_status['alarm_level'] = level

    # Trigger sensors based on alarm level
    trigger_sensors = False
    endpoint = ''
    if level == 'medium':
        endpoint = '/startbuzzer'
        trigger_sensors = True
    elif level == 'high':
        endpoint = '/startsirene'
        trigger_sensors = True

    if trigger_sensors:
        sensors = session.query(Sensor).all()
        for sensor in sensors:
            threading.Thread(target=trigger_sensor, args=(sensor, endpoint)).start()


def trigger_sensor(sensor, endpoint):
    try:
        response = requests.get(f'http://{sensor.ip_address}{endpoint}')
        if response.status_code != 200:
            print(f'Failed to trigger sensor at {sensor.ip_address} with endpoint {endpoint}')
    except requests.exceptions.RequestException as e:
        print(f'Exception occurred while triggering sensor at {sensor.ip_address} with endpoint {endpoint}: {str(e)}')

class AlarmSystemResource(Resource):
    def get(self):
        """
        Get the status of the alarm system
        ---
        responses:
          200:
            description: The status of the alarm system
        """
        return alarm_system_status, 200

class ArmResource(Resource):
    def post(self):
        """
        Arm the alarm system
        ---
        responses:
          200:
            description: Alarm system armed
        """
        alarm_system_status['status'] = 'armed'
        alarm_system_status['alarm_level'] = 'none'

        # Trigger all sensors with /arm
        sensors = session.query(Sensor).all()
        for sensor in sensors:
            threading.Thread(target=trigger_sensor, args=(sensor, '/arm')).start()

        return alarm_system_status, 200

class DisarmResource(Resource):
    def post(self):
        """
        Disarm the alarm system
        ---
        responses:
          200:
            description: Alarm system disarmed
        """
        alarm_system_status['status'] = 'disarmed'
        alarm_system_status['alarm_level'] = 'none'

        # Trigger all sensors with /disarm
        sensors = session.query(Sensor).all()
        for sensor in sensors:
            threading.Thread(target=trigger_sensor, args=(sensor, '/disarm')).start()

        return alarm_system_status, 200

class AlarmResource(Resource):
    def post(self, level):
        """
        Trigger the alarm at a specific level
        ---
        parameters:
          - name: level
            in: path
            type: string
            required: true
            description: The alarm level (low, medium, high)
        responses:
          200:
            description: Alarm triggered
        """
        if alarm_system_status['status'] == 'disarmed':
            return {'message': 'Alarm system is disarmed'}, 400
        
        try:
            update_alarm_status(level)
        except ValueError as e:
            return {'message': str(e)}, 400

        return alarm_system_status, 200