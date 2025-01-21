#include <Arduino.h>
#include <Wire.h>
#define FIT0186CPR 700 //Provided in Datasheet

//-------------------------

//Input and output Pins

//Motor Encoder
const int encoderpin1 = 2; //This is the Interrupt Pin
const int encoderpin2 = 4; //This Pin is a normal Pin read upon Interrupt
int encoderpin2Val; //Value of the encoder pin (0 or 1), this pin is read in the interrupt
float degrees= 0;
int inputPos = 0;
uint8_t direction;
bool done = 0;
float tolerance = 15;

//Motor Driver
const int PWMpin = 3; 
const int MotorA = 5;
const int MotorB = 6;

//Measured Value
volatile unsigned long accmotorpos = 0; //Position from encoder 

//-------------------------

void EncoderCheck(){

  encoderpin2Val = digitalRead(encoderpin2);

  if(digitalRead(encoderpin1) == HIGH){
    if(encoderpin2Val == 0) //CCW
    {
      accmotorpos--;   
    }
    else // CW
    {
      accmotorpos++;
    }

  }
  
  degrees = (accmotorpos % FIT0186CPR) * (360.0 / FIT0186CPR); //Calculate Degrees of Rotation 

}


void DriveMotor(int dir, float set, int PWMVal) {
    unsigned long startTime = millis(); // Record the start time
    unsigned long timeout = 5000;       // Set a timeout (e.g., 5 seconds)

    if (dir == 1) { // Counter-Clockwise (CCW)
        while (degrees < set) { // Adjust condition to rotate until target is reached
            // Check for timeout to prevent infinite loops
            if (millis() - startTime > timeout) {
                Serial.println("Timeout: CCW movement took too long.");
                break;
            }

            digitalWrite(MotorA, LOW);
            digitalWrite(MotorB, HIGH);
            analogWrite(PWMpin, PWMVal);
            delay(10); // Small delay to reduce CPU load
        }
    } else if (dir == 2) { // Clockwise (CW)
        while (degrees > set) { // Adjust condition to rotate until target is reached
            // Check for timeout to prevent infinite loops
            if (millis() - startTime > timeout) {
                Serial.println("Timeout: CW movement took too long.");
                break;
            }

            digitalWrite(MotorA, HIGH);
            digitalWrite(MotorB, LOW);
            analogWrite(PWMpin, PWMVal);
            delay(10); // Small delay to reduce CPU load
        }
    }

    // Stop the motor once the target is reached
    analogWrite(PWMpin, 0);
    digitalWrite(MotorA, LOW);
    digitalWrite(MotorB, LOW);
    done = 1; // Mark movement as done
}



void ReadData(){

  if (Serial.available() > 0) {

    uint8_t Pi_length = Serial.read();
    
    // Read Command ID
    uint8_t Pi_command_id = Serial.read();
    
    // Calculate payload size
    uint8_t Pi_payload_size = Pi_length - 3;  // Length minus Command ID and checksum and direction
    
    //Read Direction
    uint8_t Pi_Direction = Serial.read();

    // Read payload
    uint8_t Pi_payload_high = Serial.read();  // High byte of payload
    uint8_t Pi_payload_low = Serial.read();   // Low byte of payload
    
    // Read checksum
    uint8_t Pi_received_checksum = Serial.read();
    
    // Calculate checksum for validation
    uint8_t Pi_calculated_checksum = (Pi_length + Pi_command_id + Pi_Direction + Pi_payload_high + Pi_payload_low) & 0xFF;
    
    // Validate checksum
    if (Pi_received_checksum == Pi_calculated_checksum) {
      inputPos  = (Pi_payload_high << 8) | Pi_payload_low;
      direction = Pi_Direction; 
    }
  }

  Serial.flush(); 

}



void sendData(uint8_t Arduino_commandID, uint8_t *Arduino_payload, uint8_t Arduino_payloadSize) {
    
    Serial.write(0xAA);                // Start byte
    Serial.write(Arduino_payloadSize + 2);     // Data length (commandID + payload)
    Serial.write(Arduino_commandID);           // Command ID
    for (int i = 0; i < Arduino_payloadSize; i++) {
        Serial.write(Arduino_payload[i]);      // Payload data
    }
    uint8_t Arduino_checksum = Arduino_commandID;      // Basic checksum
    for (int i = 0; i < Arduino_payloadSize; i++) {
        Arduino_checksum += Arduino_payload[i];
    }
    Serial.write(Arduino_checksum & 0xFF);     // Append checksum
    Serial.flush(); 
}



void setup() {

  Serial.begin(115200);

  accmotorpos = 0;
  degrees = 0;
  
  delay(1000); // To stop motor from Moving upon startup
  // Set motor pins as outputs
  pinMode(MotorA, OUTPUT);
  pinMode(MotorB, OUTPUT);
  
  // Set encoder pins as inputs
  pinMode(encoderpin1,INPUT);
  pinMode(encoderpin2,INPUT);



  // Attach interrup to encoderpin1
  attachInterrupt(digitalPinToInterrupt(encoderpin1),EncoderCheck,RISING);

 
}

void loop() {
     
  ReadData();

  if (direction == 0x02) {
      DriveMotor(2, inputPos, 70); // Clockwise
  } else if (direction == 0x03){
      DriveMotor(1, -inputPos, 70); // Counter-Clockwise (absolute value)
  }
  else{
    DriveMotor(0,0,0);
  }

  uint8_t Arduino_commandID = 0x01;  // Command ID for temperature reading
  uint8_t Arduino_payload[2];        // Payload: 2 bytes for temperature (e.g., 23.5°C)
  float pos = degrees;  // Example temperature
  int pos_int = (int)(pos * 10);  // Convert to integer (e.g., 23.5 -> 235)
  Arduino_payload[0] = (pos_int >> 8) & 0xFF;     // High byte
  Arduino_payload[1] = pos_int & 0xFF; 

  DriveMotor(0,0,0);
  
  if(done == 1){
    
    sendData(Arduino_commandID, Arduino_payload, 2); 
    direction = 0;
    done = 0;
  }  
}