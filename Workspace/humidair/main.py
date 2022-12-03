from time import sleep
from bme280 import BME280


from machine import Pin, ADC
from hcsr04 import HCSR04
import bme280

led_amarelo = Pin(21, Pin.OUT)  # Led nível superior ao minimo
led_azul = Pin(4, Pin.OUT)  # Led menor que nível minimo

# Leitura dos estados dos contactos auxiliares de disjuntores
Cnt_Dis_C1 = Pin(13, Pin.IN)  # Contacto auxiliar - Motor 1
Cnt_Dis_C2 = Pin(12, Pin.IN)  # Contacto auxiliar - Motor 2

# Leitura dos tempos de funcionamento dos motores
Cnt_Aux_C1 = Pin(14, Pin.IN)  # Contacto auxiliar - Motor 1
Cnt_Aux_C2 = Pin(27, Pin.IN)  # Contacto auxiliar - Motor 2

# Potenciometros que simulam os contadores da água
Cnt_Agua_sys = ADC(Pin(32))  # Contador água do sistema
Cnt_Agua_sys.atten(ADC.ATTN_11DB)       #Full range: 3.3v
Cnt_Agua_rede = ADC(Pin(33))  # Contaágua da rede
Cnt_Agua_rede.atten(ADC.ATTN_11DB)       #Full range: 3.3v


"""
  Cálculo temperatura e humidade
  Bloco desumidificação
"""
# Connect to BME-280 via software SPI with custom pinning (not supported by all microcontrollers):
bme = bme280.BME280(spiBus={"sck": 18, "mosi": 23, "miso": 19}, spiCS=5)

def cntagua():
  print(Cnt_Agua_sys.read())
  print('')
  print(Cnt_Agua_rede.read())
  print('')

def temperatura():
  try:
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


def CntAux():
  if Cnt_Dis_C1.value() == 0:
    print('Possível avaria MOTOR1')
  else:
    print('Motor 1 OK')

  if Cnt_Dis_C2.value() == 0:
    print('Possível avaria MOTOR2')
  else:
    print('Motor 2 OK')

  print('')

  if Cnt_Aux_C1.value() == 0:
    print('Motor 1 Parado')
  else:
    print('Motor 1 em funcionamento')
  if Cnt_Aux_C2.value() == 0:
    print('Motor 2 Parado')
  else:
    print('Motor 2 em funcionamento')

  print('')


#### Cálculo do nível da água no depósito ####
##############################################
########################################
#
# Bloco armazenamento
#
#########################################


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
    print('tanque entre valor minimo e maximo')

  ##
  # Limite minimo - depósito vazio
  # distancia entre 18 e 20cm
  if distance > 20:
    led_amarelo.value(0)
    led_azul.value(1)
    print('tanque no valor minimo')

##
  # Só para uma questão de simulação
  # distancia maior que 20 apaga os leds
  if distance < 5:
    led_amarelo.value(1)
    led_azul.value(1)
    print('tanque maximo')
  sleep(1)


while True:
  temperatura()
  nivel()
  CntAux()
  cntagua()