from flask import Flask, render_template, jsonify
from smbus2 import SMBus, i2c_msg
import time
import threading

app = Flask(__name__)

# Sensor Configuration (from your code)
SHT20_I2C_ADDR = 0x40
TRIG_TEMP_NOHOLD = 0xF3
TRIG_HUMI_NOHOLD = 0xF5
SOFT_RESET = 0xFE

# Global variables to store readings
current_temp = 0.0
current_hum = 0.0
sensor_error = None

def sht20_reset():
    try:
        with SMBus(1) as bus:
            bus.write_byte(SHT20_I2C_ADDR, SOFT_RESET)
        time.sleep(0.05)
        return True
    except Exception as e:
        return False

def read_sht20(command):
    try:
        with SMBus(1) as bus:
            # Send measurement command
            bus.write_byte(SHT20_I2C_ADDR, command)
            
            # Wait based on measurement type
            time.sleep(0.085 if command == TRIG_TEMP_NOHOLD else 0.030)
            
            # Read data
            read = i2c_msg.read(SHT20_I2C_ADDR, 3)
            bus.i2c_rdwr(read)
            data = list(read)
            
            if len(data) < 2:
                raise IOError("Incomplete data received")
                
            raw = (data[0] << 8) + data[1]
            raw &= 0xFFFC
            
            if command == TRIG_TEMP_NOHOLD:
                return round(-46.85 + 175.72 * raw / 65536.0, 2), None
            return round(-6.0 + 125.0 * raw / 65536.0, 2), None
    except Exception as e:
        return None, str(e)

def sensor_loop():
    global current_temp, current_hum, sensor_error
    
    # Initial reset
    if not sht20_reset():
        sensor_error = "Sensor initialization failed"
        return
    
    time.sleep(0.2)
    
    while True:
        try:
            # Read temperature
            temp, temp_err = read_sht20(TRIG_TEMP_NOHOLD)
            if temp_err:
                raise IOError(temp_err)
                
            # Read humidity
            hum, hum_err = read_sht20(TRIG_HUMI_NOHOLD)
            if hum_err:
                raise IOError(hum_err)
                
            # Update global variables
            current_temp = temp
            current_hum = hum
            sensor_error = None
            
        except Exception as e:
            sensor_error = f"Sensor error: {str(e)}"
            print(sensor_error)
            sht20_reset()
            
        time.sleep(2)  # Update interval

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/data')
def get_sensor_data():
    return jsonify({
        'temperature': current_temp,
        'humidity': current_hum,
        'error': sensor_error,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    # Start sensor thread
    sensor_thread = threading.Thread(target=sensor_loop)
    sensor_thread.daemon = True
    sensor_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
