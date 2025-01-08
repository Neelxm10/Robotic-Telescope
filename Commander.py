import serial
import time
from collections import deque

# Serial setup
port = "/dev/ttyACM7"
baudrate = 115200
ser = serial.Serial(port, baudrate)
ser.reset_input_buffer()

# Buffer for motor positions
position_buffer = deque(maxlen=600)  # Store up to 600 positions


# Initialize variables
tolerance = 10
current_position = 0
err = 0

def send_control_signal(msg):
    msg = msg + '/n'
    x = msg.encode('ascii')
    ser.write(x)


def read_from_arduino():
    if ser.in_waiting > 0:  # Check if data is available
        line = ser.readline().decode('utf-8').strip()  # Read a line of data
        print(f"Raw received data: {line}")  # Debugging output
        if line.startswith("POS:"):
            position = float(line.split(":")[1])  # Directly parse the position
            position_buffer.append(position)  # Add to buffer
            print(f"Position stored: {position}")  # Debugging output


# Get user input and convert it to float
user_in = input("Enter target position: ")  # Prompt user for input
try:
    user_in = float(user_in)  # Convert the input to a float
except ValueError:
    print("Invalid input, please enter a numerical value.")
    exit(1)

send_control_signal(str(user_in))

while True:
    # Continuously populate the buffer with data from Arduino
  

    read_from_arduino()

    # Process the most recent motor position if available
    if position_buffer:
        print(f"Buffer contains: {list(position_buffer)}")  # Check buffer contents
        current_position = position_buffer.popleft() 
        print(f"Processing position: {current_position}")

        if user_in > 0:   
            err = user_in - current_position
        else:
            err = user_in + current_position
        print(f"Error: {err}")
        
        # PD control calculations     
        # Compute control output
        # Send control signal to Arduino
        if abs(err) <= tolerance:
            print("Target position reached!")
            break  # Exit the control loop
    
    # Add a short delay to avoid excessive CPU usage
    time.sleep(0.01)  # 10ms delay

        
