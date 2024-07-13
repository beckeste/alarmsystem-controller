from flask_restful import Resource

alarm_system_status = {'status': 'disarmed'}

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
        if alarm_system_status['status'] != 'alarming':
            alarm_system_status['status'] = 'armed'
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
        return alarm_system_status, 200

class AlarmResource(Resource):
    def post(self):
        """
        Trigger the alarm
        ---
        responses:
          200:
            description: Alarm triggered
        """
        if alarm_system_status['status'] == 'armed':
            alarm_system_status['status'] = 'alarming'
        return alarm_system_status, 200