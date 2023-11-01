##### operation_gamepad.py ######

import time
import machine
import mqtt
import network, ubinascii
from secrets import Tufts_Wireless as wifi
import gamepad_test


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


def whenCalled(topic, msg):
    print((topic.decode(), msg.decode()))


def main():
    try:
        fred = mqtt.MQTTClient('gamepad_pico', 'broker.hivemq.com', keepalive=1000)
        print('Connected')
        fred.connect()
        fred.set_callback(whenCalled)
    except OSError as e:
        print('Failed')
        return

    fred.subscribe('chrisrogers/')
    try:
        last_x, last_y, last_btn = 0, 0, [False] * len(gamepad_test.BTN_CONST)
        while True:
            x = 1023 - gamepad_test.read_joystick(14)
            y = 1023 - gamepad_test.read_joystick(15)
            buttons = [not gamepad_test.digital_read() & btn for btn in gamepad_test.BTN_CONST]
            new_joystick_val = (abs(x - last_x) > 2) or (abs(y - last_y) > 2)

            new_button_val = False
            for btn, last, name in zip(buttons, last_btn, gamepad_test.BTN_Value):
                if (btn != last):  # if it has changed
                    print(name)
                    new_button_val = True
            if new_joystick_val or new_button_val:
                # TODO: add button values to the msg (check tha it works)
                msg = '%d %d %d %d %d %d %d %d' % (x, y, buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5])
                print(msg)
                fred.publish('chrisrogers/', msg)

            # update last buttons and joystick values
            last_x, last_y = x, y
            last_btn = buttons

            fred.check_msg()  # check subscriptions - you might want to do this more often
    #     except Exception as e:
    #         print(e)
    finally:
        fred.disconnect()
        print('done')


connect_wifi(wifi)
led = machine.Pin('LED', machine.Pin.OUT)
if __name__ == "__main__":
    main()
