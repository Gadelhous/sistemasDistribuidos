#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
#utilizando a biblioteca de json para arquivar o dicionário
import socket
import select
import sys
import threading
import json

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10000 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena historico de conexoes 
conexoes = {}
#dicionário a ser utilizado para gravar as chaves com valores
dicionario = {}
#lock para acesso do dicionario
#esse cuidado com problemas de concorrência teria sido feito de outra maneira : implementando Manager da biblioteca de multiprocessing
lock = threading.Lock()


def iniciaServidor():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 


	print("Abrindo o servidor na porta " + str(PORT))
	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))

	# coloca-se em modo de espera por conexoes
	sock.listen(5) 

	# configura o socket para o modo nao-bloqueante
	sock.setblocking(False)

	# inclui o socket principal na lista de entradas de interesse
	entradas.append(sock)

	return sock

def aceitaConexao(sock):
	'''Aceita o pedido de conexao de um cliente
	Entrada: o socket do servidor
	Saida: o novo socket da conexao e o endereco do cliente'''

	# estabelece conexao com o proximo cliente
	clisock, endr = sock.accept()

	# registra a nova conexao
	conexoes[clisock] = endr 

	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''

	while True:
		#recebe dados do cliente
		data = clisock.recv(1024) 
		if not data: # dados vazios: cliente encerrou
			print("A conexão com " +str(endr) + ' foi encerrada')
			clisock.close() # encerra a conexao com o cliente
			return 
		#passando os valores de entrada para a função que decide se será feita uma consulta ou uma escrita
		feedback = interpretarEntrada(str(data, encoding='utf-8'))
		clisock.send(feedback.encode('utf-8')) # ecoa os dados para o cliente

def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	clientes=[] #armazena as threads criadas para fazer join
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	print("Para realizar remoções, digite  'remover ' seguido da chave desejada")
	try:
		lerDoArquivo()
	except FileNotFoundError:
		print("O arquivo contendo os dados do dicionário não foi encontrado.")
	while True:
		#espera por qualquer entrada de interesse
		leitura, escrita, excecao = select.select(entradas, [], [])
		#tratar todas as entradas prontas
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = aceitaConexao(sock)
				print ('Conectado com: ', endr)
				#cria nova thread para atender o cliente
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr))
				cliente.start()
				clientes.append(cliente) #armazena a referencia da thread para usar com join()
			elif pronto == sys.stdin: #entrada padrao
				cmd = input()
				if cmd == 'fim': #solicitacao de finalizacao do servidor
					for c in clientes: #aguarda todas as threads terminarem
						c.join()
					sock.close()
					sys.exit()
				elif cmd.startswith('remover'):  # Verifica se o comando começa com "remover"
					chave = cmd.split(' ')[1]  # Separa o valor da chave a ser removida
					remover(chave)

def remover(chave):
	if chave in dicionario:
		lock.acquire()
		del dicionario[chave]
		escreverNoArquivo()
		lock.release()
		print("A chave " + chave + " foi removida do dicionário")
	else:
		print("A chave " + chave + " não foi encontrada no dicionário")

def adicionar(chave,valor):
	dicionario[chave] = valor

def interpretarEntrada(str):
	tokens = str.strip().split(':')

	if len(tokens) == 1:
		return consulta(tokens[0])
	elif len(tokens) > 1:
		chave, valores_str = str.strip().split(':')
		valores = [valor.strip() for valor in valores_str.split(',')]
		return escrita(chave, valores)
	return "Nenhuma operação foi executada"

def consulta(chave):
	lock.acquire()
	if chave in dicionario:
		dicionario[chave] = sorted(dicionario[chave])
		if len(dicionario[chave]) > 1:
			lock.release()
			return "Os valores encontrados na chave " + chave + " foram " + ", ".join(str(valor) for valor in dicionario[chave])
		else:
			lock.release()
			return "O valor encontrado na chave " + chave + " foi " + str(dicionario[chave][0])
	else:
		lock.release()
		return "[]  -> A chave " + chave + " não foi encontrada no dicionario"

def escrita(chave,valores):
	if chave in dicionario:
		lock.acquire()
		for valor in valores:
			if valor not in dicionario[chave]:
				dicionario[chave].append(valor)
		dicionario[chave] = sorted(dicionario[chave])
		escreverNoArquivo()
		lock.release()
		return "A chave " + chave + " foi atualizada com o(s) valor(es) inserido(s) "
	else:
		lock.acquire()
		dicionario[chave] = valores
		dicionario[chave] = sorted(dicionario[chave])
		escreverNoArquivo()
		lock.release()
		if len(valores) > 1:
			return "A chave " + chave + " foi inicializada com os valores " + ", ".join(valores)
		else:
			return "A chave " + chave + " foi inicializada com o valor " + ", ".join(valores)

def escreverNoArquivo():
	with open("dicionario.json", "w") as arquivo:
		json.dump(dicionario, arquivo, indent=4)

def lerDoArquivo():
	global dicionario
	with open("dicionario.json", "r") as arquivo:
		dicionario = json.load(arquivo)

main()
