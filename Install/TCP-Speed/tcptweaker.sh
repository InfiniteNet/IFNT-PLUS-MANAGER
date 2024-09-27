#!/bin/bash
clear
# Verifica se está rodando como root
if [[ "$(whoami)" != "root" ]]; then
  echo -e "\033[1;31mErro: Você precisa rodar este script como root!\033[0m"
  exit 1
fi

# Cabeçalho
tput setaf 7
tput setab 4
tput bold
printf '%35s%s%-20s\n' "TCP Tweaker 1.0"
tput sgr0

# Verifica se as configurações já foram aplicadas
if grep -q "^#PH56" /etc/sysctl.conf; then
  echo ""
  echo "As configurações de rede TCP Tweaker já foram adicionadas no sistema!"
  echo ""
  read -p "Deseja remover as configurações do TCP Tweaker? [s/n]: " -e -i n resposta0

  # Remove as configurações caso o usuário escolha 's'
  if [[ "$resposta0" = 's' ]]; then
    grep -v "^#PH56
net.ipv4.tcp_window_scaling = 1
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 16384 16777216
net.ipv4.tcp_low_latency = 1
net.ipv4.tcp_slow_start_after_idle = 0" /etc/sysctl.conf > /tmp/syscl && mv /tmp/syscl /etc/sysctl.conf

    sysctl -p /etc/sysctl.conf > /dev/null
    echo ""
    echo "As configurações de rede do TCP Tweaker foram removidas com sucesso."
    echo ""
    exit 0
  else
    echo ""
    exit 0
  fi
else
  # Se não foram aplicadas ainda, pede a confirmação do usuário
  echo ""
  echo "Este é um script experimental. Use por sua conta e risco!"
  echo "Ele vai alterar algumas configurações de rede para reduzir a latência e melhorar a velocidade."
  echo ""
  read -p "Continuar com a instalação? [s/n]: " -e -i n resposta

  # Aplica as configurações caso o usuário confirme
  if [[ "$resposta" = 's' ]]; then
    echo ""
    echo "Modificando as seguintes configurações no sistema:"
    {
      echo " " 
      echo "#PH56"
      echo "net.ipv4.tcp_window_scaling = 1"
      echo "net.core.rmem_max = 16777216"
      echo "net.core.wmem_max = 16777216"
      echo "net.ipv4.tcp_rmem = 4096 87380 16777216"
      echo "net.ipv4.tcp_wmem = 4096 16384 16777216"
      echo "net.ipv4.tcp_low_latency = 1"
      echo "net.ipv4.tcp_slow_start_after_idle = 0"
    } >> /etc/sysctl.conf

    sysctl -p /etc/sysctl.conf
    echo ""
    echo "As configurações de rede do TCP Tweaker foram adicionadas com sucesso."
    echo ""
  else
    echo ""
    echo "A instalação foi cancelada pelo usuário!"
    echo ""
    exit 0
  fi
fi
