#include <Arduino.h>
#include <Wire.h>

#define FIT0186CPR 700  // Encoder counts per revolution (CPR) from datasheet

// -------------------------
// Input and Output Pins
const int encoderpin1 = 2; // Interrupt pin
const int encoderpin2 = 4; // Read in interrupt handler

const int PWMpin = 3;
const int MotorA = 5;
const int MotorB = 6;

// -------------------------
// Variables
volatile long accmotorpos = 0;  // Absolute position counter
int inputPos = 0;
int pwmValue = 0;
int current_pos = 0;
int timestamp = 0;
bool done = false;

// -------------------------
// Encoder Interrupt Service Routine
void EncoderCheck() {
    int encoderpin2Val = digitalRead(encoderpin2);

    if (digitalRead(encoderpin1) == HIGH) {
        accmotorpos += (encoderpin2Val == 0) ? -1 : 1;  // CCW (-1), CW (+1)
    }

    current_pos = (accmotorpos % FIT0186CPR) * (360.0 / FIT0186CPR);  // Convert to degrees

    uint8_t Arduino_commandID = 0x04;  // Encoder data message
    uint8_t Arduino_payload[2];
    
    Arduino_payload[0] = (current_pos >> 8) & 0xFF;
    Arduino_payload[1] = current_pos & 0xFF;

    sendData(Arduino_commandID, Arduino_payload, sizeof(Arduino_payload));
}

// -------------------------
// Motor Control
void DriveMotor(int dir, int PWMVal) {
    if (dir == 1) {  // Counter-Clockwise
        digitalWrite(MotorA, HIGH);
        digitalWrite(MotorB, LOW);
        analogWrite(PWMpin, PWMVal);

        if (current_pos <= inputPos * 0.8) {
            done = true;
        }
    } 
    else if (dir == 2) {  // Clockwise
        digitalWrite(MotorA, LOW);
        digitalWrite(MotorB, HIGH);
        analogWrite(PWMpin, PWMVal);

        if (current_pos >= inputPos * 0.8) {
            done = true;
        }
    } 
    else {  // Stop motor
        digitalWrite(MotorA, LOW);
        digitalWrite(MotorB, LOW);
    }
}

// -------------------------
// Read Serial Data (from Raspberry Pi)
void ReadData() {
    if (Serial.available() > 4) {
        uint8_t Pi_length = Serial.read();
        uint8_t Pi_command_id = Serial.read();
        uint8_t Pi_payload_high = Serial.read();
        uint8_t Pi_payload_low = Serial.read();
        uint8_t Pi_received_checksum = Serial.read();

        uint8_t Pi_calculated_checksum = (Pi_length + Pi_command_id + Pi_payload_high + Pi_payload_low) & 0xFF;

        if (Pi_received_checksum == Pi_calculated_checksum) {
            if (Pi_command_id == 0x05) {  // Heartbeat acknowledgment
                timestamp = (Pi_payload_high << 8) | Pi_payload_low;

                uint8_t ACK_payload[2] = { 
                    (timestamp >> 8) & 0xFF, 
                    timestamp & 0xFF 
                };

                send_ACK(0x05, ACK_payload, sizeof(ACK_payload));  // Send heartbeat response
            } 
            else if (Pi_command_id == 0x01) {  // Motor position command
                inputPos = (Pi_payload_high << 8) | Pi_payload_low;
            }
        }

        Serial.flush();
    }
}

// -------------------------
// Send Encoder Data
void sendData(uint8_t commandID, uint8_t *payload, uint8_t payloadSize) {
    Serial.write(0xAA);                         // Start byte
    Serial.write(payloadSize + 2);              // Data length
    Serial.write(commandID);                    // Command ID
    Serial.write(payload, payloadSize);         // Payload data

    uint8_t checksum = commandID;
    for (int i = 0; i < payloadSize; i++) {
        checksum += payload[i];
    }

    Serial.write(checksum & 0xFF);              // Append checksum
}

// -------------------------
// Send Heartbeat Acknowledgment
void send_ACK(uint8_t commandID, uint8_t *payload, uint8_t payloadSize) {
    Serial.write(0xBB);                         // Start byte
    Serial.write(payloadSize + 2);              // Data length
    Serial.write(commandID);                    // Command ID
    Serial.write(payload, payloadSize);         // Payload data

    uint8_t checksum = commandID;
    for (int i = 0; i < payloadSize; i++) {
        checksum += payload[i];
    }

    Serial.write(checksum & 0xFF);              // Append checksum
}

// -------------------------
// Setup
void setup() {
    Serial.begin(115200);

    accmotorpos = 0;
    current_pos = 0;
    
    delay(1000);  // Prevent motor movement on startup

    pinMode(MotorA, OUTPUT);
    pinMode(MotorB, OUTPUT);
    pinMode(encoderpin1, INPUT);
    pinMode(encoderpin2, INPUT);

    attachInterrupt(digitalPinToInterrupt(encoderpin1), EncoderCheck, RISING);
}

// -------------------------
// Main Loop
void loop() {
    ReadData();

    if (inputPos > current_pos) {
        pwmValue = map(abs(current_pos - inputPos), 0, 360, 50, 255);
        DriveMotor(2, pwmValue);  // Clockwise
    } 
    else if (inputPos < current_pos) {
        pwmValue = map(abs(current_pos - inputPos), 0, 360, 50, 255);
        DriveMotor(1, pwmValue);  // Counter-Clockwise
    } 
    else {
        DriveMotor(0, 0);  // Stop motor
    }

    if (done) {
        DriveMotor(0, 0);
        done = false;
    }
}
