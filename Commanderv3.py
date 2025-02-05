import serial
import threading
import time
from collections import deque

class SerialMessenger:
    def __init__(self, port, baudrate, max_buffer_size=600):
        self.ser = serial.Serial(port, baudrate, timeout=2)  # Increased timeout
        self.ser.reset_input_buffer()

        self.cmd_ID = 0x01  # Move Motor Command
        self.ACK_ID = 0x05  # Heartbeat Acknowledge
        self.encoder_buffer = deque(maxlen=max_buffer_size)
        self.ack_buffer = deque(maxlen=max_buffer_size)
        self.running = True
        self.lock = threading.Lock()

        self.read_thread = threading.Thread(target=self._read_serial_data, daemon=True)
        self.read_thread.start()

    def send_position(self, position):
        """Sends a position command to the motor."""
        command_id = self.cmd_ID
        highbyte = (position >> 8) & 0xFF
        lowbyte = position & 0xFF
        payload = [highbyte, lowbyte]

        length = 1 + len(payload) + 1  # cmd_id + payload + checksum
        checksum = (length + command_id + sum(payload)) & 0xFF
        message = bytes([length, command_id]) + bytes(payload) + bytes([checksum])

        with self.lock:
            self.ser.write(message)
        time.sleep(0.01)

    def send_heartbeat(self):
        """Sends a heartbeat message."""
        timestamp = 15  # Placeholder timestamp
        highbyte = (timestamp >> 8) & 0xFF
        lowbyte = timestamp & 0xFF
        payload = [highbyte, lowbyte]

        length = 1 + len(payload) + 1  # ACK_id + payload + checksum
        checksum = (length + self.ACK_ID + sum(payload)) & 0xFF
        message = bytes([length, self.ACK_ID]) + bytes(payload) + bytes([checksum])

        with self.lock:
            self.ser.write(message)

    def _read_serial_data(self):
        """Continuously reads serial data."""
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    start_byte = self.ser.read(1)
                    if start_byte == b'\xAA':  # Encoder data
                        length = self.ser.read(1)[0]
                        command_id = self.ser.read(1)[0]
                        payload = self.ser.read(length - 2)
                        checksum = self.ser.read(1)[0]

                        calculated_checksum = (command_id + sum(payload)) & 0xFF
                        if calculated_checksum == checksum and command_id == 0x04:
                            encoder_value = (payload[0] << 8) | payload[1]
                            with self.lock:
                                self.encoder_buffer.append(encoder_value)

                    elif start_byte == b'\xBB':  # Heartbeat acknowledgment
                        length = self.ser.read(1)[0]
                        ack_id = self.ser.read(1)[0]
                        payload = self.ser.read(length - 2)
                        checksum = self.ser.read(1)[0]

                        calculated_checksum = (ack_id + sum(payload)) & 0xFF
                        if calculated_checksum == checksum and ack_id == self.ACK_ID:
                            time_value = (payload[0] << 8) | payload[1]
                            with self.lock:
                                self.ack_buffer.append(time_value)

                except Exception as e:
                    print(f"Error reading serial data: {e}")

    def get_latest_encoder_position(self):
        """Returns the latest encoder position."""
        with self.lock:
            return self.encoder_buffer[-1] if self.encoder_buffer else None

    def get_latest_ack_timestamp(self):
        """Returns the latest heartbeat acknowledgment timestamp."""
        with self.lock:
            return self.ack_buffer[-1] if self.ack_buffer else None

    def stop(self):
        """Stops the read thread and closes the serial connection."""
        self.running = False
        self.read_thread.join()
        self.ser.close()


# -------------------- MAIN PROGRAM --------------------
if __name__ == "__main__":
    port = "/dev/ttyACM0"
    baudrate = 115200

    messenger = SerialMessenger(port, baudrate)

    try:
        while True:
            # Get the latest data
            latest_position = messenger.get_latest_encoder_position()
            latest_heartbeat = messenger.get_latest_ack_timestamp()

            if latest_position is not None:
                print(f"Latest Encoder Position: {latest_position}")

            if latest_heartbeat is not None:
                print(f"Latest Heartbeat ACK Timestamp: {latest_heartbeat}")

            # Allow user to input motor position
            user_input = input("Enter target position (or 'q' to quit): ")
            if user_input.lower() == 'q':
                break

            try:
                target_position = int(user_input)
                messenger.send_position(target_position)
            except ValueError:
                print("Invalid input. Please enter an integer.")

            # Send heartbeat every second
            messenger.send_heartbeat()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting program.")

    finally:
        messenger.stop()