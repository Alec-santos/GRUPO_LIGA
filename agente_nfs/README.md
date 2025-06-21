# Desafio 2 - 18/06

# Projeto de ChatBot para notas fiscais.

* Observação:

  - A maquina precisa ter 5.9 GiB de memoria Live só para o OLLAMA server executar,
    caso contratio ele vai gerar um erro:
    
    - Erro do assistente: 
			
			Erro ao processar pergunta: Ollama call failed with status code 500. Details: 
			{"error":"model requires more system memory (5.9 GiB) than is available (2.5 GiB)"}

* Baixar o código fonte e o executavel do sistema: 

  - Em um terminal e faça o clone da pasta [GRUPO_LIGA]
  	
  	- Em seguida acesse a pasta [agente_nfs] onde econtra-se o codigo fonte, o executavel do sistema esta na pasta [agente_nfs/dist] encotrara um arquivo binario [main].
  	
  - Para compilar o codifo fonte é preciso criar um ambinete virtual no python 3.12.11, 

  - Para o sistema funcionar é necessario instalar o servidor do OLLAMA no PC. 

		# Instalar o OLLAMA no PC
	
			curl -fsSL https://ollama.com/install.sh | sh

		# Executrar o serviço do Ollama
	
			ollama run llama3

  - Executrar o arquivo binario do ChatBot de notas fiscais, baixe o sistema do google drive 
	
		Link dogoogle drive:
		
		https://drive.google.com/drive/folders/11OEEUWhiPTQOOtvTxx5xGFoG68qJkH98

  - Executar o sistema no Linux ou no Windows: 
	
		./main
		


