# Configuração do ambiente do LangFlow

Este é um guia para realizar as configurações necessárias para que o LangFlow seja executado em uma máquina local, e na mesma maquina também executando o servidor do Ollama e seus serviços, no caso o modelo de sua escolha como, (llama3, llama4, mistral, gemma, qwen, etc).

## Configurando no ambiente: 

 * [Linux](#Sistema-Linux-UbuntuDebian) - sistema operacional.

 * [Windows](#Sistema-Windows-1011) - sistema operacional. 


---


## Sistema Linux (Ubuntu/Debian)	

## 1. Precisa ter o docker instalado na máquina, caso não, segue abaixo a instalação.

 - Configurar o docker apt repositório:
  
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

 - Para instalar a versão mais recente, execute:
  
		sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

 - Verifique se a instalação foi bem-sucedida executando o hello-worldimagem:
  
		sudo docker run hello-world

 - Para maiores detalhes segue o link abaixo:

    https://docs.docker.com/engine/install/ubuntu/


## 2. Baixar as imagens do LangFlow do repositório do docker hub.

 - Em um terminal baixe a imagem correspondente à ultima versão,
   o comando irá verificar se a imagem existe, caso não, irá fazer o download e em seguida executar o Langflow:
   
		sudo docker run -it --rm -p 7860:7860 langflowai/langflow:latest
   
 - Acesse o Langflow com o link abaixo no seu navegador da web:

		http://localhost:7860

 - Para maiores detalhes segue o link abaixo:

    https://hub.docker.com/r/langflowai/langflow

 - Para verificar as imagens que existe na maquina:

		sudo docker images

## 3. Baixe o Ollama e os modelos LLM do site oficial.

 - Execute o comando abaixo para instalar o servidor Ollama:

		curl -fsSL https://ollama.com/install.sh | sh

 - A execução Ollama é automática: À um problema, o servidor só libera a porta 11434 para o IP localhost e como o 
   Langflow está em um docker ele não vai enxergar o Ollama, Segue abaixo a correção para isso:
  
	- Altere o arquivo de serviço do ollama:
		
		sudo nano /etc/systemd/system/ollama.service

	- Substitua a linha como mostra abaixo:

		# Substitua:  
		
		ExecStart=/usr/local/bin/ollama serve

		# Por este:
		
		ExecStart=/usr/bin/env OLLAMA_HOST=0.0.0.0:11434 /usr/local/bin/ollama serve

	- Recarregue o systemd e reinicie o serviço:

		sudo systemctl daemon-reload
		sudo systemctl restart ollama

 - Segue o link do site oficial para escolher o modelo LLM que desejar:

    https://ollama.com/search

 - Para executar o modelo, o comando verificará se existe o modelo no local, caso não, 
   irá fazer o download e em seguida executar:

		ollama run llama3

 - Para verificar os modelos que existem na maquina:

		ollama list

## 4. Segue o link para a documentação do Langflow.

 - Agora é só estudar e ficar, expert... ;)

    https://docs.langflow.org/


---


## Sistema Windows (10/11)


## 1. Precisa ter o docker instalado na máquina, caso não, segue abaixo a instalação.

 - Verificar se o docker já está instalado, no PowerShell ou Prompt de Comando (cmd), digite:
 
		docker --version

 - Instalar o Docker Desktop no Windows, baixe o executável do link abaixo:
 
 	 - Clique duas vezes no arquivo baixado, durante a instalação, certifique-se de que a opção 
	 "Use WSL 2 instead of Hyper-V" esteja marcada (recomendado para Windows 10 e 11), 
	 Siga as instruções e reinicie o PC, se necessário.

    https://www.docker.com/products/docker-desktop

 - Verifique se a instalação foi bem-sucedida executando o hello-worldimagem, no PowerShell execute:

		docker run hello-world


## 2. Baixar as imagens do LangFlow do repositório do docker hub.

 - No PowerShell, baixe a imagem correspondente à ultima versão,
   o comando irá verificar se a imagem existe, caso não, irá fazer o download e em seguida executar o Langflow:
   
		docker run -it --rm -p 7860:7860 langflowai/langflow:latest
   
 - Acesse o Langflow com o link abaixo no seu navegador da web:

		http://localhost:7860

 - Para maiores detalhes segue o link abaixo:

    https://hub.docker.com/r/langflowai/langflow

 - Para verificar as imagens que existe na maquina:

		docker images


## 3. Baixe o Ollama e os modelos LLM do site oficial.

 - Instalar o Ollama no Windows

	- Vá para o site oficial, clique em “Download for Windows”, Instale o Ollama normalmente (arquivo .exe).
	
	- Após a instalação, o servidor Ollama é iniciado automaticamente, escutando apenas em localhost:11434.

	- Problema: Docker (LangFlow) não consegue acessar o localhost do Windows, o container Docker não enxerga diretamente o localhost do host, então é preciso expor o servidor Ollama na rede local, faça um redirecionar o tráfego de rede.
	
	- Procure a linha IPv4 Address (exemplo: 192.168.0.105), é o seu IP local, no PowerShell digite:

		ipconfig

	- Crie um redirecionamento da porta com netsh, abra o PowerShell como Administrador e execute:

		netsh interface portproxy add v4tov4 listenport=11434 listenaddress=0.0.0.0 connectport=11434 connectaddress=127.0.0.1

	- Agora containers do Docker podem acessar o Ollama no endereço:

		http://<IP_LOCAL>:11434


 - Segue o link do site oficial para escolher o modelo LLM que desejar:

    https://ollama.com/search

 - Para executar o modelo, o comando verificará se existe o modelo no local, caso não, 
   irá fazer o download e em seguida executar:

		ollama run llama3

 - Para verificar os modelos que existem na maquina:

		ollama list


## 4. Segue o link para a documentação do Langflow.

 - Agora é só estudar e ficar, expert... ;)

    https://docs.langflow.org/

