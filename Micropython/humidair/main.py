# Instituto Superior de Engenharia do Porto
# HumidAir - Solução para Reaproveitamento de Água em Piscinas Aquecidas

# Copyright (c) 2022 - 2023
# Daniel Gonçalves e Eduardo Ramalhadeiro, Nº 1180812/1210171,
# 1180812@isep.ipp.pt/1210171@isep.ipp.p

# Full project code available in: https://github.com/danilmour/Sistema-de-Reaproveitamento-de-Agua

# Based on: https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/
# Complete project details at https://RandomNerdTutorials.com

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#######################################
# Realiza pedido de estado dos botões #
#######################################

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
    try:
        conn.send(response)
    except:
        print ('')    
    
    conn.close()
    return  deshum_on, deshum_off, central_on, central_off

#####################################################
# Informação desumidificador/temperatura            #
# Ligação ao sensor de temperatura/humidade via SPI #
#####################################################

def Read_BME(n):
    try:
        temperature, raw_humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                         tempOversampling=bme280.OVSMPL_4,
                                                         humidityOversampling=bme280.OVSMPL_4,
                                                         pressureOversampling=bme280.OVSMPL_4)

        # Se necessário por uma questão de depuração
        #print(
        #    f"{temperature:.1f} *C; {raw_humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

    except bme280.BME280Error as e:
        print(f"BME280 error: {e}")
    
    humidity = raw_humidity * 100
    
    # Valor pré-definido da humidade por questões de simulação
    if humidity > nivel_humidade and n == 1:
        Cnt_desHUM.value(1)
    elif humidity < nivel_humidade or n == 0:
        Cnt_desHUM.value(0)


    return temperature, humidity

########################################
# Cálculo do nível da água no depósito #
# Controlo da válvula de 3 vias        #
# Define o estado eletroválvula        #
########################################

def nivel():
    global Estado_EletroValvula
    
    sensor = HCSR04(trigger_pin = trig, echo_pin = echo, echo_timeout_us = echo_timeout)

    distancia = sensor.distance_cm()
    
    # depósito com água suficiente
    if distancia > distancia_min and distancia < distancia_max:
        nivel_medio = 1
        nivel_minimo = 0
        nivel_maximo = 0
        S1.value(1) # boia em baixo
        S2.value(0)
        Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito
        Estado_EletroValvula = 0  # Sistema alimentado pelo Humidair

    # Limite minimo - depósito vazio
    if distancia > distancia_max:
        nivel_medio = 0
        nivel_minimo = 1
        nivel_maximo = 0
        S1.value(0)
        S2.value(0)
        Cnt_V3V.value(0)  # Válvula de 3 vias fechada - enche depósito
        Estado_EletroValvula = 1  # sistema alimentado pela rede

    # Limite máximo - depósito cheio
    if distancia < distancia_min:
        nivel_medio = 0
        nivel_minimo = 0
        nivel_maximo = 1
        S1.value(1)
        S2.value(1)
        Cnt_V3V.value(1)  # Válvula 3 vias aberta - água fora
        Estado_EletroValvula = 0  # Sistema alimentado pelo Humidair

    return nivel_maximo, nivel_medio, nivel_minimo


##############################################################
# A função web_page retorna uma variável html                #
# que contém o texto HTML necessário para construir a página #
##############################################################

def web_page(n, m):
    global time_start
    global estado_desumidificador
    global estado_central
       
    temperatura, humidade = Read_BME(n)
    
    # Leitura do estados dos motores
    leitura_motor1 = Cnt_Dis_C1.value()
    leitura_motor2 = Cnt_Dis_C2.value() 
    
    Cntagua(leitura_motor1, leitura_motor2, m)
    
############################################################################
# Antes gerar a página o texto HTML todas as variáveis têm de ser testadas #
############################################################################ 

    nivel_maximo, nivel_medio, nivel_minimo = nivel()
    if nivel_maximo == 1:
        estado_deposito = "CHEIO"
    elif nivel_medio == 1:
        estado_deposito = "Medio"
    elif nivel_minimo == 1:
        estado_deposito = "vazio" 
    
    # Leitura do estados dos motores
    if leitura_motor1 == 1:
       estado_motor1 = "OK"
    elif leitura_motor1 == 0:
       estado_motor1 = "Verificar Motor"
    if leitura_motor2 == 1:
       estado_motor2 = "OK"
    elif leitura_motor2 == 0:
       estado_motor2 = "Verificar Motor"
   
   # Estad do desumidificador e central
    if n == 1:
        estado_desumidificador = "ON"
    elif n == 0:
        estado_desumidificador = "OFF"
        
    if m == 1:
        estado_central = "ON"
        Cnt_Central.value(1)
    elif m == 0:
        estado_central = "OFF"
        Cnt_Central.value(0)
     
    time_start = rtc.datetime()
    #time.sleep (1)

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
                                """ + estado_desumidificador + """
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <b>Central</b>
                            </td>
                            <td>
                                """ + estado_central + """
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
    return html

def webserver():
###########################################################################
# Cria um socket para atender pedidos e enviar o texto HTML como resposta #
###########################################################################

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    global n
    global m
    
    while True:
        des_on, des_off, central_on, central_off = pedido(s, n, m)

        if des_on == 6:
            n = 1
        elif des_off == 6:
            n = 0

        if central_on == 6:
            m = 1
        elif central_off == 6:
            m = 0          

########################################################
#################### Monitorização #####################
#                                                      #
# Pressão do caudal da água                            #
# Contabilização do tempo de funcionamento dos motores #
# Controlo da eletroválvula                            #
#                                                      #
########################################################
def Cntagua(Cnt_Dis_C1, Cnt_Dis_C2, Cnt_central):
    global ctrl # Variável auxiliar que controla a alternância dos motores
    global soma1, soma2, soma3
    global tempoTotal1
    global tempoTotal2
    global time_start

    time.sleep(0.01)  # delay para a leitura atuar na iteração atual.
    # Pouco caudal, bombas funcionam em alternancia
    
    # Teste inicial da variável de controlo
    if Cnt_Dis_C1 == 1 and Cnt_Dis_C2 == 0:
        ctrl = 0
    
    if Cnt_Dis_C1 == 0 and Cnt_Dis_C2 == 1:
        ctrl = 1
    
    if Cnt_Agua_sys.read() < pressao_agua and Estado_EletroValvula == 0 and Cnt_central == 1:
        Cnt_EletroValvula.value(Estado_EletroValvula)
        
        # Contagem do tempo Motor 1
        if ctrl == 0 and Cnt_Dis_C1 == 1:
            Motor_1.value(1)
            Motor_2.value(0)
            time_actual = rtc.datetime()
            soma1 = soma1 + abs(time_actual[6] - time_start[6])
            tempoTotal1 = tempoTotal1 + soma1
                
        # Contagem do tempo Motor 2
        elif ctrl == 1 and Cnt_Dis_C2 == 1:
            Motor_1.value(0)
            Motor_2.value(1)
            time_actual = rtc.datetime()
            soma2 = soma2 + abs(time_actual[6] - time_start[6])
            tempoTotal2 = tempoTotal2 + soma2


        if  soma2 > 5:
            soma2 = 0
            ctrl = 0    
        
        if  soma1 > 5:
            soma1 = 0
            ctrl = 1
            
    # Se na simulação os interruptores estiverem desligados, então, os motores estão parados
    if Cnt_Dis_C1 == 0 and Cnt_Dis_C2 == 0:
        Motor_1.value(0)
        Motor_2.value(0)
            
    # Muito caudal, funcionam as duas bombas em conjunto
    if Cnt_Agua_sys.read() > pressao_agua and Estado_EletroValvula == 0 and Cnt_Dis_C1 == 1 and Cnt_Dis_C2 == 1 and Cnt_central == 1:
        Motor_1.value(1)
        Motor_2.value(1)
        time_actual = rtc.datetime()
        soma3 = soma3 + abs(time_actual[6] - time_start[6])
        tempoTotal1 = tempoTotal1 + soma3
        tempoTotal2 = tempoTotal2 + soma3
        
    if Cnt_Agua_sys.read() > pressao_agua and (Cnt_Dis_C1 == 0 and Cnt_Dis_C2 == 1) or (Cnt_Dis_C1 == 1 and Cnt_Dis_C2 == 0):
        Cnt_EletroValvula.value(1) # Se houver muita pressão mas só um motor estiver operacional,
        Motor_1.value(0)           # o sistema é alimentado pela rede
        Motor_2.value(0)		   # Ambos os motores ficam desligados

    # Depósito vazio, eletroválvula accionada, bombas paradas - sistema sanitário alimentado pela rede
    if Estado_EletroValvula == 1:  
        Cnt_EletroValvula.value(Estado_EletroValvula)


######################################
# Início do funcionamento do sistema #
######################################
bme = bme280.BME280(spiBus={"sck": sckPin_bme280, "mosi": mosiPin_bme280, "miso": misoPin_bme280}, spiCS = spiCSPin_bme280)
rtc = RTC()
while True:
    webserver()
