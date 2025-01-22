import serial
import time



#################### SET UP ####################

# Serial setup
port = "/dev/ttyACM2"
baudrate = 115200
ser = serial.Serial(port, baudrate)

# Clear the input buffer (received data)
ser.reset_input_buffer()

# Clear the output buffer (data waiting to be sent)
ser.reset_output_buffer()

cmd_ID = 0x01 #Move Motor Command
CW = 0x02 # Clock Wise
CCW = 0x03 #Counter Clock Wise

###############################################





###### Send Serial message from arduino ####

def send_position(Pi_cmd,Pi_payload): #Serial Message Function
   
   highbyte = Pi_payload >> 8 & 0xFF # High byte
   lowbyte = Pi_payload & 0xFF #Low Byte
   Pi_payload = [highbyte,lowbyte]
   Pi_direction = CW
   Pi_length = 1 + 1 + len(Pi_payload) + 1 + 1 # command_id + Direction + payload + checksum
   Pi_checksum = (Pi_length + Pi_cmd + sum(Pi_payload) + Pi_direction) & 0xFF
   
   message = bytes([Pi_length, Pi_cmd,Pi_direction]) + bytes(Pi_payload) + bytes([Pi_checksum])
   ser.write(message)
   time.sleep(0.01) 

############################################



###### Read Serial message from arduino ####

def read_from_arduino():
    if ser.read(1) == b'\xAA':  # Look for start byte
        Arduino_length = ser.read(1)[0]  # Read length byte
        Arduino_command_id = ser.read(1)[0]  # Command ID
        Arduino_payload = ser.read(Arduino_length - 2)  # Payload
        Arduino_checksum = ser.read(1)[0]  # Checksum
    
        # Verify checksum
        Arduino_calculated_checksum = Arduino_command_id + sum(Arduino_payload)
        if (Arduino_calculated_checksum & 0xFF) == Arduino_checksum:
            return Arduino_command_id, Arduino_payload   


############################################





###### Get user input and convert it to float ####

user_in = input("Enter target position: ")  # Prompt user for input
try:
    user_in = int(user_in)  # Convert the input to a float
except ValueError:
    print("Invalid input, please enter a numerical value.")
    exit(1)

# send position to arduino
send_position(cmd_ID,user_in)

##################################################





########## Convert from Serial to Number ##########

cmd,payload = read_from_arduino()
if cmd == 0x01:  # Command ID for temperature reading
        # Convert payload back to temperature (2 bytes -> float)
        pos = (payload[0] << 8) | payload[1]
        motor_pos = pos / 10.0  # Convert back to float
        print(f"Motor Position: {motor_pos}°")


##################################################