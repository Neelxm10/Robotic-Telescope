#include <Arduino.h>
#include <Wire.h>


//-------------------------

//Input and output Pins

//Motor Encoder
const int encoderpin1 = 2; //This is the Interrupt Pin
const int encoderpin2 = 4; //This Pin is a normal Pin read upon Interrupt
int encoderpin2Val = 0; //Value of the encoder pin (0 or 1), this pin is read in the interrupt

//Motor Driver
const int PWMpin = 3; 
int PWMVal = 75; //0-255 PWM value for speed
const int MotorA = 5;
const int MotorB = 6;

//Measured Value
volatile float accmotorpos = 0; //Position from encoder 

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

}

void DriveMotor(int dir, int PWM,int IN1,int IN2, float set) {
  
  if (dir==1){
    
  
    while(accmotorpos < set){
      analogWrite(PWMpin, PWM); // Sets PWM/Speed of Motor
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      
        Serial.print("Encoder Count: ");
        Serial.println(accmotorpos);
      
   

    }
   }

  else if(dir==-1){

    
  
    while(accmotorpos > set){
      analogWrite(PWMpin, PWM); // Sets PWM/Speed of Motor
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      
        Serial.print("Encoder Count: ");
        Serial.println(accmotorpos);


    }
  }
  else
  { 
      analogWrite(PWMpin, PWM);
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

  delay(100);
  DriveMotor(1, PWMVal, MotorA, MotorB, 100);
  delay(100);
  DriveMotor(-1, PWMVal, MotorA, MotorB, 0);
  DriveMotor(0, 0, MotorA, MotorB, 0);

  while (true){}
}

