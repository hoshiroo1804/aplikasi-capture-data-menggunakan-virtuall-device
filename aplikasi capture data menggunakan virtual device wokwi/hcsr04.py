import machine, time
from machine import Pin

class HCSR04:
    """
    Driver menggunakan sensor untrasonik HC-SR04.
    Rentang sensor antara 2cm dan 4m.
    Batas waktu yang diterima saat mendengarkan pin gema diubah menjadi OSError('Di luar jangkauan')
    """
    # echo_timeout_us berdasarkan pada batas jangkauan chip (400cm))
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        trigger_pin: Pin Output digunakan untuk mengirim pulsa
        echo_pin: Pin readonly untuk mengukur jarak. Pin harus dilindungi dengan resistor 1k
        echo_timeout_us: Batas waktu dalam mikrodetik untuk mendengarkan pin gema.
        Secara default didasarkan pada rentang batas sensor (4m)
        """

        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        """
        send pulse untuk memicu dan mendengarkan pin gema.
        Kami menggunakan metode `machine.time_pulse_us()` untuk mendapatkan mikrodetik hingga gema diterima.
        """
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        """
       untuk Dapatkan jarak dalam milimeter tanpa operasi floating point.
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582 
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        untuk dapatkan jarak dalam sentimeter dengan operasi floating point.
        Ini mengembalikan pelampung
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms