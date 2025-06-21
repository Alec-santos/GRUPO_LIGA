# Desafio 2 - 18/06

# Projeto de ChatBot para notas fiscais.

* Observação:

  - O sistema só funcionará no S.O. Linux.

  - Na mesma pasta do executável é preciso ter a pasta [data] com os arquivos csv dentro, para o sistema conseguir ler os dados.

  - Para o sistema de chatbot de notas fiscais funcionar é preciso instalar o Ollama no computador.
  
  - O computador precisa ter 6 Gb de memória livre só para o Ollama server executar,
    caso contrário ele vai gerar um erro:
    
		Assistente:			
		Erro ao processar pergunta: Ollama call failed with status code 500. Details: 
		{"error":"model requires more system memory (5.9 GiB) than is available (2.5 GiB)"}


* Instalar o servidor Ollama no computador
	
		curl -fsSL https://ollama.com/install.sh | sh

  - Executar o serviço llama3 no Ollama
	
		ollama run llama3


* Código fonte e o executável do sistema chatbot de notas fiscais: 

  - Em um terminal, faça o clone da pasta [GRUPO_LIGA]
  	
  	Em seguida acesse a pasta [agente_nfs] onde vai encontrar o código fonte, 
    e na pasta [agente_nfs/dist] vai encontrar um arquivo binario que é o executável do chatbot [main].

		./agente_nfs/dist/main
		ou 
		./main
  	
    Obs.: Para compilar o código fonte é preciso criar um ambiente virtual no python 3.12.11.

  - Caso tenha algum problema para executar o sistema de chatbot, baixe o sistema do google drive 
	
		https://drive.google.com/drive/folders/11OEEUWhiPTQOOtvTxx5xGFoG68qJkH98
		

