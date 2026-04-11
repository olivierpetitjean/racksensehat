import time
import pigpio
from utils import debug_print, Verbose

PULSE = 2  # Fan pulses per revolution


class GpioController:
    def __init__(self, settings):
        self._fan1_pin = int(settings['fan1Pin'])
        self._fan2_pin = int(settings['fan2Pin'])
        self._fan1_sensor = int(settings['fan1Sensor'])
        self._fan2_sensor = int(settings['fan2Sensor'])
        self._red_led = settings['redLed']
        self._green_led = settings['greenLed']
        self._sys_fan = settings['systemFan']
        self._sys_buzzer = settings['sysBuzzer']
        self._output_enabled = settings['outputEnabled']
        self._btn1 = int(settings['button1Pin'])
        self._btn2 = int(settings['button2Pin'])
        self._frequency = int(settings['fanFrequency'])
        self._resolution = int(settings['fanPWMResolution'])
        self._fan1_name = settings.get('fan1Name', 'Fan 1')
        self._fan2_name = settings.get('fan2Name', 'Fan 2')

        self._gpio = None
        self._fan1_pwr = 0
        self._fan2_pwr = 0
        self._fan1_callback = None
        self._fan2_callback = None
        self._fan1_timer = None
        self._fan2_timer = None

        self._button_callback = None
        self._button1_pressed = False
        self._button2_pressed = False
        self._button1_timer = time.time()
        self._button2_timer = time.time()
        self._button_both_pressed = False

    def init(self):
        self._gpio = pigpio.pi()
        if not self._gpio.connected:
            raise RuntimeError("Unable to connect to pigpiod")
        debug_print("Connected to pigpiod.", Verbose.INFO)

        # System fan
        self._gpio.set_mode(self._sys_fan, pigpio.OUTPUT)
        self._gpio.write(self._sys_fan, 0)

        # Buzzer
        self._gpio.set_mode(self._sys_buzzer, pigpio.OUTPUT)

        # LEDs
        self._gpio.set_mode(self._red_led, pigpio.OUTPUT)
        self._gpio.set_mode(self._green_led, pigpio.OUTPUT)
        self._gpio.write(self._red_led, 0)
        self._gpio.write(self._green_led, 0)

        # Fan outputs
        self._gpio.set_mode(self._fan1_pin, pigpio.OUTPUT)
        rc = self._gpio.hardware_PWM(self._fan1_pin, self._frequency, self._resolution)
        self._log_gpio_result(f"{self._fan1_name} hardware PWM init on GPIO {self._fan1_pin}", rc)
        rc = self._gpio.set_PWM_dutycycle(self._fan1_pin, 255)
        self._log_gpio_result(f"{self._fan1_name} initial duty on GPIO {self._fan1_pin}", rc)
        self._gpio.set_mode(self._fan2_pin, pigpio.OUTPUT)
        rc = self._gpio.hardware_PWM(self._fan2_pin, self._frequency, self._resolution)
        self._log_gpio_result(f"{self._fan2_name} hardware PWM init on GPIO {self._fan2_pin}", rc)
        rc = self._gpio.set_PWM_dutycycle(self._fan2_pin, 255)
        self._log_gpio_result(f"{self._fan2_name} initial duty on GPIO {self._fan2_pin}", rc)
        debug_print(
            f"{self._fan1_name}/{self._fan2_name} outputs initialized on GPIO {self._fan1_pin}/{self._fan2_pin} "
            f"(freq={self._frequency}, resolution={self._resolution})",
            Verbose.INFO,
        )

        # Output enable
        self._gpio.set_mode(self._output_enabled, pigpio.OUTPUT)
        self._gpio.write(self._output_enabled, 1)

        # Fan tachometer inputs
        self._gpio.set_mode(self._fan1_sensor, pigpio.INPUT)
        self._gpio.set_mode(self._fan2_sensor, pigpio.INPUT)
        self._gpio.set_PWM_frequency(self._fan1_sensor, 50)
        self._gpio.set_PWM_frequency(self._fan2_sensor, 50)
        self._gpio.set_pull_up_down(self._fan1_sensor, pigpio.PUD_UP)
        self._gpio.set_pull_up_down(self._fan2_sensor, pigpio.PUD_UP)
        self._fan1_timer = time.time()
        self._fan1_callback = self._gpio.callback(self._fan1_sensor, pigpio.RISING_EDGE)
        self._fan2_timer = time.time()
        self._fan2_callback = self._gpio.callback(self._fan2_sensor, pigpio.FALLING_EDGE)
        debug_print(
            f"{self._fan1_name}/{self._fan2_name} tachometer inputs initialized on GPIO {self._fan1_sensor}/{self._fan2_sensor}",
            Verbose.DEBUG,
        )

        # Buttons
        self._gpio.set_mode(self._btn1, pigpio.INPUT)
        self._gpio.set_mode(self._btn2, pigpio.INPUT)
        self._gpio.set_pull_up_down(self._btn1, pigpio.PUD_DOWN)
        self._gpio.set_pull_up_down(self._btn2, pigpio.PUD_DOWN)
        self._gpio.callback(self._btn1, pigpio.EITHER_EDGE, self._on_btn1)
        self._gpio.callback(self._btn2, pigpio.EITHER_EDGE, self._on_btn2)
        debug_print(f"Buttons initialized on GPIO {self._btn1}/{self._btn2}", Verbose.DEBUG)

        debug_print("GPIO initialized.", Verbose.INFO)

    def set_button_callback(self, callback):
        self._button_callback = callback

    # --- Fan RPM ---

    def _log_gpio_result(self, action, rc, pin=None):
        if rc < 0:
            debug_print(f"{action} failed with pigpio rc={rc}", Verbose.ERROR)
            return
        if pin is not None:
            try:
                readback = self._gpio.get_PWM_dutycycle(pin)
                debug_print(f"{action} succeeded (rc={rc}, readback={readback})", Verbose.DEBUG)
                return
            except Exception as ex:
                debug_print(f"{action} succeeded (rc={rc}), readback failed: {ex}", Verbose.DEBUG)
                return
        debug_print(f"{action} succeeded (rc={rc})", Verbose.DEBUG)

    def get_fan1_rpm(self):
        if self._fan1_callback is None:
            debug_print(f"{self._fan1_name} tachometer callback unavailable.", Verbose.WARNING)
            return 0
        elapsed = time.time() - self._fan1_timer
        self._fan1_timer = time.time()
        falls = self._fan1_callback.tally()
        self._fan1_callback.reset_tally()
        return ((falls / PULSE) / elapsed) * 60

    def get_fan2_rpm(self):
        if self._fan2_callback is None:
            debug_print(f"{self._fan2_name} tachometer callback unavailable.", Verbose.WARNING)
            return 0
        elapsed = time.time() - self._fan2_timer
        self._fan2_timer = time.time()
        falls = self._fan2_callback.tally()
        self._fan2_callback.reset_tally()
        return ((falls / PULSE) / elapsed) * 60

    # --- Fan power ---

    def set_fan1_power(self, power):
        if self._fan1_pwr != power:
            debug_print(f"Setting {self._fan1_name} power to {power}%", Verbose.INFO)
            dc = int((255 * power) / 100)
            rc = self._gpio.set_PWM_dutycycle(self._fan1_pin, dc)
            self._log_gpio_result(f"{self._fan1_name} duty update to {dc}/255 on GPIO {self._fan1_pin}", rc, self._fan1_pin)
            self._fan1_pwr = power
            return power
        return -1

    def set_fan2_power(self, power):
        if self._fan2_pwr != power:
            debug_print(f"Setting {self._fan2_name} power to {power}%", Verbose.INFO)
            dc = int((255 * power) / 100)
            rc = self._gpio.set_PWM_dutycycle(self._fan2_pin, dc)
            self._log_gpio_result(f"{self._fan2_name} duty update to {dc}/255 on GPIO {self._fan2_pin}", rc, self._fan2_pin)
            self._fan2_pwr = power
            return power
        return -1

    # --- Outputs ---

    def red_led(self, state):
        self._gpio.write(self._red_led, state)

    def green_led(self, state):
        self._gpio.write(self._green_led, state)

    def system_fan(self, state):
        self._gpio.write(self._sys_fan, state)

    def beep(self, duration):
        try:
            self._gpio.set_PWM_dutycycle(self._sys_buzzer, 128)
            time.sleep(duration)
            self._gpio.set_PWM_dutycycle(self._sys_buzzer, 0)
        except Exception as ex:
            debug_print(f"Unable to play short beep: {ex}", Verbose.WARNING)

    def beep2(self, duration):
        try:
            self._gpio.set_PWM_dutycycle(self._sys_buzzer, 200)
            time.sleep(duration)
            self._gpio.set_PWM_dutycycle(self._sys_buzzer, 0)
        except Exception as ex:
            debug_print(f"Unable to play alert beep: {ex}", Verbose.WARNING)

    # --- Button handlers ---

    def _on_btn1(self, pin, level, tick):
        dt = time.time() - self._button1_timer
        if dt < 0.01:
            return
        self._button1_timer = time.time()
        if level == 1:
            self._button1_pressed = True
            debug_print("Button 1 pressed", Verbose.DEBUG)
        elif level == 0:
            self._button1_pressed = False
            debug_print("Button 1 released", Verbose.DEBUG)
        else:
            return
        if self._button_callback and not self._button1_pressed:
            if not self._button2_pressed:
                if self._button_both_pressed:
                    self._button_both_pressed = False
                    self._button_callback(2, dt)
                else:
                    self._button_callback(0, dt)
            else:
                self._button_both_pressed = True

    def _on_btn2(self, pin, level, tick):
        dt = time.time() - self._button2_timer
        if dt < 0.01:
            return
        self._button2_timer = time.time()
        if level == 1:
            self._button2_pressed = True
            debug_print("Button 2 pressed", Verbose.DEBUG)
        elif level == 0:
            self._button2_pressed = False
            debug_print("Button 2 released", Verbose.DEBUG)
        else:
            return
        if self._button_callback and not self._button2_pressed:
            if not self._button1_pressed:
                if self._button_both_pressed:
                    self._button_both_pressed = False
                    self._button_callback(2, dt)
                else:
                    self._button_callback(1, dt)
            else:
                self._button_both_pressed = True

    # --- Cleanup ---

    def dispose(self):
        self.red_led(0)
        self.green_led(0)
        if self._fan1_callback:
            self._fan1_callback.cancel()
        if self._fan2_callback:
            self._fan2_callback.cancel()
        if self._gpio:
            self._gpio.stop()
        debug_print("GPIO disposed.", Verbose.INFO)
