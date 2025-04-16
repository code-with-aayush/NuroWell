import serial
import time

# Configure the serial port
try:
    ser = serial.Serial('COM8', 9600, timeout=5)
    time.sleep(2)  # Wait for the serial connection to initialize
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    exit()

def collect_sensor_data():
    values = []
    start_time = time.time()
    
    while len(values) < 4 and (time.time() - start_time) < 30:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    value = float(line)
                    values.append(value)
                except ValueError:
                    pass
        time.sleep(0.1)
    
    return values if len(values) == 4 else None

def write_to_file(data):
    try:
        with open('sensor_data.txt', 'w') as f:
            f.write('\n'.join(str(value) for value in data))
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == '__main__':
    data = collect_sensor_data()
    
    if data and len(data) == 4:
        write_to_file(data)
    
    ser.close()