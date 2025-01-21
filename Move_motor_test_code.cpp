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
   
  if (dir==1){
    
    while(degrees >= set){
      digitalWrite(MotorA, HIGH);
      digitalWrite(MotorB, LOW);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor
      delay(100);
      done = 1;
    }
   }

  else if(dir==2){
    
   
    while(degrees <= set){
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, HIGH);
      analogWrite(PWMpin, PWMVal); // Sets PWM/Speed of Motor
      delay(100); 
      done = 1;   
    } 
  }
  else
  { 
      analogWrite(PWMpin, 0);
      digitalWrite(MotorA, LOW);
      digitalWrite(MotorB, LOW);
  }

  

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

  DriveMotor(2, 100, 100);


}


