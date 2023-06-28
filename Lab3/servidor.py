# Servidor de calculadora usando RPyC
import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import json

#dicionário a ser utilizado para gravar as chaves com valores
dicionario = {}
#lock para acesso do dicionario
#esse cuidado com problemas de concorrência teria sido feito de outra maneira : implementando Manager da biblioteca de multiprocessing
lock = threading.Lock()


class Echo(rpyc.Service):
    '''Classe que oferece as operacoes da nossa manipulação de dicionario'''

    def on_connect(self, conx):
        print("Conexao estabelecida.")

    def on_disconnect(self, conx):
        print("Conexao encerrada.")

    def exposed_remover(self, chave):
        self.remover(chave)

    def exposed_consulta(self, chave):
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

    def exposed_escrita(self, entrada):
        chave, valores_str = entrada.strip().split(':')
        valores = [valor.strip() for valor in valores_str.split(',')]
        if chave in dicionario:
            lock.acquire()
            for valor in valores:
                if valor not in dicionario[chave]:
                    dicionario[chave].append(valor)
            dicionario[chave] = sorted(dicionario[chave])
            self.escreverNoArquivo()
            lock.release()
            return "A chave " + chave + " foi atualizada com o(s) valor(es) inserido(s) "
        else:
            lock.acquire()
            dicionario[chave] = valores
            dicionario[chave] = sorted(dicionario[chave])
            self.escreverNoArquivo()
            lock.release()
            if len(valores) > 1:
                return "A chave " + chave + " foi inicializada com os valores " + ", ".join(valores)
            else:
                return "A chave " + chave + " foi inicializada com o valor " + ", ".join(valores)

    def remover(self,chave):
        if chave in dicionario:
            lock.acquire()
            del dicionario[chave]
            self.escreverNoArquivo()
            lock.release()
            print("A chave " + chave + " foi removida do dicionário")
        else:
            print("A chave " + chave + " não foi encontrada no dicionário")
    def escreverNoArquivo(self):
        with open("dicionario.json", "w") as arquivo:
            json.dump(dicionario, arquivo, indent=4)

    def lerDoArquivo(self):
        global dicionario
        with open("dicionario.json", "r") as arquivo:
            dicionario = json.load(arquivo)


echo = ThreadedServer(Echo, port=10000)
echo.start()
