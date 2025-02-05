import serial
import threading
import time
from collections import deque

class SerialMessenger:
    def __init__(self, port, baudrate, max_buffer_size=600):
        # Serial setup
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.ser.reset_input_buffer()

        # Message parameters
        self.cmd_ID = 0x01  # Move Motor Command
        self.encoder_buffer = deque(maxlen=max_buffer_size)  # Store encoder data

        # Threading and control variables
        self.running = True
        self.lock = threading.Lock()

        # Start the read thread
        self.read_thread = threading.Thread(target=self._read_encoder_data, daemon=True)
        self.read_thread.start()

    def send_position(self, command_id, position):
        """Sends a position command to the serial device."""

        # Prepare the payload
        highbyte = (position >> 8) & 0xFF
        lowbyte = position & 0xFF
        payload = [highbyte, lowbyte]

        # Calculate the message length and checksum
        length = 1 + len(payload) + 1 # cmd_id + payload + checksum
        checksum = (length + command_id + sum(payload)) & 0xFF

        # Construct the message
        message = bytes([length, command_id]) + bytes(payload) + bytes([checksum])

        # Send the message
        self.ser.write(message)
        time.sleep(0.01)

    def _read_encoder_data(self):
        """Continuously reads encoder data from the serial device."""
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    if self.ser.read(1) == b'\xAA':  # Look for start byte
                        length = self.ser.read(1)[0]
                        command_id = self.ser.read(1)[0]
                        payload = self.ser.read(length - 2)
                        checksum = self.ser.read(1)[0]

                        # Verify checksum
                        calculated_checksum = (command_id + sum(payload)) & 0xFF
                        if calculated_checksum == checksum and command_id == 0x04:  # Encoder data command ID
                            encoder_value = (payload[0] << 8) | payload[1]

                            # Store in buffer
                            with self.lock:
                                self.encoder_buffer.append(encoder_value)

                except Exception as e:
                    print(f"Error reading encoder data: {e}")

    def get_latest_encoder_position(self):
        """Returns the most recent encoder position."""
        with self.lock:
            if self.encoder_buffer:
                return self.encoder_buffer[-1]
            return None

    def stop(self):
        """Stops the read thread and closes the serial connection."""
        self.running = False
        self.read_thread.join()
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.close()


# Example usage
if __name__ == "__main__":
    # Adjust the port and baudrate as needed
    port = "/dev/ttyACM0"
    baudrate = 115200

    messenger = SerialMessenger(port, baudrate)

    try:
        # Command example: Move motor to a position
        user_input = input("Enter target position: ")
        try:
            target_position = int(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            exit(1)

        # Send position command
        messenger.send_position(messenger.cmd_ID, target_position)

        # Periodically check encoder data
        while True:
            latest_position = messenger.get_latest_encoder_position()
            if latest_position is not None:
                print(f"Latest encoder position: {latest_position}")
            time.sleep(0.5)
            

    except KeyboardInterrupt:
        print("Exiting program.")

       
    finally:
        messenger.stop()