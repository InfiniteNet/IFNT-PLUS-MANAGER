#!/usr/bin/env python
# encoding: utf-8

import smtplib
import socket
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Coletar dados de sistema e argumentos
nome = sys.argv[1]
ip = sys.argv[2]
adress_os = '/etc/issue.net'

# Ler o sistema operacional
with open(adress_os, 'r') as file:
    os_info = file.read().strip()

# Data e hora da instalação
data_atual = datetime.now()
ano = str(data_atual.year)
mes = str(data_atual.month)
dia = str(data_atual.day)
hora = str(data_atual.hour)
minuto = str(data_atual.minute)
segundo = str(data_atual.second)

# Criar a mensagem de e-mail
msg = MIMEMultipart('alternative')
msg['Subject'] = "INSTALACAO DO SSHPLUS"
msg['From'] = 'www.infinitenet.netn@gmail.com'
msg['To'] = 'www.infinitenet.net@gmail.com'

# Formatar o conteúdo do e-mail
texto_html = f"""
<html>
<head></head>
<body>
<b><i>Olá! Alves</i></b>
<br></br>
<b><i>SEU SCRIPT FOI INSTALADO EM UM VPS<i></b>
<br></br>
<b><p>══════════════════════════</p><b><i>INFORMAÇÕES DA INSTALAÇÃO<i></b>
<br><b><font color="blue">IP:</b> </font><i><b><font color="red">{ip}</font></b></i>
<br><b><font color="blue">Nome: </b></font> <i><b><font color="red">{nome}</font></b></i>
<br><b><font color="blue">Sistema: </b></font> <i><b><font color="red">{os_info}</font></b></i>
<b><p>══════════════════════════</p><b><i>DATA DA INSTALAÇÃO<i></b>
<br><b><font color="blue">Dia: </b></font> <i><b><font color="red">{dia}</font></b></i>
<br><b><font color="blue">Mês: </b></font> <i><b><font color="red">{mes}</font></b></i>
<br><b><font color="blue">Ano: </b></font> <i><b><font color="red">{ano}</font></b></i>
<b><p>══════════════════════════</p><b/>
<b><i>HORA DA INSTALAÇÃO<i>
<br><b><font color="blue">Hora: </b></font><i> <b><font color="red">{hora}</font></b></i>
<br><b><font color="blue">Minutos: </b></font> <i><b><font color="red">{minuto}</font></b></i>
<br><b><font color="blue">Segundos: </b></font> <i><b><font color="red">{segundo}</font></b></i>
<b><p>══════════════════════════</p><b><b><i><font color="#00FF00">By: crazy</i></b></br></p>
</body>
</html>
"""

# Anexar o conteúdo HTML ao e-mail
msg2 = MIMEText(texto_html, 'html')
msg.attach(msg2)

# Configurar o servidor de e-mail
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    # Autenticação segura (substitua pela variável de ambiente)
    email_user = os.getenv('EMAIL_USER', 'infinitenet.net@gmail.com')
    email_pass = os.getenv('EMAIL_PASS', 'Gvt@946894334')
    
    server.login(email_user, email_pass)

    # Enviar o e-mail
    server.sendmail(email_user, 'www.infinitenet.net@gmail.com', msg.as_string())
    server.quit()
    print("E-mail enviado com sucesso.")
except Exception as e:
    print(f"Erro ao enviar o e-mail: {e}")
