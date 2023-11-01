##### operation_bot.py ######

# MACHINE LIBRARIES ————————————
from machine import Pin, PWM, I2C
import time, struct
import uasyncio as asyncio

# DEVICE LIBRARIES —————————————
# import joystick

# NETWORK LIBRARIES ————————————
import urequests as requests
import mqtt
import network, ubinascii
from secrets import Tufts_Wireless as wifi

left_wheel_servo = PWM(Pin(12))
right_wheel_servo = PWM(Pin(13))
gantry_servo = PWM(Pin(14))
dropper_servo = PWM(Pin(15))
left_wheel_servo.freq(50)
right_wheel_servo.freq(50)
gantry_servo.freq(50)
dropper_servo.freq(50)

duty = 1200


# global x
# global y
# x = 0
# y = 0
def connect_wifi(wifi):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    print("MAC " + mac)

    station.connect(wifi['ssid'], wifi['pass'])
    while not station.isconnected():
        time.sleep(1)
    print('Connection successful')
    print(station.ifconfig())


def set_all_servos(x):
    for pin in range(12, 15):
        PWM(Pin(pin)).duty_u16(x)
        
def sControl(cent):
    return int((float(cent) / 100) * 1800 + 4800)


def whenCalled(topic, msg):
    global x
    global y
    print("recieved a message: %s on topic: %s" %(msg.decode(), topic.decode()))
    #print((topic.decode(), msg.decode()))
    info = msg.decode()
    info = info.split(" ")
    btns = info[2:]
    #btns = map(lambda x: 200 * x / 1023 - 100, info[2:])
 
    if btns[4] == "0":
        x = 200 * int(info[0]) / 1023 - 100
        y = 200 * int(info[1]) / 1023 - 100
        left_wheel_servo.duty_u16(sControl(-(y - x)))
        right_wheel_servo.duty_u16(sControl(y + x))
        if btns[0] == "1":
            dropper_servo.duty_u16(sControl(-100))
            print("picking up")
        if btns[1] == "1":
            gantry_servo.duty_u16(sControl(100))
            print("to the left")
        if btns[2] == "1":
            gantry_servo.duty_u16(sControl(-100))
            print("to the right")
        
        if btns[1] == "1" or btns[2] == "1":
            time.sleep(.03)
            gantry_servo.duty_u16(sControl(0))

        if btns[3] == "1":
            dropper_servo.duty_u16(sControl(200))
            print("dropping down")

    else:
        if btns[0] == "1":
            x=0
            y=20
        if btns[1] == "1":
            x=-20
            y=0
        if btns[2] == "1":
            x=20
            y=0
        if btns[3] == "1":
            x=0
            y=-20            
        left_wheel_servo.duty_u16(sControl(-(y - x)))
        right_wheel_servo.duty_u16(sControl(y + x))
        time.sleep(.2)
        left_wheel_servo.duty_u16(sControl(0))
        right_wheel_servo.duty_u16(sControl(0))


def main():
    try:
        fred = mqtt.MQTTClient('operations_arm_pico', 'broker.hivemq.com', keepalive=1000)
        print('Connected')
        fred.connect()
        print("rest")
        fred.set_callback(whenCalled)
    except OSError as e:
        print('Failed')
        return
    fred.subscribe("chrisrogers/")
    try:
        while True:
            fred.check_msg()
    except Exception as e:
        print(e)
    finally:
        fred.disconnect()


connect_wifi(wifi)
#set_all_servos(0)
main()
