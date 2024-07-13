new Vue({
    el: '#app',
    data: {
        systemStatus: '',
        sensors: [],
        newSensorMac: ''
    },
    methods: {
        armSystem() {
            axios.post('http://localhost:8081/alarmsystem/arm')
                .then(response => {
                    this.systemStatus = response.data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        disarmSystem() {
            axios.post('http://localhost:8081/alarmsystem/disarm')
                .then(response => {
                    this.systemStatus = response.data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        triggerAlarm() {
            axios.post('http://localhost:8081/alarmsystem/alarm')
                .then(response => {
                    this.systemStatus = response.data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        fetchSensors() {
            axios.get('http://localhost:8081/sensors')
                .then(response => {
                    this.sensors = Object.keys(response.data).map(key => ({
                        mac_address: key,
                        last_updated: response.data[key].last_updated,
                        ip_address: response.data[key].ip_address
                    }));
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        addSensor() {
            axios.post('http://localhost:8081/sensors', { mac_address: this.newSensorMac })
                .then(() => {
                    this.fetchSensors();
                    this.newSensorMac = '';
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        deleteSensor(macAddress) {
            axios.delete(`http://localhost:8081/sensors/${macAddress}`)
                .then(() => {
                    this.fetchSensors();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        fetchSystemStatus() {
            axios.get('http://localhost:8081/alarmsystem')
                .then(response => {
                    this.systemStatus = response.data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    },
    mounted() {
        this.fetchSystemStatus();
        this.fetchSensors();
        setInterval(() => {
            this.fetchSystemStatus();
            this.fetchSensors();
        }, 5000); // Aktualisiert alle 5 Sekunden
    }
});