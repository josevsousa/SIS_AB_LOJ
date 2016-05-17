# from gluon.storage import Storage
# vendaAtual = Storage()  #vendaAtual é uma session
# vendaAtual.codigo = 5555  #vendaAtual{'codigo':555}


from datetime import datetime, timedelta

class double_real(object):
    def __init__(self, valor):
        self.valor = valor

    # BR R$    
    def real(self):
        valor = '%.2f'%(float(self.valor)) #converte o valor em string e completa a casa decimal em 2
        valor = valor.replace('.','') # tira a virgula da string
        valorT = len(valor)-1 #conta quantos digitos tem a string
        nValor = [] #cria um novoValor vazio
        rValor = 'R$ ' # cria uma string 
        #serpara os digitos em um array
        for item in valor:
            nValor.append(item)
        #         000,00
        if valorT > 1:  
            nValor.insert(-2,',')  
        #     000.000,00
        if valorT > 4:
            nValor.insert(-6,'.')
        # 000.000.000,00
        if valorT > 7:
            nValor.insert(-10,'.')    
        # monta uma string com os valores do array 
        for item in nValor:
            rValor += item   

        return rValor 


    # US $
        #aqui