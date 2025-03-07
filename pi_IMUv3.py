import time
import smbus
from imusensor.MPU9250 import MPU9250

class IMU:
    def __init__(self, bus_num=1, address=0x68):
        """
        Initialize the MPU9250 sensor via I2C.

        :param bus_num: I2C bus number (default is 1)
        :param address: I2C address for the MPU9250 (default is 0x68)
        """
        self.bus = smbus.SMBus(bus_num)
        self.address = address
        # Create the MPU9250 object and initialize it
        self.imu = MPU9250.MPU9250(self.bus, self.address)
        self.imu.begin()

        # Enable I2C passthrough for the magnetometer
        self.bus.write_byte_data(self.address, 0x37, 0x02)  # Set BYPASS_EN bit
        self.bus.write_byte_data(self.address, 0x24, 0x00)   # Disable I2C_MST_EN
        if hasattr(self.imu, 'initAK8963'):
            self.imu.initAK8963()

    def update(self):
        """
        Read sensor data and compute the current orientation.
        """
        self.imu.readSensor()
        self.imu.computeOrientation()

    def get_sensor_data(self):
        """
        Update the sensor and return the latest data.

        :return: A dictionary containing accelerometer, gyroscope,
                 and orientation (roll, pitch, yaw) data.
        """
        self.update()
        # Extract sensor values
        accel = self.imu.AccelVals  # [x, y, z]
        gyro = self.imu.GyroVals    # [x, y, z]
        orientation = (self.imu.roll, self.imu.pitch, self.imu.yaw)
        return (accel,gyro,orientation)

if __name__ == '__main__':
    imu_sensor = IMU()  # Create an instance of the IMU class

    try:
        while True:
            data = imu_sensor.get_sensor_data()
            # Display accelerometer data
            print("Accelerometer Data:")
            print("  X: {:.2f}, Y: {:.2f}, Z: {:.2f}".format(*data['accelerometer']))
            # Display gyroscope data
            print("Gyroscope Data:")
            print("  X: {:.2f}, Y: {:.2f}, Z: {:.2f}".format(*data['gyroscope']))
            # Display orientation (roll, pitch, yaw)
            print("Orientation:")
            print("  Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(*data['orientation']))
            print("-" * 40)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting gracefully.")