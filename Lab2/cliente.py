#servidor de echo: lado cliente
import socket

HOST = 'localhost' # maquina onde esta o servidor
PORT = 10000       # porta que o servidor esta escutando

def iniciaCliente():
	'''Cria um socket de cliente e conecta-se ao servidor.
	Saida: socket criado'''
	# cria socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet (IPv4 + TCP) 

	# conecta-se com o servidor
	sock.connect((HOST, PORT)) 

	return sock

def fazRequisicoes(sock):
	'''Faz requisicoes ao servidor e exibe o resultado.
	Entrada: socket conectado ao servidor'''
	print("Caso opte por entrar com chaves e valores, siga o padrão -> chave: valor ")
	print("Para finalizar esta conexão, digite 'fim'")
	# le as mensagens do usuario ate ele digitar 'fim'
	while True:
		msg = input("Digite uma mensagem :   	")
		if msg == 'fim':
			print("Finalizando conexão com o servidor")
			break

		# envia a mensagem do usuario para o servidor
		sock.send(msg.encode('utf-8'))

		#espera a resposta do servidor
		msg = sock.recv(1024)

		# imprime a mensagem recebida
		print(str(msg, encoding='utf-8'))

	# encerra a conexao
	sock.close()

def main():
	'''Funcao principal do cliente'''
	#inicia o cliente
	sock = iniciaCliente()
	#interage com o servidor ate encerrar
	fazRequisicoes(sock)

main()
 
