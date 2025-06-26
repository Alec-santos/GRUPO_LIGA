# Configuração do ambiente do LangFlow

Este é um guia para realizar as configurações necessárias para que o LangFlow sejá executado em uma máquina local, e na mesma maquina também executando o servidor do Ollama e seus serviços, no caso o modelo de sua escolha como, (llama3, llama4, mistral, gemma, qwen, etc)

## Configurando no ambiente Linux

## 1. Precisa ter o docker instalado na máquina, caso não tenha segue os passos para instalar.

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
   o comando ira verificar se a imagem existe, caso não, irá fazer o download e em seguida executar o Langflow:
   
		docker run -it --rm -p 7860:7860 langflowai/langflow:latest
   
 - Acesse o Langflow com o link abaixo no seu navegador da web:

		http://localhost:7860

- Para maiores detalhes segue o link abaixo:

    https://hub.docker.com/r/langflowai/langflow

## 3. Baixe o modelo do Ollama do site oficial.

 - Execute o comando abaixo para instalar o servidor Ollama:

		curl -fsSL https://ollama.com/install.sh | sh

 - Para executar o servidor Ollama,
   Obs.: a execução é automática porém o servidor só libera a porta 11434 para o IP Host localhost 
   e como o Langflow está em um docker ele não vai enxergar o Ollama, Segue abaixo a correção para isso:
  
		# Pare o servidor ollama:
		
		sudo systemctl stop ollama
		
		# Force o servidor a liberar para todos os IPs na porta 11434:
		
		OLLAMA_HOST=0.0.0.0:11434 ollama serve

- Segue o link site oficial para escolher o modelo LLM que desejar:

    https://ollama.com/search

- Para executar o modelo o comando verificar se existe o modelo no local, caso não, 
  tenha ira fazer o download e em seguida executar o modelo:

		ollama run llama3

- Para verificar os modelos que foram feitos o download na maquina:

		ollama list




