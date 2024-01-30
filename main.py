from servo_motor import ServoMotor

servoMotors = []

servoMotors.append(ServoMotor(Channel=0, ZeroOffset=0))
servoMotors.append(ServoMotor(Channel=1, ZeroOffset=0))

servoMotors[0].setAngle(60)
servoMotors[1].setAngle(100)
