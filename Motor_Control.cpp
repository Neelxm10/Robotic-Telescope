#include <Arduino.h>
#include <Wire.h>
#define FIT0186CPR 700 //Provided in Datasheet

//-------------------------

//Input and output Pins

//User Input
int input1 = 0;  // First numerical input
int input2 = 0;  // Second numerical input

//Motor Encoder
const int encoderpin1 = 2; //This is the Interrupt Pin
const int encoderpin2 = 4; //This Pin is a normal Pin read upon Interrupt
int encoderpin2Val = 0; //Value of the encoder pin (0 or 1), this pin is read in the interrupt
float degrees;

//Motor Driver
const int PWMpin = 3; 
int PWMVal;//0-255 PWM value for speed
const int MotorA = 5;
const int MotorB = 6;

//Measured Value
volatile unsigned long accmotorpos = 0; //Position from encoder 

//-------------------------

void EncoderCheck(){

  encoderpin2Val = digitalRead(encoderpin2);

  if(encoderpin2Val == 0) //CW
  {
    accmotorpos++;  
  }
  else // CCW
  {
    accmotorpos--;
  }

  degrees = (accmotorpos % FIT0186CPR) * (360.0 / FIT0186CPR); //Calculate Degrees of Rotation 
}


void DriveMotor(int dir, int IN1,int IN2, float set) {
  
  if (dir==1){
     
    //while(degrees <= set){
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      PWMVal = map(degrees,0,set,255,0);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor
      Serial.print("Encoder Count: ");
      Serial.println(degrees);
    //}
   }

  else if(dir==2){
     
    // while(degrees >= set){
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      PWMVal = map(degrees,0,set,0,255);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor      
      Serial.print("Encoder Count: ");
      Serial.println(degrees);
    //}
  }
  else
  { 
      analogWrite(PWMpin, 0);
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
  }

}

void setup() {

  Serial.begin(9600);
  
 
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

  if (Serial.available() > 0) {
    // Read the first integer input
    input1 = Serial.parseInt();
  

    DriveMotor(1, MotorA, MotorB, input1);
    delay(100);
    
  }

}

