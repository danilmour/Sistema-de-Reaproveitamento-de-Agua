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
Cnt_Agua_sys.atten(ADC.ATTN_11DB)  # Full range: 3.3v
Cnt_Agua_rede = ADC(Pin(33))  # Contaágua da rede
Cnt_Agua_rede.atten(ADC.ATTN_11DB)  # Full range: 3.3v

# Controlo do desumidificador - ON/OFF
Cnt_desHUM = Pin(15, Pin.OUT)  # Led nível superior ao minimo
Cnt_desHUM.value(0)

# Simulação Válvulas 3 vias
Cnt_V3V = Pin(2, Pin.OUT)
Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito

#### Informação web-server ####
#########################################
#
# Realiza pedido de estado do botão
#
#########################################

def pedido(s):
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)
    deshum_on = request.find('/?led=on')
    deshum_off = request.find('/?led=off')
    return deshum_on, deshum_off, conn

#### Informação web-server ####
#########################################
#
# Refresca a página com novos dados
#
#########################################

def refresh(conn, n):
    response = web_page(n)  # Chama a função web_page
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

#### Informação desumidificador/temperatura ####
##############################################
#
# Bloco desumidificação
#
#########################################

# Connect to BME-280 via software SPI with custom pinning (not supported by all microcontrollers):
bme = bme280.BME280(spiBus={"sck": 18, "mosi": 23, "miso": 19}, spiCS=5)


def Read_BME(n):
  try:
    # Synchronously trigger a MODE_FORCED conversion and return the result.
    temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                     tempOversampling=bme280.OVSMPL_4,
                                                     humidityOversampling=bme280.OVSMPL_4,
                                                     pressureOversampling=bme280.OVSMPL_4)  
    
    # Print the result.
    print(f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

  except bme280.BME280Error as e:
    print(f"BME280 error: {e}")

  # Se o desumidificador não tiver sido desligado manualmente, é atuado quando a humidade for superior a 60%
  if humidity * 100 > 60 and n == 1:  # MUDAR ISTO
    Cnt_desHUM.value(1)
  else:
    Cnt_desHUM.value(0)
  
  return temperature, humidity*100

#### Cálculo do nível da água no depósito ####
##############################################
#
# Bloco armazenamento
#
#########################################

def nivel():
  # Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
  # ESP32
  sensor = HCSR04(trigger_pin=25, echo_pin=26, echo_timeout_us=10000)

  distancia = sensor.distance_cm()
  print('Distancia:', distancia, 'cm')
  # depósito cheio
  # distancia entre 5 e 8cm
  if distancia > 5 and distancia < 20:
    nivel_medio = 1
    nivel_minimo = 0
    nivel_maximo = 0
    led_amarelo.value(1)
    led_azul.value(0)
    Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito
    print('tanque entre valor minimo e maximo')

  ##
  # Limite minimo - depósito vazio
  # distancia entre 18 e 20cm
  if distancia > 20:
    nivel_medio = 0
    nivel_minimo = 1
    nivel_maximo = 0
    led_amarelo.value(0)
    led_azul.value(1)
    Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito
    print('tanque no valor minimo')

##
  # Só para uma questão de simulação - TANQUE COMPLETAMENTE CHEI0
  # distancia maior que 20 apaga os leds
  if distancia < 5:
    nivel_medio = 0
    nivel_minimo = 0
    nivel_maximo = 1
    led_amarelo.value(1)
    led_azul.value(1)
    Cnt_V3V.value(1)  # Válvula 3 vias aberta - água fora
    print('tanque maximo')
  sleep(1)
  
  return nivel_maximo, nivel_medio, nivel_minimo


#########################################
#
# Criação do webserver
#
#########################################


def web_page(n):
      if n == 1:
        gpio_state = "ON"
      else:
        gpio_state = "OFF"
      
      temperatura, humidade = Read_BME(n)
      nivel_maximo, nivel_medio, nivel_minimo = nivel()
      
      if nivel_maximo == 1:
          estado_deposito = "CHEIO"
      elif nivel_medio == 1:
          estado_deposito = "Medio"
      elif nivel_minimo == 1:
          estado_deposito = "vazio"         
      
      html = """<html><head> <title>HumidAir</title> <meta http-equiv="refresh" content="5" name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
      h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: green; border: none;
      border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
      .button2{background-color: red;}</style></head><body> <h1>ESP Web Server</h1>
      <p>Desumidificador: <strong>""" + gpio_state + """</strong>
      <p>Temperatura: <strong>""" + str(temperatura) + """</strong>
      <p>Humidade: <strong>""" + str(humidade) + """</strong>
      <p>Desligar Desumidificador - SOS
      </p><p><a href="/?led=on"><button class="button">ON</button></a></p>
      <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
      <p>Estado deposito: <strong>""" + estado_deposito + """</strong>    
      </body></html>"""
      return html

def webserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    while True:
        des_on, des_off, conn = pedido(s)
        
        if des_on == -1 and des_off == -1:
            refresh(conn, -1)
        elif des_on == 6:
            print('Desumidificador ON')
            Cnt_desHUM.value(1)
            refresh(conn, 1)
        elif des_off == 6:
            print('Desumidificador OFF')
            Cnt_desHUM.value(0)
            refresh(conn, 0)
   
def cntagua():
  print(Cnt_Agua_sys.read())
  print('')
  print(Cnt_Agua_rede.read())
  print('')


#### Sinalização dos contactos auxiliares ####
##############################################
#
# Bloco transporte
#
#########################################

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

while True:
   webserver()
   #Read_BME()
   #nivel()
   #CntAux()
   #cntagua()

