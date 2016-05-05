# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
# @auth.requires_membership('admin')

@auth.requires_login()
def index():
    #redireciona para outra pagina se o usuario for do grupo operacional_A
    redirect(URL('caixa','etapa_1?menu=caixa')) 
    #if auth.has_membership('operacional_A'):
    #    redirect(URL('caixa','etapa_1?menu=caixa')) 

    from datetime import datetime, timedelta
    meses = 1
    dias_por_mes = 30
    hoje = datetime.now()
    dt_futura = hoje + timedelta(dias_por_mes*meses)

    # dados para o grafico
    ano = int(hoje.strftime('%Y'))
    ano = ano - 3
    dadosgraf = []
    for i in range(1,4):
        #burcar dados do grafico
        dadosgraf.append([ano+i,[49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]])
    
    form = SQLFORM.factory(
        Field("date_initial", requires=IS_NOT_EMPTY(error_message="Campo vazio")),
        Field("date_final", requires=IS_NOT_EMPTY(error_message="Campo vazio")),
        formstyle='divs',
        submit_button="Search",
        )

    # response.flash = T("Seja bem vindo!  %s !"%(hoje.strftime('%d/%m/%Y')))
    return locals()

def updateSt():
    index = request.vars.transitory  
    index = index.split(';')
    db(db.parcelados.id == index[0]).update(statusPagamento=index[1], dataPagamento=index[2])

def cheques_boletos():
    from datetime import datetime, timedelta
    meses = 1
    dias_por_mes = 30
    hoje = datetime.now()
    dt_futura = hoje + timedelta(dias_por_mes*meses)

    pattern = '%' + request.vars.transitory + '%' #primeira letra maiusculo
    query = db((db.parcelados.id>0) & (db.parcelados.excluido != True) & (db.parcelados.dataVencimento.like(pattern)) ).select()
    
    itens = ''
    for i in query:
        representante = db(db.representantes.id == i.representante ).select('nome')[0].nome
        if i.excluido != True:
            itens = itens+"<tr><td style='display:none'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='check'><div class='check_%s'></div></td><tr>"%(i.id, i.codigo, i.tipoVenda, (i.dataVencimento).strftime('<b style="color:red">%d</b>/%m/%Y'), i.parcela, double_real(float(i.valor)).real(), i.cliente, representante, i.statusPagamento)
            pass
        pass
    table = XML("%s %s"%(itens,'<script>window.onload = checkOk();</script>')) # carregar funcao no DOM  
    # table = query   
                                  
    return table

def cheques_boletos_buscar():
    index = request.vars.transitory
    index = index.split(';')
    date_initial = index[0] 
    date_initial = date_initial.split('/')
    date_initial = "%s-%s-%s"%(date_initial[2],date_initial[0],date_initial[1])
    date_final = index[1] 
    date_final = date_final.split('/')
    data_final = "%s-%s-%s"%(date_final[2],date_final[0],date_final[1])
    

    # # fazendo consulta entre as datas ecolhidas
    query = db((db.parcelados.dataVencimento >= date_initial) & (db.parcelados.dataVencimento <= data_final)).select()      
   
    itens = ''
    for i in query:
        representante = db(db.representantes.id == i.representante ).select('nome')[0].nome
        if i.excluido != True:
            itens = itens+"<tr><td style='display:none'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='check'><div class='check_%s'></div></td><tr>"%(i.id, i.codigo, i.tipoVenda, (i.dataVencimento).strftime('<b style="color:red">%d</b>/%m/%Y'), i.parcela, double_real(float(i.valor)).real(), i.cliente,representante, i.statusPagamento)
            pass
        pass

    table = XML("%s %s"%(itens,'<script>window.onload = checkOk();</script>')) # carregar funcao no DOM 
    return table  

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def tela_representantes():

    pattern = '%' + request.vars.transitory + '%' #primeira letra maiusculo
    # queryHistoricoVendas = db((db.historicoVendas.id>0) & (db.historicoVendas.deletado != True) & (db.historicoVendas.dataVenda.like(pattern)) ).select()

    # grafico = DIV(_id="container", _style='min-width: 300px; height: 400px; margin: 0 auto')
    rows = TBODY()

    # busca representantes
    for representante in db(db.representantes.id>0).select():
        # representante jose
        comissaoVendas = 0.0
        qtdeVendas = 0
        for venda in db((db.historicoVendas.representante == representante.id) & (db.historicoVendas.deletado != True) & (db.historicoVendas.dataVenda.like(pattern))).select():
            # print "*** %s ***"%
            comissaoVendas += float(venda.valorVenda)
            qtdeVendas += 1
        row = TR(TD(representante.nome),TD(qtdeVendas),TD(double_real(comissaoVendas).real()),TD(double_real((comissaoVendas*10/100)).real()))
        rows.append(row)

    return TABLE(THEAD(TR(TH('Representante'),TH('Qtde Vendas'),TH('Total Vendas'),TH('Total Comissão'))),rows,_id="representantes",_class="table hover table-bordered")

def tela_representantes_busca():   
    index = request.vars.transitory
    index = index.split(';')
    date_initial = index[0] 
    date_initial = date_initial.split('/')
    date_initial = "%s-%s-%s"%(date_initial[2],date_initial[0],date_initial[1])
    date_final = index[1] 
    date_final = date_final.split('/')
    data_final = "%s-%s-%s"%(date_final[2],date_final[0],date_final[1])
    # fazendo consulta entre as datas ecolhidas
    
    rows = TBODY()

    # busca representantes
    for representante in db(db.representantes.id>0).select():
        # representante jose
        comissaoVendas = 0.0
        qtdeVendas = 0
        for venda in db((db.historicoVendas.representante == representante.id) & (db.historicoVendas.deletado != True) & ((db.historicoVendas.dataVenda >= date_initial) & (db.historicoVendas.dataVenda <= data_final))).select():
            # print "*** %s ***"%
            comissaoVendas += float(venda.valorVenda)
            qtdeVendas += 1
        row = TR(TD(representante.nome),TD(qtdeVendas),TD(double_real(comissaoVendas).real()),TD(double_real((comissaoVendas*10/100)).real()))
        rows.append(row)

    return TABLE(THEAD(TR(TH('Representante'),TH('Qtde Vendas'),TH('Total Vendas'),TH('Total Comissão'))),rows,_id="representantes",_class="table hover table-bordered")


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


