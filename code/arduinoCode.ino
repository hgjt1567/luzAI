#include <Stepper.h>

int numSteps = 2038;
Stepper stepperX(numSteps, 8, 10, 9, 11);
Stepper stepperZ(numSteps, 2, 4, 3, 5);
int incoming[3];


void setup()
{
  pinMode(7, OUTPUT);
  Serial.begin(9600);
  stepperX.setSpeed(15);
  stepperZ.setSpeed(15);
}

void loop()
{
  while(Serial.available() >= 3)
  {
    //incoming data
    for (int i = 0; i < 3; i++)
    {
      incoming[i] = Serial.read();
    }

    //light toggle
    if (incoming[2]==1)
    {
      digitalWrite(7,HIGH);
    }
    else
    {
      digitalWrite(7, LOW);
    }

    //motor control
    if (incoming[0]==0)
    {
      if (incoming[1]==0)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(-1);
          stepperZ.step(1);
        }
      }
      else if (incoming[1]==1)
      {
        for(int i=0; i<150; i++)
        {
          stepperZ.step(1);
        }
      }
      else if (incoming[1]==2)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(1);
          stepperZ.step(1);
        }
      }
    }
    else if (incoming[0]==1)
    {
      if (incoming[1]==0)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(-1);
        }
      }
      else if (incoming[1]==2)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(1);
        }
      }
    }
    else if (incoming[0]==2)
    {
      if (incoming[1]==0)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(-1);
          stepperZ.step(-1);
        }
      }
      else if (incoming[1]==1)
      {
        for(int i=0; i<150; i++)
        {
          stepperZ.step(-1);
        }
      }
      else if (incoming[1]==2)
      {
        for(int i=0; i<150; i++)
        {
          stepperX.step(1);
          stepperZ.step(-1);
        }
      }
    }
  }
}
