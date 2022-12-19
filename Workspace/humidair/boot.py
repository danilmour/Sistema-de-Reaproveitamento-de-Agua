# boot.py -- run on boot-up
# Complete project details at https://RandomNerdTutorials.com

try:
  import usocket as socket
except:
  import socket

from machine import Pin, ADC, RTC
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

import utime as time
#from time import sleep, time
from bme280 import BME280

from hcsr04 import HCSR04
import bme280

led_amarelo = Pin(21, Pin.OUT)  # Led nível superior ao minimo
led_azul = Pin(4, Pin.OUT)  # Led menor que nível minimo

# Leitura dos estados dos contactos auxiliares de disjuntores
Cnt_Dis_C1 = Pin(34, Pin.IN)  # Contacto auxiliar - Motor 1
Cnt_Dis_C2 = Pin(35, Pin.IN)  # Contacto auxiliar - Motor 2

# Leitura dos tempos de funcionamento dos motores
Motor_1 = Pin(14, Pin.OUT)  # Contacto auxiliar - Motor 1
Motor_2 = Pin(27, Pin.OUT)  # Contacto auxiliar - Motor 2

# Potenciometros que simulam os contadores da água
Cnt_Agua_sys = ADC(Pin(32))  # Contador água do sistema
Cnt_Agua_sys.atten(ADC.ATTN_11DB)  # Full range: 3.3v
# Cnt_Agua_rede = ADC(Pin(33))  # Contaágua da rede
# Cnt_Agua_rede.atten(ADC.ATTN_11DB)  # Full range: 3.3v

# Controlo do desumidificador - ON/OFF
Cnt_desHUM = Pin(15, Pin.OUT) 
Cnt_desHUM.value(0)

# Controlo da central - ON/OFF
Cnt_Central = Pin(12, Pin.OUT) 
Cnt_Central.value(0)

# Controlo da eletroválvula
# Se Estado_EletroValvula = 1 -> Sistema Humidair
# Se Estado_EletroValvula = 0 -> Água da rede

Estado_EletroValvula = 1  # Inicio sitema sanitário alimentado pela rede
Cnt_EletroValvula = Pin(33, Pin.OUT)
Cnt_EletroValvula.value(Estado_EletroValvula)

# Simulação Válvulas 3 vias
Cnt_V3V = Pin(2, Pin.OUT)
Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito

cnt = 0
toggle = 0
soma1 = 0
soma2 = 0
soma3 = 0
tempoTotal1 = 0
tempoTotal2 = 0

ssid = '6ea6en6'
password = 'a4ae33324a96'

#ssid = 'Galaxy A12EF90'
#password = 'byjn6377'

#ssid = 'minedu'
#password = '2015.escola'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
