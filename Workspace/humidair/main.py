#####################################
# Informação web-server             #
#####################################
# Realiza pedido de estado do botão #
#####################################


def pedido(s, n, m):
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(2048)
    request = str(request)
    print('Content = %s' % request)
    deshum_on = request.find('/?des=on')
    deshum_off = request.find('/?des=off')
    central_on = request.find('/?cen=on')
    central_off = request.find('/?cen=off')
    
    response = web_page(n, m)  # Chama a função web_page
    conn.send('HTTP/1.1 200 OK\r\n')
    conn.send('Content-Type: text/html\r\n')
    conn.send('Connection: close\n\n')
    print ('bla')
    conn.sendall(response)
    conn.close()
    return  deshum_on, deshum_off, central_on, central_off

#####################################
# Informação web-server             #
#####################################
# Refresca a página com novos dados #
#####################################


def refresh(n, m):
    conn, addr = s.accept()    
    response = web_page(n, m)  # Chama a função web_page
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    print ('bla')
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
    #print ('bme_n', n)
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
    elif humidity * 100 < 60 or n == 0:
        Cnt_desHUM.value(0)


    return temperature, humidity*100

########################################
# Cálculo do nível da água no depósito #
########################################
# Bloco armazenamento                  #
########################################


def nivel():
    global Estado_EletroValvula
    
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
        Estado_EletroValvula = 0  # Sistema alimentado pelo Humidair

    # Limite minimo - depósito vazio
    # distancia entre 18 e 20cm
    if distancia > 20:
        nivel_medio = 0
        nivel_minimo = 1
        nivel_maximo = 0
        led_amarelo.value(0)
        led_azul.value(1)
        Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito
        Estado_EletroValvula = 1  # sistema alimentado pela rede

    # Só para uma questão de simulação - TANQUE COMPLETAMENTE CHEI0
    # distancia maior que 20 apaga os leds
    if distancia < 5:
        nivel_medio = 0
        nivel_minimo = 0
        nivel_maximo = 1
        led_amarelo.value(1)
        led_azul.value(1)
        Cnt_V3V.value(1)  # Válvula 3 vias aberta - água fora
        Estado_EletroValvula = 0  # Sistema alimentado pelo Humidair

    return nivel_maximo, nivel_medio, nivel_minimo

########################
# Criação do webserver #
########################


def web_page(n, m):
    global time_start
    global gpio_state
    global gpio_state2

    if n == 1:
        gpio_state = "ON"
    elif n == 0:
        gpio_state = "OFF"
        
    if m == 1:
        gpio_state2 = "ON"
        Cnt_Central.value(1)
    elif m == 0:
        gpio_state2 = "OFF"
        Cnt_Central.value(0)
    
    temperatura, humidade = Read_BME(n)
    nivel_maximo, nivel_medio, nivel_minimo = nivel()

    if nivel_maximo == 1:
        estado_deposito = "CHEIO"
    elif nivel_medio == 1:
        estado_deposito = "Medio"
    elif nivel_minimo == 1:
        estado_deposito = "vazio"
        
    if Cnt_Dis_C1.value() == 1:
       estado_motor1 = "OK"
    elif Cnt_Dis_C1.value() == 0:
       estado_motor1 = "Verificar Motor"
    if Cnt_Dis_C2.value() == 1:
       estado_motor2 = "OK"
    elif Cnt_Dis_C2.value() == 0:
       estado_motor2 = "Verificar Motor"
    
    time_start = rtc.datetime()
    time.sleep (1)

    html = """<html>

                <head>
                    <title>HumidAir</title>
                    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                    <meta http-equiv="refresh" content="2" name="viewport" content="width=device-width, initial-scale=1">
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
                                <b>Central</b>
                            </td>
                            <td>
                                """ + gpio_state2 + """
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
                        <tr>
                            <td>
                                <b>Estado da Eletroválvula</b>
                            </td>
                            <td>
                                """ + str(Estado_EletroValvula) + """
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Estado do Motor 1</b>
                            </td>
                            <td>
                                """ + estado_motor1 + """
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Estado do Motor 2</b>
                            </td>
                            <td>
                                """ + estado_motor2 + """                
                            </td>
                        </tr>
                    </table>
                    <div class="espaco"></div>
                    <table class="table" align="center">
                        <thead>
                            <h2 class="alerta">Paragem de Emergência</h2>
                        </thead>
                        <tr>
                            <td class="alerta">
                                <b>! Desligar Desumidificador - SOS !</b>
                            </td>
                            <td>
                                <a href="/?des=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                                <a href="/?des=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
                            </td>
                        </tr>
                        <tr>
                            <td class="alerta">
                                <b>! Desligar Central - SOS !</b>
                            </td>
                            <td>
                                <a href="/?cen=on"><button class="btn btn-outline-success fs-1 buttons">ON</button></a>
                                <a href="/?cen=off"><button class="btn btn-outline-danger fs-1 buttons">OFF</button></a>
                            </td>
                        </tr>
                    </table>
                </body>

                </html>"""
    Cntagua()
    return html


def webserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    global n
    global m
    
    while True:
        des_on, des_off, central_on, central_off = pedido(s, n, m)

#         if des_on == -1 and des_off == -1:
#             n = -1
#             #refresh(conn, n, m)
        if des_on == 6:
            #Cnt_desHUM.value(1)
            n = 1
            #refresh(conn, n, m)
        elif des_off == 6:
            #Cnt_desHUM.value(0)
            n = 0
            #refresh(conn, n, m)

#         if central_on == -1 and central_off == -1:
#             m = -1
#             #refresh(conn, n, m)
        if central_on == 6:
            #Cnt_Central.value(1)
            m = 1
            #refresh(conn, n, m)
        elif central_off == 6:
            #Cnt_Central.value(0)
            m = 0
        #refresh(n, m)
            
            
def Cntagua():
    global cnt
    global soma1,soma2, soma3
    global tempoTotal1
    global tempoTotal2
    global time_start

    time.sleep(0.01)  # delay para a leitura atuar na iteração atual.
    # Pouco caudal, bombas funcionam em alternancia
    if Cnt_Agua_sys.read() < 1500 and Estado_EletroValvula == 0:
        Cnt_EletroValvula.value(Estado_EletroValvula)
        if cnt == 1:
            # Motor_1 = Pin(14, Pin.OUT)  # Contacto auxiliar - Motor 1
            Motor_1.value(0)
            Motor_2.value(1)
            time_actual = rtc.datetime()
            soma1 = soma1 + abs(time_actual[6] - time_start[6])
            tempoTotal1 = tempoTotal1 + soma1
                
        elif cnt == 0:
            Motor_1.value(1)
            Motor_2.value(0)
            time_actual = rtc.datetime()
            soma2 = soma2 + abs(time_actual[6] - time_start[6])
            tempoTotal2 = tempoTotal2 + soma2
        
        if  soma1 > 5:
            cnt = 0
            soma1 = 0
            
        if  soma2 > 5:
            cnt = 1
            soma2 = 0
                
    # Muito caudal, funcionam as duas bombas em conjunto
    if Cnt_Agua_sys.read() > 1500 and Estado_EletroValvula == 0:
        Motor_1.value(1)
        Motor_2.value(1)
        time_actual = rtc.datetime()
        soma3 = soma3 + abs(time_actual[6] - time_start[6])
        tempoTotal1 = tempoTotal1 + soma3
        tempoTotal2 = tempoTotal2 + soma3

    if Estado_EletroValvula == 1:  # Depósito vazio, eletroválvula accionada, bombas paradas - sistema sanitário alimentado pela rede
        Cnt_EletroValvula.value(Estado_EletroValvula)

    
########################################
# Sinalização dos contactos auxiliares #
########################################
# Bloco transporte                     #
########################################


def CntAux():
    if Cnt_Dis_C1.value() == 1:
        print('Possível avaria MOTOR1')
    elif Cnt_Dis_C1.value() == 0:
        print('Motor 1 OK')

    if Cnt_Dis_C2.value() == 1:
        print('Possível avaria MOTOR2')
    elif Cnt_Dis_C2.value() == 0:
        print('Motor 2 OK')


######################################
# Início do funcionamento do sistema #
######################################
while True:
    webserver()
