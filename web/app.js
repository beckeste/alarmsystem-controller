new Vue({
    el: '#app',
    data: {
        systemStatus: '',
        sensors: [],
        newSensorMac: '',
        apiUrl: `http://${hostIpAddress}:${apiPort}`
    },
    methods: {
        armSystem() {
            console.log('Arm system called');
            axios.post(`${this.apiUrl}/alarmsystem/arm`)
                .then(response => {
                    this.systemStatus = response.data.status;
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
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        triggerAlarm() {
            console.log('Trigger alarm called');
            axios.post(`${this.apiUrl}/alarmsystem/alarm`)
                .then(response => {
                    this.systemStatus = response.data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },
        fetchSensors() {
            console.log('Fetch sensors called');
            axios.get(`${this.apiUrl}/sensors`)
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
            console.log('Add sensor called');
            axios.post(`${this.apiUrl}/sensors`, { mac_address: this.newSensorMac })
                .then(() => {
                    this.fetchSensors();
                    this.newSensorMac = '';
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
        fetchSystemStatus() {
            console.log('Fetch system status called');
            axios.get(`${this.apiUrl}/alarmsystem`)
                .then(response => {
                    this.systemStatus = response.data.status;
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
        }, 5000); // Aktualisiert alle 5 Sekunden
    }
});