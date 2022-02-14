#include <AccelStepper.h>

#define STEP_SCALE 16
#define MAX_SPEED 50000.0
#define Y_ACCELERATION 31250.0
#define X_ACCELERATION 31250.0

//Servo mySrv[3];
int incomingByte = 0;   // for incoming serial data
int lastCommand = 0;
int paramCnt = 0;
unsigned char maxAngles[3][2] = {{30, 150}, {30, 150}, {30, 150}};

#define motorInterfaceType 1
AccelStepper stepperX = AccelStepper(motorInterfaceType, D5, D6); // x stepper on pins D5 and D6
AccelStepper stepperY = AccelStepper(motorInterfaceType, D0, D1); // y stepper on pins D0 and D1

#define LED_BUILTIN D4
void flashLed (int nr) { // just for debug 
  for (int i = 0; i < nr; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(20);
    digitalWrite(LED_BUILTIN, LOW);
    delay(20);
  }

}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(19200);    
  delay(100);

  Serial.write('A');

  stepperX.setAcceleration(X_ACCELERATION * STEP_SCALE);
  stepperX.setMaxSpeed(MAX_SPEED);
  stepperX.setCurrentPosition(150 * STEP_SCALE);
  stepperY.setAcceleration(Y_ACCELERATION  * STEP_SCALE);
  stepperY.setMaxSpeed(MAX_SPEED);
  stepperY.setCurrentPosition(150 * STEP_SCALE);
}

void loop() {
  static long cnt = 0;
  static uint8_t lastByte = 0;
  static uint16_t lastX = 1000, lastY = 1000, lastZ = 1000, currX = 1000, currY = 1000, currZ = 1000, currTime = 0;

  stepperX.run();
  stepperY.run();

  if (Serial.available() > 0) {
    incomingByte = Serial.read();

    if (incomingByte > 180) { // Command
      switch (incomingByte) {
        case 255: //new stepper data
          paramCnt = 0;
          break;

      }
      lastCommand = incomingByte;

        
    } else {
      paramCnt++;
      switch (lastCommand) {
        case 255: //new stepper data

          if (paramCnt == 2) { //X
            lastX = currX;
            currX = (uint16_t)lastByte * 127 + incomingByte;
          }

          if (paramCnt == 4) { //Y
            lastY = currY;
            currY = (uint16_t)lastByte * 127 + incomingByte;
          }

          if (paramCnt == 6) { //Z

          }
          if (paramCnt == 8) { //Time
            currTime = (uint16_t)lastByte * 127 + incomingByte;
            if (currTime > 0) {
              ////stepperX.setMaxSpeed(max(1.0, min(MAX_SPEED,   abs(((float)currX - (float)stepperX.currentPosition())) / (float)currTime * 1000.0) ));
              ////stepperY.setMaxSpeed(max(1.0, min(MAX_SPEED,   abs(((float)currY - (float)stepperY.currentPosition())) / (float)currTime * 1000.0) ));
              // these lines seem to cause a crash but should interpolate between step commands to make it smoother :(


              float x = abs(((float)currY - (float)lastY)) / (float)currTime * 1000.0;


            }

            stepperX.moveTo(currX);
            stepperY.moveTo(currY);
          }

          break;
      }
    }

    lastByte = incomingByte;
  }
}
