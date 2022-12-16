import utime as time
#from time import sleep, time
from bme280 import BME280

from machine import Pin, ADC, RTC
from hcsr04 import HCSR04
import bme280

led_amarelo = Pin(21, Pin.OUT)  # Led nível superior ao minimo
led_azul = Pin(4, Pin.OUT)  # Led menor que nível minimo

# Leitura dos estados dos contactos auxiliares de disjuntores
Cnt_Dis_C1 = Pin(13, Pin.IN)  # Contacto auxiliar - Motor 1
Cnt_Dis_C2 = Pin(12, Pin.IN)  # Contacto auxiliar - Motor 2

# Leitura dos tempos de funcionamento dos motores
Motor_1 = Pin(14, Pin.OUT)  # Contacto auxiliar - Motor 1
Motor_2 = Pin(27, Pin.OUT)  # Contacto auxiliar - Motor 2

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

cnt = 0
toggle = 0
soma = 0
aux = 0
tempoTotal1 = 0
tempoTotal2 = 0

#####################################
# Informação web-server             #
#####################################
# Realiza pedido de estado do botão #
#####################################


def pedido(s):
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)
    deshum_on = request.find('/?led=on')
    deshum_off = request.find('/?led=off')
    return deshum_on, deshum_off, conn

#####################################
# Informação web-server             #
#####################################
# Refresca a página com novos dados #
#####################################


def refresh(conn, n):
    response = web_page(n)  # Chama a função web_page
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()


##########################################
# Informação desumidificador/temperatura #
##########################################
# Bloco desumidificação                  #
##########################################
# Connect to BME-280 via software SPI with custom pinning (not supported by all microcontrollers):
bme = bme280.BME280(spiBus={"sck": 18, "mosi": 23, "miso": 19}, spiCS=5)
rtc = RTC()


def Read_BME(n):
    try:
        # Synchronously trigger a MODE_FORCED conversion and return the result.
        temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                         tempOversampling=bme280.OVSMPL_4,
                                                         humidityOversampling=bme280.OVSMPL_4,
                                                         pressureOversampling=bme280.OVSMPL_4)

        print(
            f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

    except bme280.BME280Error as e:
        print(f"BME280 error: {e}")

    if humidity * 100 > 60 and n == 1:  # MUDAR ISTO
        Cnt_desHUM.value(1)
    else:
        Cnt_desHUM.value(0)

    return temperature, humidity*100

########################################
# Cálculo do nível da água no depósito #
########################################
# Bloco armazenamento                  #
########################################


def nivel():
    sensor = HCSR04(trigger_pin=25, echo_pin=26, echo_timeout_us=10000)

    distancia = sensor.distance_cm()
    # depósito cheio
    # distancia entre 5 e 8cm
    if distancia > 5 and distancia < 20:
        nivel_medio = 1
        nivel_minimo = 0
        nivel_maximo = 0
        led_amarelo.value(1)
        led_azul.value(0)
        Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito

    # Limite minimo - depósito vazio
    # distancia entre 18 e 20cm
    if distancia > 20:
        nivel_medio = 0
        nivel_minimo = 1
        nivel_maximo = 0
        led_amarelo.value(0)
        led_azul.value(1)
        Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito

    # Só para uma questão de simulação - TANQUE COMPLETAMENTE CHEI0
    # distancia maior que 20 apaga os leds
    if distancia < 5:
        nivel_medio = 0
        nivel_minimo = 0
        nivel_maximo = 1
        led_amarelo.value(1)
        led_azul.value(1)
        Cnt_V3V.value(1)  # Válvula 3 vias aberta - água fora
    time.sleep(1)

    return nivel_maximo, nivel_medio, nivel_minimo

########################
# Criação do webserver #
########################


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

    Cntagua()

    <html>

    <head>
    <title>HumidAir</title>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <meta http-equiv="refresh" content="5" name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        body,
        td {
            text-align: center;
        }

        .buttons {
            width: 150px;
        }

        p,
        td {
            font-size: 15pt;
        }

        h1,
        h2 {
            color: darkblue;
        }

<<<<<<< HEAD:Backup_APAGAR/main.py
        .alerta {
            color: red;
        }

        .espaco {
            height: 100px;
        }
    </style>
</head>
=======
                        .alerta {
                            color: red;
                        }

                        .espaco {
                            height: 100px;
                        }
                    </style>
                </head>

                <body>
                    <h1><b>HumidAir</b></h1>
                    <hr>
                    <table class="table">
                        <thead>
                            <h2>Informações</h2>
                        </thead>
                        <tr>
                            <td>
                                <b>Desumidificador</b>
                            </td>
                            <td>
                                """ + gpio_state + """
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Temperatura</b>
                            </td>
                            <td>
                                """ + str(temperatura) + """ ºC
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Humidade</b>
                            </td>
                            <td>
                                """ + str(humidade) + """ %
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Estado do Depósito</b>
                            </td>
                            <td>
                                """ + estado_deposito + """
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Tempo de funcionamento da Bomba 1</b>
                            </td>
                            <td>
                                """ + str(tempoTotal1) + """ s
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Tempo de funcionamento da Bomba 2</b>
                            </td>
                            <td>
                                """ + str(tempoTotal2) + """ s
                            </td>
                        </tr>
                    </table>
                    <div class="espaco"></div>
                    <table class="table" align="center">
                        <tr>
                            <h2 class="alerta">Paragem de Emergência</h2>
                        </tr>
                        <tr>
                            <td class="alerta">
                                <b>! Desligar Desumidificador - SOS !</b>
                            </td>
                            <td>
                                <a href="/?led=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                                <a href="/?led=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
                            </td>
                        </tr>
                        <tr>
                            <td class="alerta">
                                <b>! Desligar Central - SOS !</b>
                            </td>
                            <td>
                                <a href="/?central=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                                <a href="/?central=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
                            </td>
                        </tr>
                    </table>
                </body>
>>>>>>> 31ab0a0ceceda717004c13d18f22bb6c1b725bd3:Workspace/humidair/main.py

<body>
    <h1><b>HumidAir</b></h1>
    <hr>
    <table class="table">
        <thead>
            <h2>Informações</h2>
        </thead>
        <tr>
            <td>
                <b>Desumidificador</b>
            </td>
            <td>
                """ + gpio_state + """
            </td>
        </tr>
        <tr>
            <td>
                <b>Temperatura</b>
            </td>
            <td>
                """ + str(temperatura) + """ ºC
            </td>
        </tr>
        <tr>
            <td>
                <b>Humidade</b>
            </td>
            <td>
                """ + str(humidade) + """ %
            </td>
        </tr>
        <tr>
            <td>
                <b>Estado do Depósito</b>
            </td>
            <td>
                """ + estado_deposito + """
            </td>
        </tr>
        <tr>
            <td>
                <b>Tempo de funcionamento da Bomba 1</b>
            </td>
            <td>
                """ + str(tempoTotal1) + """ s
            </td>
        </tr>
        <tr>
            <td>
                <b>Tempo de funcionamento da Bomba 2</b>
            </td>
            <td>
                """ + str(tempoTotal2) + """ s
            </td>
        </tr>
    </table>
    <div class="espaco"></div>
    <table class="table" align="center">
        <tr>
            <h2 class="alerta">Paragem de Emergência</h2>
        </tr>
        <tr>
            <td class="alerta">
                <b>! Desligar Desumidificador - SOS !</b>
            </td>
            <td>
                <a href="/?led=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                <a href="/?led=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
            </td>
        </tr>
        <tr>
            <td class="alerta">
                <b>! Desligar Central - SOS !</b>
            </td>
            <td>
                <a href="/?central=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                <a href="/?central=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
            </td>
        </tr>
    </table>
</body>

</html>
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
            Cnt_desHUM.value(1)
            refresh(conn, 1)
        elif des_off == 6:
            Cnt_desHUM.value(0)
            refresh(conn, 0)


def Cntagua():
    global cnt
    global soma
    global tempoTotal1
    global tempoTotal2

    time.sleep(0.01)  # delay para a leitura atuar na iteração atual.
    if Cnt_Agua_sys.read() < 1500:  # Pouco caudal, bombas funcionam em alternancia
        if cnt == 1:
            time_start = rtc.datetime()
            # Motor_1 = Pin(14, Pin.OUT)  # Contacto auxiliar - Motor 1
            Motor_1.value(0)
            Motor_2.value(1)
            time.sleep(1)
            time_actual = rtc.datetime()
            soma = soma + abs(time_actual[6] - time_start[6])
            tempoTotal1 = tempoTotal1 + soma
            if soma > 5:
                cnt = 0
                soma = 0
        if cnt == 0:
            time_start = rtc.datetime()
            Motor_1.value(1)
            Motor_2.value(0)
            time.sleep(1)
            time_actual = rtc.datetime()
            soma = soma + abs(time_actual[6] - time_start[6])
            tempoTotal2 = tempoTotal2 + soma
            if soma > 5:
                cnt = 1
                soma = 0
    if Cnt_Agua_sys.read() > 1500:  # Muito caudal, funcionam as duas bombas em conjunto
        Motor_1.value(1)
        Motor_2.value(1)
        tempoTotal1 = tempoTotal1 + 1
        tempoTotal2 = tempoTotal2 + 1
        soma = 0
        cnt = 0
        time.sleep(1)

########################################
# Sinalização dos contactos auxiliares #
########################################
# Bloco transporte                     #
########################################


def CntAux():
    if Cnt_Dis_C1.value() == 0:
        print('Possível avaria MOTOR1')
    else:
        print('Motor 1 OK')

    if Cnt_Dis_C2.value() == 0:
        print('Possível avaria MOTOR2')
    else:
        print('Motor 2 OK')


######################################
# Início do funcionamento do sistema #
######################################
while True:
    webserver()
    # Read_BME(0)
    # nivel()
    # Cntagua()
    # CntAux()