# Configuração do ambiente do LangFlow

Este é um guia para realizar as configurações necessárias para que o LangFlow sejá executado em uma máquina local, e na mesma maquina também executando o servidor do Ollama e seus serviços, no caso o modelo de sua escolha como, (llama3, llama4, mistral, gemma, qwen, etc)

## Configurando no ambiente Linux

1. Precisa ter instalado docker na máquina, segue o passos para instalar:

 * Configurar o Docker aptrepositório. 
  
		# Add Docker's official GPG key:
		sudo apt-get update
		sudo apt-get install ca-certificates curl
		sudo install -m 0755 -d /etc/apt/keyrings
		sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
		sudo chmod a+r /etc/apt/keyrings/docker.asc

		# Add the repository to Apt sources:
		echo \
			"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
			$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
			sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
		sudo apt-get update

 * Para instalar a versão mais recente, execute:
  
		sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

 * Verifique se a instalação foi bem-sucedida executando o hello-worldimagem:
  
		sudo docker run hello-world

 * Para maiores detalhes segue o link abaxo:

    https://docs.docker.com/engine/install/ubuntu/


2. Baixar as imagens do docker hub


