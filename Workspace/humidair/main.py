from time import sleep
from machine import Pin
import bme280
from hcsr04 import HCSR04

# Led nível superior ao minimo
led_amarelo = Pin(21, Pin.OUT)
# Led menor que nível minimo
led_azul = Pin(4, Pin.OUT)


"""
Cálculo temperatura e humidade
Bloco desumidificação
"""


def temperatura():
  try:
    # Connect to BME-280 via software SPI with custom pinning (not supported by all microcontrollers):
    bme = bme280.BME280(spiBus={ "sck": 18, "mosi": 23, "miso": 19 }, spiCS=5)

    # Alternatively:
    # Connect to BME-280 via pre-initialized Micropython bus object:
    #bme = bme280.BME280(spiBus=machine.SPI(0, ...), spiCS=machine.Pin(5, ...))

    # Synchronously trigger a MODE_FORCED conversion and return the result.
    temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                     tempOversampling=bme280.OVSMPL_4,
                                                     humidityOversampling=bme280.OVSMPL_4,
                                                     pressureOversampling=bme280.OVSMPL_4)

    # See help(bme280.BME280) for documentation and more methods.

    # Print the result.
    print(f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

  except bme280.BME280Error as e:
    print(f"BME280 error: {e}")

"""
#### Cálculo do nível da água no depósito ####
##############################################
########################################
#
# Bloco armazenamento
#
#########################################
"""

def nivel():
  # Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
  # ESP32
  sensor = HCSR04(trigger_pin=25, echo_pin=26, echo_timeout_us=10000)

  distance = sensor.distance_cm()
  print('Distance:', distance, 'cm')
  # depósito cheio
  # distancia entre 5 e 8cm
  if distance > 5 and distance < 20:
    led_amarelo.value(1)
    led_azul.value(0)

  ##
  # Limite minimo - depósito vazio
  # distancia entre 18 e 20cm
  if distance > 20:
    led_amarelo.value(0)
    led_azul.value(1)

##
  # Só para uma questão de simulação
  # distancia maior que 20 apaga os leds
  if distance < 5:
    led_amarelo.value(0)
    led_azul.value(0)

  sleep(1)


while True:
  nivel()
  temperatura()
