# Cliente do servidor de manipulação de dicionário
import rpyc

echo = rpyc.connect('localhost', 10000)
while True:
    op = input("Digite uma operacao(escrita,remoção,consulta ou 'fim' para terminar):")
    if op == 'fim':
        echo.close()
        break
    if op == 'remoção':
        chave = input("Entre com a chave: ")
        remocao = echo.root.remover(chave)
        print(remocao)
    elif op == 'consulta':
        chave = input("Entre com a chave: ")
        print(chave)
        consulta = echo.root.consulta(chave)
        print(consulta)
    elif op == 'escrita':
        entrada = input("Entre com uma chave e valor(es), seguindo o padrão -> chave: valor       :")
        escrita = echo.root.escrita(entrada)
        print(escrita)



