#!/bin/bash
# By alves_s.a
# Pequeno script para permissão de autenticação root

clear

# Verifica se o script está sendo executado como root
if [[ "$(whoami)" != "root" ]]; then
    clear
    echo -e "\033[1;31mERRO: Você deve executar este script como root. \033[1;32m(\033[1;33msudo -i\033[1;32m)\033[0m"
    exit 1
fi

# Ajusta as configurações de SSH para permitir login root e autenticação por senha
sed -i "s/prohibit-password/yes/g" /etc/ssh/sshd_config
sed -i "s/without-password/yes/g" /etc/ssh/sshd_config
sed -i "s/#PermitRootLogin/PermitRootLogin/g" /etc/ssh/sshd_config

# Verifica se a configuração de 'PasswordAuthentication' existe, se não, adiciona
if ! grep -q "PasswordAuthentication" /etc/ssh/sshd_config; then
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
fi

# Habilita 'PasswordAuthentication' caso esteja desabilitado
sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/g" /etc/ssh/sshd_config
sed -i "s/#PasswordAuthentication no/PasswordAuthentication yes/g" /etc/ssh/sshd_config

# Reinicia o serviço SSH para aplicar as mudanças
systemctl restart ssh

# Configura regras de firewall (iptables) para abrir as portas necessárias
iptables -F
iptables -A INPUT -p tcp --dport 81 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 8799 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 1194 -j ACCEPT

# Solicita que o usuário defina a senha de root
clear
echo -ne "\033[1;32mDEFINA A SENHA ROOT\033[1;37m: "
read -s senha

# Validação para garantir que uma senha foi fornecida
if [[ -z "$senha" ]]; then
    echo -e "\n\033[1;31mSENHA INVÁLIDA! Por favor, tente novamente.\033[0m"
    exit 1
fi

# Define a senha de root
echo "root:$senha" | chpasswd
echo -e "\n\033[1;31m[ \033[1;33mOK! \033[1;31m]\033[1;37m - \033[1;32mSENHA DEFINIDA COM SUCESSO! \033[0m"
