import requests
import threading
from flask_restful import Resource
from sqlalchemy.orm import sessionmaker
from models import Sensor, engine

Session = sessionmaker(bind=engine)
session = Session()

alarm_system_status = {'status': 'disarmed', 'alarm_level': 'none'}

ALARM_LEVELS = {
    'none': 0,
    'low': 1,
    'medium': 2,
    'high': 3
}

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
        
        if level not in ALARM_LEVELS:
            return {'message': 'Invalid alarm level'}, 400
        
        current_level = alarm_system_status['alarm_level']
        if ALARM_LEVELS[level] <= ALARM_LEVELS[current_level]:
            return {'message': f'Cannot trigger {level} alarm when current alarm level is {current_level}'}, 400
        
        alarm_system_status['status'] = 'alarming'
        alarm_system_status['alarm_level'] = level

        # Trigger sensors based on alarm level
        sensors = session.query(Sensor).all()
        endpoint = ''
        if level == 'medium':
            endpoint = '/startbuzzer'
        elif level == 'high':
            endpoint = '/startsirene'

        for sensor in sensors:
            threading.Thread(target=trigger_sensor, args=(sensor, endpoint)).start()

        return alarm_system_status, 200