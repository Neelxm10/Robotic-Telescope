#include <Arduino.h>
#include <Wire.h>
#define FIT0186CPR 700 //Provided in Datasheet

//-------------------------

//Input and output Pins

//Motor Encoder
const int encoderpin1 = 2; //This is the Interrupt Pin
const int encoderpin2 = 4; //This Pin is a normal Pin read upon Interrupt
int encoderpin2Val; //Value of the encoder pin (0 or 1), this pin is read in the interrupt
float degrees=0;

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


void DriveMotor(int dir,float set, int PWMVal) {
  
  if (dir==1){
    
    while(degrees >= set){
      digitalWrite(MotorA, HIGH);
      digitalWrite(MotorB, LOW);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor
      Serial.print("POS:");
      Serial.println(degrees);
      delay(100);
    }
   }

  else if(dir==2){
    
   
    while(degrees <= set){
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, HIGH);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor
      Serial.print("POS:");
      Serial.println(degrees);
      delay(100);    
    } 
  }
  else
  { 
      analogWrite(PWMpin, 0);
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, LOW);
  }

  Serial.flush(); 

}

void setup() {

  Serial.begin(115200);
  
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


  static unsigned long lastUpdate = 0;

 
  if (Serial.available() > 0) {
    
    // Read the first integer input
    int input1 = 0;  // First numerical input
    input1 = Serial.parseInt();
 
    if (input1 >= 0) {
      DriveMotor(2, input1, 70); // Clockwise
    } else {
      DriveMotor(1, -input1, 70); // Counter-Clockwise (make the input positive for control)   
    }



    DriveMotor(0,0,0);

  }

}

