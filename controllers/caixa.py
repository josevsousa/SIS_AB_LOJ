# -*- coding: utf-8 -*-

@auth.requires_login()
def etapa_1():
    if not session.parcelada:
        session.parcelada = " "

    representante = ''   
    if session.representante:
        representante = db(db.representantes.id == session.representante ).select('nome')[0].nome

    # form cliente e representante
    form = SQLFORM.factory(
        Field('Cliente',default=session.cliente, requires = IS_NOT_EMPTY(error_message = "Digite o nome do cliente"
            ), widget = SQLFORM.widgets.autocomplete(
            request, db.clientes.nome, limitby=(0,5), min_length=1))
        #     # Field('Cliente',default=session.cliente , requires = IS_IN_DB(db, Clientes.nome, error_message = 'Escolha um cliente'),
            # Field('Cliente', default=session.cliente, requires = IS_IN_DB(db, Clientes.nome, error_message = 'Escolha um representante') ),
            #Field('Representante',default=representante , requires = IS_IN_DB(db, Representantes.nome, error_message = 'Escolha um representante'))
        )
    if form.process().accepted:
        nomeCliente = form.vars.Cliente
        session.cliente = nomeCliente
        session.email_Cliente = db(db.clientes.nome == nomeCliente).select('email')[0].email
        #session.representante = db(db.representantes.nome == form.vars.Representante ).select('id')[0].id
        #cria codigo da venda  
        if not session.codigo_venda:
            from datetime import datetime
            now = datetime.now()
            session.codigo_venda =  now.strftime("%y%m%d""%S%M%H")
            pass    
        redirect(URL('etapa_2?menu=caixa')) 
    
    form.add_button('Cadastrar Cliente', URL('clientes','/cadastrarClientes?menu=clientes'))


    # #<!-- codigo, data, itens, sub_total, tipo_pagamento, desconto  -->
    # message = dict(nome='jose ok')
    # mail.send(to=['jose.vicente.de.sousa@gmail.com'],
    #     subject='Recebido da artesanalbaby',
    #     message = ['confira seu email!', response.render('romaneio.html',message)]
    #     )
        
    return dict(form=form)   



# ------------------ ETAPA 2 ---------------------
@auth.requires_login()
def etapa_2():
    grid = db(Itens.codigoVenda == session.codigo_venda).select() 
    # ---- sTotal
    sTotal = 0.0
    for iten in grid:
        sTotal += float(iten.valorTotal)  
    session.sTotal = sTotal
    # ---- fim sTotal
    return dict(grid=grid, sTotal=sTotal)

def produto():
    codigo = request.vars.codigo
    produto = request.vars.produto
    qtde = request.vars.qtde
    valorVariado = request.vars.valor

    if codigo == '1003':
        valorUn = round(float(valorVariado.replace('R$','').replace(' ','').replace(',','')),2)
        valorTotal = int(qtde)*valorUn
    else:
        valorUn = round(float((db(db.produtos.codigo_produto == codigo).select('preco_produto_lojinha'))[0].preco_produto_lojinha),2)
        
        valorTotal = int(qtde)* valorUn
        pass
    
    Itens.insert(codigoVenda=session.codigo_venda,codigoIten=codigo,produto=produto,quantidade=qtde,valorUnidade=valorUn,valorTotal=valorTotal)
    
    #-----------------redirect(URL('etapa_2?menu=caixa')) 
 
def delItem():
    index = request.vars.transitory
    # index = index.split(";")
    db(Itens.id == index).delete()
    # session.venda_sTotal = float(session.venda.sTotal) - float(index[1]) #subtração do valor dos itens

def buscaCodigo():
    cod = request.vars.transitory
    iten = db(db.produtos.codigo_produto == "%s"%cod).select('nome_produto') 
    # se o iten existir!
    if iten:
        ret =  "$('#no_table_qtde').attr('disabled',false).focus();$('#no_table_produto').val(%s);$('#no_table_codigo').css('color','#555').parent().removeClass('has-error')"% repr(iten[0].nome_produto)
    else:
        ret =  "$('#no_table_qtde').attr('disabled',true);$('#no_table_codigo').parent().addClass('has-error').children().focus().css('color','red');$('#no_table_produto').val('')"
        pass
    return ret

def buscaProduto():
    prod = request.vars.transitory
    iten = db(db.produtos.nome_produto == "%s"%prod).select('codigo_produto') 
    # se o iten existir!
    if iten:
        ret =  "$('#no_table_qtde').attr('disabled',false).focus();$('#no_table_codigo').val(%s);$('#no_table_produto').css('color','#555').parent().removeClass('has-error');$('input[type=submit]');"% repr(iten[0].codigo_produto)
    else:
        ret =  "$('#no_table_qtde').attr('disabled',true);$('#no_table_produto').parent().addClass('has-error').children().focus().css('color','red');$('#no_table_codigo').val('')"
        pass
    return ret
# ------------------ FIM DA ETAPA 2 ---------------------

# ----------------------- ETAPA 3 -----------------------
def etapa_3():
    return dict(sTotal = session.sTotal, sTotal_F = double_real(session.sTotal).real())
# ------------------ FIM DA ETAPA 3 ---------------------

# @auth.requires_login()
def clientes_retorno():
    pattern = '%' + request.vars.itens + '%' #primeira letra maiusculo
    selecionado = [row for row in db(db.clientes.nome.like(pattern)).select()] #select no db
    #se a session nao existir criar ela

    if not session.venda.codigo:
        from datetime import datetime
        now = datetime.now()
        # session.venda.codigo =  "%s%s%s%s%s%s"% (now.second,now.minute,now.hour,now.day,now.month,now.year)
        session.venda.codigo =  now.strftime("%y%m%d""%S%M%H")

    
        # response.flash = "Codigo da venda : %s"%session.vendaAtual_codigo  

    for s in selecionado:
        session.venda.nome = s.nome
        session.venda.celular = s.celular
        session.venda.email = s.email

    # userDiv = UL(
    #   LI(STRONG('Nome : '),SPAN(session.vendaAtual_nome,_id="nn"),_class="list-group-item"),
    #   LI(STRONG('Celular : '),SPAN(session.vendaAtual_celuar),_class="list-group-item"),
    #   LI(STRONG('E-mail : '),SPAN(session.vendaAtual_email),_class="list-group-item"),_class="list-group")

# @auth.requires_login()
def fecharVenda():
    index = request.vars.transitory
    index = index.split(";")
    # dados a gravar no db
    codigoVenda = session.codigo_venda
    email = session.cliente
       
    tipoVenda = index[0]
    valorVenda = index[1]
    valorDesconto = index[2]
    totalParcelas = index[4]
    sendEmail = index[5]
    sendEmailPara = index[6]
    # pegar o nome do representante e gravar o id no historico
    representante = 'sem representante'

     # Parcela, DataVencimento, Valor
    if tipoVenda == 'boleto' or tipoVenda == 'cheque':
        for iten in session.parceladaDB:
            valor = "%.2f"%(float(valorVenda)/int(totalParcelas))
            Parcelados.insert(codigo=codigoVenda, tipoVenda=tipoVenda, cliente=email, representante=representante, parcela=iten['iten'], dataVencimento=iten['data'], valor=valor)
    vendedor = session.auth.user.email #pegar usuario logado        
    itensVenda = crud.select(Itens, Itens.codigoVenda == '%s'%codigoVenda,['codigoIten','quantidade','produto','valorUnidade','valorTotal'])
    
    if valorDesconto == '':
        valorDesconto = '0.00'
        pass
    db.historicoVendas.insert(codigoVenda = codigoVenda,clienteEmail = email,tipoVenda = tipoVenda,valorVenda = valorVenda,valorDesconto = valorDesconto,  vendedor = vendedor, representante = representante ) 
    viewDesc = ""
    if valorDesconto != "0.00":
        valorT = (float(valorVenda) + float(valorDesconto))
        viewDesc = "<h3><b>Total</b> : R$ %.2f - <b>Desconto</b> : <span>R$ %.2f</span></h3>"%(valorT, float(valorDesconto))

    if sendEmail == 'true':
        enviar_email(codigoVenda,sendEmailPara,(datetime.now()).strftime('%d/%m/%Y %H:%M:%S'))
    else:
        print 'email nao enviado'
    
    
    temp_codigoVenda = session.codigo_venda
    session.__delitem__('codigo_venda')
    session.__delitem__('cliente')
    #session.__delitem__('representante')  

#--------------------------------    

def reenviarEmail():
    index = request.vars.transitory
    index = index.split(';')
    enviar_email(index[0],index[1],index[2]) 
    # redirect(URL('etapa_2?menu=caixa'))  

def enviar_email(codigo, email,data):
    historico = db(db.historicoVendas.codigoVenda == '%s'%codigo).select()
    desconto = historico[0].valorDesconto
    total = historico[0].valorVenda
    subTotal = total+desconto
    total = "R$ %.2f"%total
    tipoVenda = historico[0].tipoVenda 
    dataRomaneio = data

    # itens = crud.select(Itens, Itens.codigoVenda == '%s'%codigo,['codigoIten','quantidade','produto','valorUnidade','valorTotal'])
    itens = db(Itens.codigoVenda == '%s'%codigo).select()
    
    parcelasCheque = False;
    
    # CHEQUE?
    if tipoVenda == 'cheque':
        cheques = db(Parcelados.codigo == '%s'%codigo).select()
    else:    
        cheques = ''

    # DESCONTO?    
    if desconto != 0.0:
        mostrarDesconto = "[ Total =  R$ %.2f ] - [ Desconto = R$ %.2f ]"%(subTotal,desconto)
    else:
        mostrarDesconto = ''
    pass
    
    # <!-- codigo, data, itens, sub_total, tipo_pagamento, desconto  -->
    message = dict(codigo=codigo,itens=itens,sub_total=total,desconto=mostrarDesconto,tipo_pagamento=tipoVenda,cheques=cheques,data=dataRomaneio)
    emailSimples = "|---------------- RECIBO DE COMPRA ----------------|\n"\
    " ### ESSE DISPOSITIVO NAO E POSSIVEL VISUALIZAR OS DADOS ###\n"\
    " ### Por gentileza visualize no seu email."
    emailHTML = response.render('romaneio.html',message)

    if mail:
        if mail.send(to=[email],
            subject='Recibo ArtesanalBaby Cod:%s'%codigo,
            message=['emailSimples', emailHTML]
        ):
            session.flash = 'Romaneio enviado com sucesso!'
        else:
            session.flash = 'Problema ao enviars o email!'
    else:
        session.flash = 'Unable to send the email : email parameters not defined'  


#@auth.requires_membership('admin') 
@auth.requires_login()
def historico():
    # data atual
    hoje = datetime.now()
    mesAno = hoje.strftime('%m/%Y')
    ano = hoje.strftime('%Y')
    mes = hoje.strftime('%m')
    hoje = hoje.strftime('%Y-%m')#pega apenas o ano e mes atual

    # formulario de busca entre datas
    form = SQLFORM.factory(
        Field("date_initial", requires=IS_NOT_EMPTY(error_message="Campo vazio")),
        Field("date_final", requires=IS_NOT_EMPTY(error_message="Campo vazio")),
        formstyle='divs',
        submit_button="Search",
        )

    # formulario aceito
    if form.process().accepted:
        # pegando as datas escolhidas 
        date_initial = form.vars.date_initial 
        date_initial = date_initial.split('/')
        date_initial = "%s-%s-%s"%(date_initial[2],date_initial[0],date_initial[1])
        date_final = form.vars.date_final 
        date_final = date_final.split('/')
        data_final = "%s-%s-%s"%(date_final[2],date_final[0],date_final[1])

        # fazendo consulta entre as datas ecolhidas
        formListar = db((db.historicoVendas.dataVenda >= date_initial) & (db.historicoVendas.dataVenda <= data_final)).select()      
    else:
        #buscar registro do mes e ano atual
        formListar = db(db.historicoVendas.dataVenda.like(hoje+'%')).select()#busca pelo ano e mes atual    
    
    # faturamento
    tbody = TR()
    mes = int(mes)
    for i in range(mes): #varre a quantidade de mes desse ano ate o mes atual
        i_str = str(i+1) #icrementa o loop do for em 1 pra tirar o numero 0 exp: 1,2,3,4...
        mess = i_str.zfill(2) #incrementa o 1,2,3 em 01,02,03 referente ao mes
        valor = db((db.historicoVendas.dataVenda.like('%s-%s%s'%(ano,mess,'%'))) & (db.historicoVendas.deletado == False)).select('valorVenda') #tabela dos meses desse ano
        valor = valor.column() #pega os valores da coluna e coloca em um [10,2,56,2,65] etc..
        total_mes = 0
        for val in valor:
            total_mes += val

        if total_mes != 0:
            if str(mes) == i_str:
                print 'esse e o mes kkkkkkkkkk - ',i_str
                tbody.append(TD(double_real(total_mes).real(),_class="destaque"))
            else:
                print 'esse nao e o mes mmmmmmmmmm - ',str(mes)
                tbody.append(TD(double_real(total_mes).real()))
        else:
            tbody.append(TD(double_real(total_mes).real(),_class="faturamento_pendente"))


    faturamento = TABLE( 
        THEAD(
            TR(
                TH('Janeiro'),
                TH('Fevereiro'),
                TH('Março'),
                TH('Abril'),
                TH('Maio'),
                TH('Junho'),
                TH('Julho'),
                TH('Agosto'),
                TH('Setembro'),
                TH('Outubro'),
                TH('Novembro'),
                TH('Desembro')
                ),
            ),
        TBODY(tbody),
        _class="table", _id="faturamento")



    return dict(formListar=formListar, mesAtual=mesAno, form=form, faturamento=faturamento)

def historico_busca():
    return ''

def historico_print():
    # codigo da venda
    cod_venda = request.vars.cod 
    # historico da venda ( venda referente ao cod_venda )
    historico_venda = db(Historico.codigoVenda == "%s"%cod_venda).select() 

    dataVenda = historico_venda[0].dataVenda
    dataVenda = dataVenda.strftime('%d/%m/%Y %H:%M:%S')
    # ok ate aqui
    # itens da venda 
    itens_venda =  db(Itens.codigoVenda == "%s"%cod_venda).select('codigoIten','quantidade','produto','valorUnidade','valorTotal')
    
    # ver se a venda foi parcelada
    if historico_venda[0].tipoVenda == 'cheque' or historico_venda[0].tipoVenda == 'boleto':
        # enviar a tabela com as parcelas para a view
        itens_parcelas = db(Parcelados.codigo == "%s"%cod_venda).select('parcela','dataVencimento','valor')
    else:
        itens_parcelas = ""
        pass    
    return dict(historico_venda=historico_venda,itens_venda=itens_venda, itens_parcelas=itens_parcelas, dataVenda=dataVenda) 

def cancelarVenda():  
    # limpar itens do db
    db(Itens.codigoVenda == session.codigo_venda).delete()
    # session.venda
    session.__delitem__('codigo_venda')
    session.__delitem__('cliente')
    

def excluirVendaRegistrada():
    codigo = request.vars.transitory
    db(db.historicoVendas.codigoVenda == codigo).update(deletado=True)
    db(db.pendentes.codigo == codigo).update(status='Finalizado')
    db(db.parcelados.codigo == codigo).update(excluido=True)
    return ''

def parcelado():
    #numero de parcelas e valor da venda
    dados = request.vars.transitory
    dados = dados.split(';')
    qtdeParcelas = int(dados[0])
    #pegar o valor total na session.sTotal
    valorDaParcela = float(dados[1])/qtdeParcelas

    from datetime import datetime, timedelta
    meses = 1
    dias_por_mes = 30
    hoje = datetime.now()
    # # dt_futura = hoje + timedelta(dias_por_mes*meses)

    itens = ""  
    enviar_itens = [] 
    for x in range(qtdeParcelas):
        dt = (hoje + (timedelta(dias_por_mes*(x+1)))).strftime("%d/%m/%Y")
        dtt = (hoje + (timedelta(dias_por_mes*(x+1)))).strftime("%Y-%m-%d %H:%M:%S")
        itens = itens+"<tr><td>%d</td><td>%s</td><td>%s</td></tr>"%(x+1, dt,double_real(valorDaParcela).real())
        enviar_itens.append({'iten':x+1,'data':dtt, 'valor': valorDaParcela})

    session.parceladaDB = enviar_itens

    grid = XML(
        "<table class='table table-striped table-bordered hover pld no-footer'>"+
            "<thead>"+
                "<th>Parc</th>"+
                "<th>Data</th>"+
                "<th>Valor</th>"+   
            "</thead>"+
            "<tbody>"+
            "%s"%itens+
            "</tbody>"+
        "</table>"
        )

    session.parcelada = grid #grid para o a tela de print

    return grid






