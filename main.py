#################################################
# WebScraping do B3 - dados dos acionistas      #
#                                               #
# Autor: Felipe Wyatt Varga                     #
# Data: 26/02/2021                              #
#################################################

from selenium import webdriver
from time import sleep

def atualizaCodigos():
    # Obtenção do arquivo .csv contendo os códigos na bolsa de cada empresa, a partir do site

    driver = webdriver.Chrome()
    driver.get('https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/ResultBuscaParticCiaAb.aspx?CNPJNome=&TipoConsult=C')

    tabela = driver.find_element_by_id('dlCiasCdCVM')
    linhas = tabela.find_elements_by_tag_name('tr')     # Cada linha da tabela
    print("Número Total de empresas: " + str(len(linhas)) + "\nObtendo dados...\n")

    saida = open("codigos.csv", "w")
    saida.write("CNPJ,EMPRESA,CODIGO\n")

    contagem = 0
    for linha in linhas[1:]:    # Pula cabeçalho
        celulas = linha.find_elements_by_tag_name("td")
        saida.write("{},{},{}\n".format(celulas[0].text, celulas[1].text, celulas[3].text))

        contagem += 1
        if contagem % 100 == 0:
            print(contagem)

    print(len(linhas))

    saida.close()
    driver.close()


def atualizaAcionistas():
    # Obtém os dados em tempo real dos acionistas das empresas da bolsa de valores B3

    # Driver do selenium, precisa ter o chromedriver.exe no mesmo diretorio
    driver = webdriver.Chrome()

    log = open("log.txt", "w")                      # arq de erros
    codigos = open("codigos.csv", "r")              # arq com os codigos CVM das emrpesas
    saida = open("Tabela_Acionistas.csv", "w")      # saida, planilha com os dados

    # Escreve cabecalho
    saida.write("CODIGO,EMPRESA,TICKER,CNPJ,DATA ACIONISTAS,FISICOS,JURIDICOS,INSTITUCIONAIS,URL B3\n")

    contagemLinhas = 0
    print("Empresas a acessar: " + str(len(codigos.readlines())))

    for l in codigos.readlines()[1:50]: # Pula cabecalho
        contagemLinhas += 1
        if contagemLinhas % 10 == 0:
            print(contagemLinhas)

        # arq csv tem as células separadas por vírgula
        linha = l.split(",")
        codigo = linha[-1].replace("\n", "")
        # Url de cada empresa da bolsa é a mesma, só muda o código da empresa
        url = 'http://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm?codigo=' + codigo

        driver.get(url) # Driver acessa URL
        sleep(1)        # Espera página carregar

        # Testar com url direto para frames
        # Mudar nomes de arquivos

        try:
            # Os dados desejados ficam dentro de 2 frames, e não podem ser acessados por fora do frame
            frame1 = driver.find_element_by_id("bvmf_iframe")
            driver.switch_to.frame(frame1)
            frame2 = driver.find_element_by_id("ctl00_contentPlaceHolderConteudo_iframeCarregadorPaginaExterna")
            driver.switch_to.frame(frame2)
        except:
            log.write("Frames nao encontrados | " + url + "\n")
            continue

        try:
            # Checa se há informações sobre número de acionistas
            # xpath foi obtido inspecionando cada elemento no site
            if driver.find_element_by_xpath('//*[@id="div1"]/div/h3').text != "Ações em Circulação no Mercado":
                # Não é considerado erro, muitos dos links não levam a empresas ativas
                log.write("Nao ha dados disponiveis | " + url + "\n")
                continue
        except:
            log.write("Nao ha dados disponiveis | " + url + "\n")
            continue

        # Obtem dados da empresa
        try:
            nomeEmpresa = driver.find_element_by_xpath('//*[@id="accordionDados"]/table/tbody/tr[1]/td[2]').text
        except:
            log.write("ERRO: Nome nao encontrado " + url + "\n")
            continue

        try:
            ticker = driver.find_element_by_xpath('//*[@id="accordionDados"]/table/tbody/tr[2]/td[2]/a[2]').text
        except:
            ticker = "?"

        try:
            cnpj = driver.find_element_by_xpath('//*[@id="accordionDados"]/table/tbody/tr[3]/td[2]').text
        except:
            cnpj = "?"


        # Obtem dados sobre acionistas
        try:
            tabelaAcionistas = driver.find_element_by_xpath('//*[@id="div1"]/div/table')
            celulas = tabelaAcionistas.find_elements_by_tag_name("td")
            for i in range(len(celulas)):
                celulas[i] = celulas[i].text
        except:
            log.write("Dados sobre acionistas nao encontrados | " + url + "\n")
            continue

        try:
            pFisicas = celulas[celulas.index('Pessoas Físicas') + 1].replace(".","")
        except:
            pFisicas = '0'

        try:
            pJuridicas = celulas[celulas.index('Pessoas Jurídicas') + 1].replace(".","")
        except:
            pJuridicas = '0'

        try:
            pInstitucionais = celulas[celulas.index('Investidores Institucionais') + 1].replace(".","")
        except:
            pInstitucionais = '0'

        try:
            dataAcionistas = driver.find_element_by_xpath('//*[@id="div1"]/div/table/thead/tr[1]/th').text
        except:
            dataAcionistas = '?'

        saida.write("{},{},{},{},{},{},{},{},{}\n".format(codigo, nomeEmpresa, ticker, cnpj, dataAcionistas, pFisicas,
                                                          pJuridicas, pInstitucionais, url))


    log.close()
    codigos.close()
    saida.close()
    driver.close()

# Se arquivo de códigos estiver atualizado, comente o método!
atualizaCodigos()
atualizaAcionistas()
