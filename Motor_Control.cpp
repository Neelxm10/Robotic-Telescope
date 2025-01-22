#include <Arduino.h>
#include <Wire.h>
#define FIT0186CPR 700 //Provided in Datasheet

//-------------------------

//Input and output Pins

//Motor Encoder
const int encoderpin1 = 2; //This is the Interrupt Pin
const int encoderpin2 = 4; //This Pin is a normal Pin read upon Interrupt
int encoderpin2Val; //Value of the encoder pin (0 or 1), this pin is read in the interrupt
int inputPos = 0;
float degrees = 0;
uint8_t direction;
bool done = 0;

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
  
  // degrees = (accmotorpos % FIT0186CPR) * (360.0 / FIT0186CPR); //Calculate Degrees of Rotation 

}


void DriveMotor(int dir, float set, int PWMVal) {
   
  if (dir==1){ //Counter Clockwise

    // while(degrees >= set){
      digitalWrite(MotorA, HIGH);
      digitalWrite(MotorB, LOW);
      analogWrite(PWMpin, PWMVal); 
      delay(1000);
      done = 1;
    // }
   }

  else if(dir==2){ //Clockwise
    
    // while(degrees <= set){
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, HIGH);
      analogWrite(PWMpin, PWMVal);
      delay(1000);
      done = 1;   
    // } 
  }
  else
  { 
      analogWrite(PWMpin, 0);
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, LOW);
  }

 
}


void ReadData() {
    if (Serial.available() > 0) {
        uint8_t Pi_length = Serial.read();
        
        // Read Command ID
        uint8_t Pi_command_id = Serial.read();
        
        // Calculate payload size
        uint8_t Pi_payload_size = Pi_length - 3;  // Length minus Command ID, Direction, and checksum
        
        // Read Direction
        uint8_t Pi_Direction = Serial.read();

        // Read payload (2 bytes: high and low)
        uint8_t Pi_payload_high = Serial.read();
        uint8_t Pi_payload_low = Serial.read();

        // Read checksum
        uint8_t Pi_received_checksum = Serial.read();

        // Calculate checksum for validation
        uint8_t Pi_calculated_checksum = (Pi_length + Pi_command_id + Pi_Direction + Pi_payload_high + Pi_payload_low) & 0xFF;

        // Validate checksum
        if (Pi_received_checksum == Pi_calculated_checksum) {
            // Combine high and low bytes into a single integer
            inputPos = (Pi_payload_high << 8) | Pi_payload_low;

            // Store direction
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
      DriveMotor(1, inputPos, 70); // Counter-Clockwise (absolute value)
  }
  else{
    DriveMotor(0,0,0);
  }

  uint8_t Arduino_commandID = 0x01;  // Command ID for temperature reading
  uint8_t Arduino_payload[2];        // Payload: 2 bytes for temperature (e.g., 23.5°C)
  float pos = accmotorpos;  // Example temperature
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