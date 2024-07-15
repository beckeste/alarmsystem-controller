new Vue({
    el: '#app',
    data: {
        systemStatus: '',
        alarmLevel: '',
        sensors: [],
        apiUrl: `http://${hostIpAddress}:${apiPort}`,
        isEditing: false // Neue Variable hinzugefügt
    },
    methods: {
        armSystem() {
            console.log('Arm system called');
            axios.post(`${this.apiUrl}/alarmsystem/arm`)
                .then(response => {
                    this.systemStatus = response.data.status;
                    this.alarmLevel = response.data.alarm_level;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        disarmSystem() {
            console.log('Disarm system called');
            axios.post(`${this.apiUrl}/alarmsystem/disarm`)
                .then(response => {
                    this.systemStatus = response.data.status;
                    this.alarmLevel = response.data.alarm_level;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        triggerAlarm(level) {
            if (this.systemStatus === 'disarmed') {
                alert('The alarm system is disarmed.');
                return;
            }

            console.log('Trigger alarm called');
            axios.post(`${this.apiUrl}/alarmsystem/alarm/${level}`)
                .then(response => {
                    this.systemStatus = response.data.status;
                    this.alarmLevel = response.data.alarm_level;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        fetchSensors() {
            if (this.isEditing) return; // Liste nicht aktualisieren, wenn bearbeitet wird

            console.log('Fetch sensors called');
            axios.get(`${this.apiUrl}/sensors`)
                .then(response => {
                    this.sensors = response.data.map(sensor => ({
                        mac_address: sensor.mac_address,
                        last_updated: sensor.last_updated,
                        ip_address: sensor.ip_address,
                        name: sensor.name,
                        capabilities: sensor.capabilities,
                        states: sensor.states || {}, // Ensure states is an object
                        editing: false
                    }));
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        deleteSensor(macAddress) {
            console.log('Delete sensor called');
            axios.delete(`${this.apiUrl}/sensors/${macAddress}`)
                .then(() => {
                    this.fetchSensors();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        editSensor(sensor) {
            this.isEditing = true; // Bearbeitungsmodus aktivieren
            sensor.editing = true;
        },
        updateSensor(sensor) {
            console.log('Update sensor called');
            axios.put(`${this.apiUrl}/sensors/${sensor.mac_address}`, {
                name: sensor.name,
                ip_address: sensor.ip_address,
                capabilities: sensor.capabilities,
                states: sensor.states
            })
                .then(() => {
                    sensor.editing = false;
                    this.isEditing = false; // Bearbeitungsmodus deaktivieren
                    this.fetchSensors();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        cancelEdit(sensor) {
            sensor.editing = false;
            this.isEditing = false; // Bearbeitungsmodus deaktivieren
            this.fetchSensors(); // Laden Sie die Sensoren erneut, um die ursprünglichen Werte wiederherzustellen
        },
        fetchSystemStatus() {
            console.log('Fetch system status called');
            axios.get(`${this.apiUrl}/alarmsystem`)
                .then(response => {
                    this.systemStatus = response.data.status;
                    this.alarmLevel = response.data.alarm_level;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    },
    mounted() {
        console.log('Vue app mounted');
        this.fetchSystemStatus();
        this.fetchSensors();
        setInterval(() => {
            this.fetchSystemStatus();
            this.fetchSensors();
        }, 1000); // Aktualisiert alle 5 Sekunden
    }
});