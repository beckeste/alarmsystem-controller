new Vue({
    el: '#app',
    data: {
        systemStatus: ''
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
        }
    },
    mounted() {
        axios.get('http://localhost:8081/alarmsystem')
            .then(response => {
                this.systemStatus = response.data.status;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
});