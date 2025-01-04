import serial

port = "/dev/ttyACM7"
baudrate = 9600

ser = serial.Serial(port,baudrate)

def command(msg):
    msg = msg + '/n'
    x = msg.encode('ascii')
    ser.write(x)

def listen():
    msg = ser.read_until()
    mystring = msg.decode('ascii')
    return mystring

while True:
    val = input()
    command(val)
    var = listen()
    print(var)

