function updateSensorData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            // Update temperature
            const tempElement = document.getElementById('temperature');
            tempElement.textContent = data.temperature !== undefined ? 
                `${data.temperature} °C` : '--.- °C';
            
            // Update humidity
            const humElement = document.getElementById('humidity');
            humElement.textContent = data.humidity !== undefined ? 
                `${data.humidity} %` : '--.- %';
            
            // Update error message
            const errorElement = document.getElementById('error');
            errorElement.textContent = data.error || '';
            errorElement.style.display = data.error ? 'block' : 'none';
            
            // Update timestamp
            document.getElementById('timestamp').textContent = data.timestamp;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Update every 2 seconds
setInterval(updateSensorData, 2000);

// Initial update
updateSensorData();