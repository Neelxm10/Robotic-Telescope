import time
import pi_IMUv3  # Import your IMU module

def main():
    # Initialize the IMU object (adjust based on your implementation)
    imu = pi_IMUv3.IMU()
    
    try:
        while True:
            # Retrieve sensor data; assuming it returns a tuple of (accelerometer, gyroscope)
            accelerometer_data, gyroscope_data, orientation_data = imu.get_sensor_data()
            
            # Display the accelerometer data
            print("Accelerometer Data:")
            print(f"  X: {accelerometer_data[0]}, Y: {accelerometer_data[1]}, Z: {accelerometer_data[2]}")
            
            # Display the gyroscope data
            print("Gyroscope Data:")
            print(f"  X: {gyroscope_data[0]}, Y: {gyroscope_data[1]}, Z: {gyroscope_data[2]}")
            
            #Display orientation data
            print("Orientation Data:")
            print(f"  x: {orientation_data[0]}, Y: {orientation_data[1]}, Z: {orientation_data[2]}")
            
            print("-" * 40)  # Separator for readability
            
            # Wait for a second before the next reading
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == '__main__':
    main()
