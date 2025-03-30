# Written by chat gpt, use i2c to communicate
#include <Wire.h>
#include <Servo.h>

byte servoPin_forward_port = 9;
byte servoPin_forward_starboard = 3;
byte servoPin_aft_port = 6;
byte servoPin_aft_starboard = 5;

Servo servo_forward_port;
Servo servo_forward_starboard;
Servo servo_aft_port;
Servo servo_aft_starboard;

int pwm_values[4] = {1500, 1500, 1500, 1500};

void setup(){
    Serial.begin(9600);
    Wire.begin(8); // I2C Slave address 8
    Wire.onReceive(receiveData);

    servo_forward_port.attach(servoPin_forward_port);
    servo_forward_starboard.attach(servoPin_forward_starboard);
    servo_aft_port.attach(servoPin_aft_port);
    servo_aft_starboard.attach(servoPin_aft_starboard);

    servo_forward_port.write(1500);
    servo_forward_starboard.write(1500);
    servo_aft_port.write(1500);
    servo_aft_starboard.write(1500);
}

void receiveData(int byteCount) {
    if (byteCount == 8) { // 4 PWM values, 2 bytes each
        for (int i = 0; i < 4; i++) {
            int highByte = Wire.read();
            int lowByte = Wire.read();
            pwm_values[i] = (highByte << 8) | lowByte;
        }
        sendMotorCommands();
    }
}

void sendMotorCommands(){
    servo_forward_port.write(pwm_values[0]);
    servo_forward_starboard.write(pwm_values[1]);
    servo_aft_port.write(pwm_values[2]);
    servo_aft_starboard.write(pwm_values[3]);
}

void loop(){
    delay(10);
}
