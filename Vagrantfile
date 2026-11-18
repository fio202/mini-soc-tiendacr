# -*- mode: ruby -*-
# Mini SOC "TiendaCR" - laboratorio local en VirtualBox
#   siem     192.168.56.20  Ubuntu 24.04 + Wazuh (manager, indexer, dashboard)
#   target   192.168.56.10  Ubuntu 24.04 + DVWA (Docker) + nginx + Suricata + agente Wazuh
#   attacker 192.168.56.30  Kali Linux
# Red solo-anfitrion 192.168.56.0/24; el anfitrion (laptop) es 192.168.56.1.
#
# Orden recomendado:  vagrant up siem && vagrant up target && vagrant up attacker

SIEM_IP     = "192.168.56.20"
TARGET_IP   = "192.168.56.10"
ATTACKER_IP = "192.168.56.30"
HOST_IP     = "192.168.56.1"
WAZUH_SERIES = "4.14"

Vagrant.configure("2") do |config|
  config.vm.box_check_update = false
  # Usa el resolvedor DNS del anfitrion (evita fallos intermitentes del DNS del NAT)
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  config.vm.define "siem" do |s|
    s.vm.box = "bento/ubuntu-24.04"
    s.vm.hostname = "tiendacr-siem"
    s.vm.network "private_network", ip: SIEM_IP
    s.vm.provider "virtualbox" do |vb|
      vb.name = "tiendacr-siem"
      vb.memory = 8192
      vb.cpus = 4
    end
    s.vm.provision "shell", path: "provision/common.sh",
      env: { "TEAM_IPS" => HOST_IP }
    s.vm.provision "shell", path: "provision/siem.sh",
      env: { "WAZUH_SERIES" => WAZUH_SERIES, "TARGET_IP" => TARGET_IP, "HOST_IP" => HOST_IP }
    # Reglas propias + respuesta activa:  vagrant provision siem --provision-with rules
    s.vm.provision "rules", type: "shell", path: "provision/siem-rules.sh"
  end

  config.vm.define "target" do |t|
    t.vm.box = "bento/ubuntu-24.04"
    t.vm.hostname = "tiendacr-web"
    t.vm.network "private_network", ip: TARGET_IP
    t.vm.provider "virtualbox" do |vb|
      vb.name = "tiendacr-web"
      vb.memory = 4096
      vb.cpus = 2
      # Suricata necesita ver todo el trafico de la interfaz solo-anfitrion
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end
    t.vm.provision "shell", path: "provision/common.sh",
      env: { "TEAM_IPS" => "#{HOST_IP} #{ATTACKER_IP}" }
    t.vm.provision "shell", path: "provision/target.sh",
      env: { "WAZUH_SERIES" => WAZUH_SERIES, "SIEM_IP" => SIEM_IP,
             "TARGET_IP" => TARGET_IP, "TEAM_IPS" => "#{HOST_IP} #{ATTACKER_IP}" }
    # Reglas propias de Suricata:  vagrant provision target --provision-with rules
    t.vm.provision "rules", type: "shell", path: "provision/target-rules.sh"
    # Punto 2.8 (solo bajo demanda):
    #   vagrant provision target --provision-with remediate    (estado remediado)
    #   vagrant provision target --provision-with vulnerable   (estado original)
    t.vm.provision "remediate", type: "shell", run: "never",
      path: "provision/remediation.sh", env: { "MODE" => "remediate" }
    t.vm.provision "vulnerable", type: "shell", run: "never",
      path: "provision/remediation.sh", env: { "MODE" => "vulnerable" }
  end

  config.vm.define "attacker", autostart: false do |a|
    a.vm.box = "kalilinux/rolling"
    a.vm.hostname = "tiendacr-kali"
    a.vm.network "private_network", ip: ATTACKER_IP
    a.vm.provider "virtualbox" do |vb|
      vb.name = "tiendacr-kali"
      vb.memory = 4096
      vb.cpus = 2
      vb.gui = false
    end
  end
end
