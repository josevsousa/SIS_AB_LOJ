def produtos(): 
    path = request.folder+"static/mysqlImport/produtos_AB.csv"
    f = file(path,'r')

    # linha = f.readline().split(',')
    
    for l in f.readlines():
    	linha = l.split(',')
        db.produtos.insert(codigo_produto=linha[1],nome_produto=linha[2],preco_produto_lojinha=linha[3],dataGravado=linha[4])
        # print (codigo_produto=linha[1],nome_produto=linha[2],preco_produto_lojinha=linha[5],dataGravado=linha[4])
    
    f.close()

    return dict()
