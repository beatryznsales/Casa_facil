import os
import sqlite3
import math
import inquirer
import requests
import unicodedata
from . import Logs_erros
from .tabelas import mostrar_tabela 
from .cancelamentos import pedir_input, OperacaoCancelada, informar_cancelamento  # Permite escrever "voltar" para cancelar a operação e regressar ao menu anterior.

pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa 
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "../casa_facil.db")
pathlogs = os.path.join(pasta_programa, "../logs_erros.txt")

def adicionar_imovel(): # Permitir cancelar a operação através da palavra "voltar"
    try:
        return _adicionar_imovel()
    except OperacaoCancelada:
        informar_cancelamento()


def _adicionar_imovel():
    print("\n--- ADICIONAR NOVO IMÓVEL ---")
    print("Escreva 'voltar' em qualquer campo para cancelar a operação.")

    # Pedir o NIF do proprietário (Para testes usar o nif: 248516971)
    while True:
        nif_proprietario = pedir_input("NIF do proprietário responsável: ").strip()

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if (len(nif_proprietario) != 9 or not nif_proprietario.isascii() or not nif_proprietario.isdigit()):
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            Logs_erros.logs_erro(901,'NIF invalido', 'Numero de caracteres diferente de 9', pathlogs)
            continue
        else:
            break  

    # Verificar se o proprietário já está registado na base de dados
    conexao = None

    try:
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()
        cursor.execute("SELECT nif FROM proprietarios WHERE nif = ?", (int(nif_proprietario),))

        if cursor.fetchone() is None:
            print(f"\nNão existe nenhum proprietário registado com o NIF {nif_proprietario}.")
            Logs_erros.logs_erro(902,'NIF Inexistente', 'Sem registo de proprietario', pathlogs)
            print("Antes de adicionar um imóvel, registe primeiro o seu proprietário no Menu: 3. Gestão de Proprietários.")
            return

        print("\nProprietário encontrado. Pode continuar o registo do imóvel.")

    except sqlite3.Error as e:
        print(f"\nErro ao verificar o proprietário: {e}")
        Logs_erros.logs_erro(902,'Verificacao invalida', 'Erro a verificar proprietario', pathlogs)
        return

    finally:
        if conexao is not None:
            conexao.close()

    # Recolher e validar os dados da morada
    print("\nIndique os dados da morada do imóvel:")

    # Validar o nome da rua e o número da porta
    while True:
        rua = pedir_input("Nome da rua (sem número da porta): ").strip()

        if rua == "":
            print("O nome da rua não pode estar vazio.")
            Logs_erros.logs_erro(903,'Campo invalido', 'Campo Rua nao preenchido', pathlogs)
            continue

        if len(rua) > 150:
            print("O nome da rua não pode ultrapassar 150 caracteres.")
            Logs_erros.logs_erro(904,'Campo invalido', 'Campo Rua nao pode conter mais de 150 caracteres', pathlogs)
            continue

        # Separar as palavras do nome da rua
        palavras_rua = rua.lower().split()

        # Verificar expressões associadas ao número da porta e bloquea-las
        if "," in rua or any(expressao in palavras_rua for expressao in ["nº", "n.º","n.", "número", "numero"]): 
            print("Não deve inserir o número da porta no campo da rua.")
            Logs_erros.logs_erro(905,'Campo invalido', 'Nao pode colocar o numero da porta no campo da rua', pathlogs)
            continue

        # Verificar e bloquear expressões como n123, n123A, nº123 ou n.º123 no inicio da frase
        if any(palavra.startswith(("nº", "n.º")) or (palavra.startswith("n") and (palavra[1:].isdigit() or (len(palavra) > 2 and palavra[1:-1].isdigit() and palavra[-1].isalpha()))) for palavra in palavras_rua):
            print("Não deve inserir o número da porta no campo da rua.")
            Logs_erros.logs_erro(905,'Campo invalido', 'Nao pode colocar o numero da porta no campo da rua', pathlogs)
            continue

        # Verificar se foi introduzido um código postal
        if any(len(palavra) == 8 and palavra[4] == "-" and palavra[:4].isdigit() and palavra[5:].isdigit() for palavra in palavras_rua):
            print("Não deve inserir o código postal no campo da rua.")
            Logs_erros.logs_erro(906,'Campo invalido', 'Nao pode colocar o codigo postal no campo da rua', pathlogs)
            continue

        # Verificar se existem caracteres inválidos, incluindo vírgulas
        if not all(caracter.isalnum() or caracter in " .'-ºª" for caracter in rua):
            print("O nome da rua contém caracteres inválidos.")
            Logs_erros.logs_erro(907,'Campo invalido', 'foram inseridos caracteres invalidos no campo rua', pathlogs)
            continue

        # Verificar se a rua contém letras
        if not any(caracter.isalpha() for caracter in rua):
            print("O nome da rua deve conter letras.")
            continue

        # Validar o número da porta
        while True:
            num_porta = pedir_input("Número da porta (ex.: 25 ou 25A): ").strip().upper()

            if num_porta == "":
                print("O número da porta não pode estar vazio.")
                Logs_erros.logs_erro(908,'Campo invalido', 'Campo: número da porta - vazio', pathlogs)

            elif len(num_porta) > 5:
                print("O número da porta não pode ultrapassar 5 caracteres.")
                Logs_erros.logs_erro(909,'Campo invalido', 'Campo: número da porta - excesso de caracteres', pathlogs)

            elif (num_porta.isascii() and num_porta.isdigit() and int(num_porta) > 0):
                break

            elif (num_porta[:-1].isascii() and num_porta[:-1].isdigit() and int(num_porta[:-1]) > 0 and num_porta[-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                break

            else:
                print("Número da porta inválido. Exemplos de números de porta: 25 ou 25A")
                Logs_erros.logs_erro(909,'Campo invalido', 'Campo: número da porta - fora das regras estabelecidas', pathlogs)

        # Identificar números presentes no nome da rua
        numeros_rua = []

        for palavra in palavras_rua:
            palavra = palavra.upper().strip(" .'-")

            if palavra.isdigit():
                numeros_rua.append(palavra)

            elif (len(palavra) > 1 and palavra[:-1].isdigit() and palavra[-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"): 
                numeros_rua.append(palavra)

        # Obter a parte numérica da porta
        if num_porta[-1].isalpha():
            numero_comparar = num_porta[:-1]
        else:
            numero_comparar = num_porta

        # Verificar se o número da porta aparece no nome da rua
        numero_repetido = False

        for numero in numeros_rua:
            if numero[-1].isalpha():
                numero_rua = numero[:-1]
            else:
                numero_rua = numero

            if numero_rua == numero_comparar:
                numero_repetido = True
                break

        # Pedir confirmação quando existe uma possível repetição
        if numero_repetido:
            print("\nAtenção: O número da porta também aparece no nome da rua.")
            Logs_erros.logs_erro(910,'Campo invalido', 'Informação duplicada', pathlogs)
            print("\n")

            while True:
                resposta = pedir_input("Esse número faz parte do nome oficial da rua? (Sim [S]/Não [N]): ").strip().lower()
                if resposta in ["sim", "s"]:
                    break

                elif resposta in ["não", "nao", "n"]:
                    print("Não introduza a morada completa, apenas o nome da rua.")
                    print("Introduza novamente apenas o nome da rua.")
                    break

                else:
                    print("Resposta inválida. Introduza Sim ou Não.")
                    Logs_erros.logs_erro(911,'Resposta Invalida', 'So sao aceites respostas de sim ou nao', pathlogs)

            if resposta in ["não", "nao", "n"]:
                continue

        break

    # Validar o andar/fração (campo opcional)
    while True:
        num_apartamento = pedir_input("Andar/Fração (se houver, ex.: 2.º Esq., R/C ou 3B): ").strip()

        if num_apartamento == "":
            break

        elif len(num_apartamento) > 15:
            print("A identificação do andar/fração não pode ultrapassar 15 caracteres.")
            Logs_erros.logs_erro(912,'Campo invalido', 'Excedeu o numero de caracteres', pathlogs)

        elif not all(caracter.isalnum() or caracter in " .ºª/-" for caracter in num_apartamento):
            print("A identificação do andar/fração contém caracteres inválidos.")
            Logs_erros.logs_erro(913,'Campo invalido', 'Caracteres invalidos', pathlogs)

        elif not any(caracter.isalnum() for caracter in num_apartamento):
            print("A identificação do andar/fração deve conter letras ou números.")
            Logs_erros.logs_erro(914,'Campo invalido', 'Confirme restricoes do campo numero de apartamento', pathlogs)
            
        else:
            break

    # Permitir corrigir o código postal e/ou a cidade caso a API encontre diferenças
    alterar_codigo_postal = True
    alterar_cidade = True

    while True:
        if alterar_codigo_postal:
            # Validar o código postal português
            while True:
                codigo_postal = pedir_input("Código postal (1234-567): ").strip()

                partes = codigo_postal.split("-")

                if len(partes) != 2:
                    print("Código postal inválido. Utilize o formato 1234-567.")
                    Logs_erros.logs_erro(915,'Campo invalido', 'Formato de Código Postal', pathlogs)

                elif not (partes[0].isascii() and partes[1].isascii() and partes[0].isdigit() and partes[1].isdigit()):
                    print("O código postal deve conter apenas números e um hífen.")
                    Logs_erros.logs_erro(915,'Campo invalido', 'Formato de Código Postal', pathlogs)

                elif len(partes[0]) != 4 or len(partes[1]) != 3:
                    print("Código postal inválido. Utilize o formato 1234-567.")
                    Logs_erros.logs_erro(915,'Campo invalido', 'Formato de Código Postal', pathlogs)

                elif partes[0][0] == "0":
                    print("O código postal não pode começar por zero.")
                    Logs_erros.logs_erro(915,'Campo invalido', 'Formato de Código Postal', pathlogs)

                else:
                    break

        if alterar_cidade:
            # Validar o nome da cidade  
            while True:
                cidade = pedir_input("Cidade: ").strip()

                if cidade == "":
                    print("A cidade não pode estar vazia.")
                    Logs_erros.logs_erro(916,'Campo invalido', 'O campo Cidade esta vazio', pathlogs)

                elif len(cidade) > 100:
                    print("O nome da cidade não pode ultrapassar 100 caracteres.")
                    Logs_erros.logs_erro(917,'Campo invalido', 'Numero de caracteres excedido', pathlogs)

                elif not all(caracter.isalpha() or caracter in " '-" for caracter in cidade):
                    print("A cidade deve conter apenas letras, espaços, hífenes ou apóstrofos.")
                    Logs_erros.logs_erro(918,'Campo invalido', 'Caracteres invalidos', pathlogs)

                elif not any(caracter.isalpha() for caracter in cidade):
                    print("A cidade deve conter letras.")
                    Logs_erros.logs_erro(918,'Campo invalido', 'Caracteres invalidos', pathlogs)

                else:
                    break

        divergencia = False

        # Consultar a GEO API PT para verificar o código postal e a cidade (validação complementar)
        # Se a API estiver indisponível, o registo continua com as validações locais anteriores
        try:
            resposta = requests.get(f"https://json.geoapi.pt/cp/{codigo_postal}", timeout=3)

            if resposta.status_code == 200:
                dados = resposta.json()

                # A designação postal, a localidade e o concelho podem ter nomes diferentes
                cidades_api = [dados.get("Designação Postal", ""), dados.get("Localidade", ""), dados.get("Concelho", "")]

                # Retirar os acentos e ignorar diferenças entre maiúsculas e minúsculas
                cidade_introduzida = "".join(caracter for caracter in unicodedata.normalize("NFD", cidade.casefold()) if not unicodedata.combining(caracter))
                cidades_normalizadas = ["".join(caracter for caracter in unicodedata.normalize("NFD", nome.casefold()) if not unicodedata.combining(caracter)) for nome in cidades_api if isinstance(nome, str) and nome]

                if cidade_introduzida in cidades_normalizadas:
                    print("Código postal e cidade confirmados pela API.")
                else:
                    print("\nAtenção: a cidade não corresponde ao código postal introduzido.")
                    Logs_erros.logs_erro(1001,'Erro de Validacao', 'Dados de cidade e codigo postal nao correspondentes', pathlogs)
                    print("Verifique o código postal e a cidade antes de continuar.")
                    print("Dados encontrados:", ", ".join(nome for nome in cidades_api if nome))
                    divergencia = True

            elif resposta.status_code == 404:
                print("\nAtenção: código postal não encontrado na API. Confirme os dados introduzidos.")
                Logs_erros.logs_erro(1002,'Erro de Validacao', 'Ccdigo postal inexistente', pathlogs)
                divergencia = True

            else:
                print("\nNão foi possível validar o código postal online. O registo vai continuar.")
                Logs_erros.logs_erro(1003,'Erro de Validacao', 'Codigo postal não foi validado online', pathlogs)

        except (requests.RequestException, ValueError, TypeError, KeyError):
            # Falha de Internet, do serviço ou da resposta: não bloquear o registo do imóvel
            print("\nValidação online indisponível. O registo vai continuar normalmente.")
            Logs_erros.logs_erro(1004,'Erro de Validacao', 'Validacao online indisponivel', pathlogs)

        # Se a API detetar uma diferença, permitir corrigir os dados antes de continuar
        if divergencia:
            confirmacao = [inquirer.List("confirmar",
                    message="Deseja alterar o código postal ou a cidade?",
                    choices=["Sim", "Não"],
                    default="Sim")
            ]

            resposta = inquirer.prompt(confirmacao)

            # Se não pretender corrigir, manter os dados introduzidos
            if resposta is None or resposta["confirmar"] == "Não":
                print("\nOs dados introduzidos serão mantidos.")
                break

            # Escolher quais os dados que pretende corrigir
            menu = [inquirer.List("campo",
                    message="Que dados pretende alterar?",
                    choices=["Código postal", "Cidade", "Código postal e cidade"])
            ]

            escolha = inquirer.prompt(menu)

            if escolha is None:
                print("\nOs dados introduzidos serão mantidos.")
                break

            alterar_codigo_postal = escolha["campo"] in ["Código postal", "Código postal e cidade"]
            alterar_cidade = escolha["campo"] in ["Cidade", "Código postal e cidade"]

            # Voltar a validar apenas os dados escolhidos e consultar novamente a API
            continue

        # Continuar o registo se a API confirmar os dados ou estiver indisponível
        break

    # Recolher e validar os dados do imóvel
    print("\nIndique os dados do imóvel:")

    # Validar o tipo de imóvel
    while True:
        tipo = pedir_input("Tipo de imóvel (Moradia, Apartamento, Quinta): ").strip().lower()

        if tipo in ["moradia", "apartamento", "quinta"]:
            tipo = tipo.capitalize()
            break

        else:
            print("Tipo de imóvel inválido. Escolha Moradia, Apartamento ou Quinta.")
            Logs_erros.logs_erro(1005,'Erro de Validacao', 'Tipo Imovel nao correspondente as opcoes', pathlogs)

    # Validar o número de quartos
    quartos = fornecer_validar_quartos()

    # Validar o estado do imóvel
    while True:
        estado = pedir_input("Estado do imóvel (Nova, Seminova, Usada, Em mau estado): ").strip().lower()

        if estado == "nova":
            estado = "Nova"
            break

        elif estado == "seminova":
            estado = "Seminova"
            break

        elif estado == "usada":
            estado = "Usada"
            break

        elif estado == "em mau estado":
            estado = "Em mau estado"
            break

        else:
            print("Estado inválido. Escolha uma das opções apresentadas.")
            Logs_erros.logs_erro(1006,'Erro de Validacao', 'Opcao inexistente', pathlogs)


    renda = fornecer_validar_renda("Valor mensal da renda (€): ")


    # Definir automaticamente a situação inicial do imóvel
    situacao = "Disponível"

    # Verificar o proprietário e inserir o imóvel na base de dados
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        conexao.execute("PRAGMA foreign_keys = ON")
        cursor = conexao.cursor()

        # Verificar se o proprietário já está registado
        cursor.execute("SELECT nif FROM proprietarios WHERE nif = ?", (int(nif_proprietario),))

        if cursor.fetchone() is None:
            print(f"\nNão existe nenhum proprietário registado com o NIF {nif_proprietario}.")
            Logs_erros.logs_erro(1007,'Erro de Validacao', 'NIF nao se encontra no registo de proprietarios', pathlogs)
            print("Registe primeiro o proprietário no menu Gestão de Proprietários.")
            return

        # Inserir a morada na base de dados
        cursor.execute("INSERT INTO moradas(rua, num_porta, num_apartamento, codigo_postal, cidade) VALUES (?, ?, ?, ?, ?)", (rua, num_porta, num_apartamento, codigo_postal, cidade))

        # Obter o ID da morada criada.
        id_morada = cursor.lastrowid

        # Inserir o imóvel e associá-lo à morada e ao proprietário
        cursor.execute("INSERT INTO imoveis (tipo, quartos, id_morada, estado, renda, situacao, nif_proprietario) VALUES (?, ?, ?, ?, ?, ?, ?)", (tipo, quartos, id_morada, estado, renda, situacao, int(nif_proprietario)))

        # Atualizar o número de habitações registadas pelo proprietário
        # Com UPDATE proprietarios atualizar o numero de habitações na coluna identificada por SET
        # Com COALESCE() é devolvido o valor já existente na tabela e somado mais um imovel. Converte os NULL em zero
        # WHERE nif = ? indica qual o proprietário cujo registo deve ser atualizado (senão todos os proprietarios aumentariam +1)
        #( ..., ) criam um tuplo com um único elemento (o nif do proprietario)
        cursor.execute("UPDATE proprietarios SET N_habitacoes_registadas = COALESCE(N_habitacoes_registadas, 0) + 1 WHERE nif = ?", (int(nif_proprietario),))

        # Guardar as alterações na base de dados
        conexao.commit()

        print("\nImóvel e respetiva morada adicionados com sucesso!")
        print("Situação do imóvel: Disponível")
        print("\nPara completar o processo de arrendamento, aceda à opção 'Atribuir imóvel a um inquilino' no menu Gestão de Imóveis.")

    except sqlite3.Error as e:
        # Anular as alterações se ocorrer um erro
        if conexao is not None:
            conexao.rollback()

        print(f"\nErro ao adicionar o imóvel: {e}")
        Logs_erros.logs_erro(1008,'Erro de Validacao', 'Erro ao adicionar imovel', pathlogs)

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()

def consultar_imoveis():
    # Consultar todos os imóveis registados e as respetivas moradas

    # Inicializar a variável de ligação à base de dados antes do try
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Consultar os imóveis e os dados das respetivas moradas e proprietários
        # JOIN permite relacionar as tabelas através do ID da morada e do NIF do proprietário
        cursor.execute("""
            SELECT imoveis.id, imoveis.tipo, imoveis.quartos,
                   imoveis.estado, imoveis.renda, imoveis.duracao,
                   imoveis.situacao, imoveis.nif_proprietario,
                   moradas.rua, moradas.num_porta, moradas.num_apartamento,
                   moradas.codigo_postal, moradas.cidade,
                   proprietarios.nome_completo
            FROM imoveis
            JOIN moradas ON imoveis.id_morada = moradas.id
            JOIN proprietarios ON imoveis.nif_proprietario = proprietarios.nif
            ORDER BY imoveis.id
            """)

        # Obter todos os resultados da consulta
        imoveis = cursor.fetchall()

        if len(imoveis) == 0:
            print("\nNão existem imóveis registados.")

        else:
            # Preparar os dados dos imóveis para apresentação em tabela
            dados_imoveis = []

            for imovel in imoveis:
                # Reunir os dados da morada numa única coluna
                andar = f", {imovel[10]}" if imovel[10] else ""
                morada = f"{imovel[8]}, {imovel[9]}{andar}, {imovel[11]} {imovel[12]}"

                # Destacar a situação do imóvel a verde ou vermelho
                situacao = unicodedata.normalize("NFC", imovel[6])
                if situacao == "Disponível":
                    situacao = "[bold green]Disponível[/bold green]"
                elif situacao == "Arrendada":
                    situacao = "[bold red]Arrendada[/bold red]"

                dados_imoveis.append((
                    imovel[0], imovel[1], imovel[2], imovel[3],
                    f"{imovel[4]:.2f} €",
                    imovel[5] if imovel[5] is not None else "Sem contrato",
                    situacao, imovel[7], morada, imovel[13]
                ))

            mostrar_tabela(
                "IMÓVEIS REGISTADOS",
                ["ID", "Tipo", "Quartos", "Estado", "Renda Mensal",
                 "Duração", "Situação", "NIF proprietário",
                 "Morada", "Proprietário"],
                dados_imoveis
            )

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao consultar imóveis: {e}")
        Logs_erros.logs_erro(1009,'Erro de Validacao', 'Erro ao consultar imoveis', pathlogs)

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()

        input("\nPressione Enter para voltar ao menu...")


def consultar_imoveis_disponiveis():
# Estabelecer ligação à base de dados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
        # Consultar apenas os imoveis com status disponível
        # Para que a informação consultada apareça de forma amigavel, junto dados como nome do proprietário e os detalhes da morada
        cursor.execute("SELECT imoveis.*, proprietarios.nome_completo, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.codigo_postal, moradas.cidade " \
        "FROM imoveis JOIN moradas ON imoveis.id_morada = moradas.id JOIN proprietarios ON imoveis.nif_proprietario = proprietarios.nif WHERE situacao IN ('Disponível', 'Disponível')")
        disponiveis = cursor.fetchall()

        if len(disponiveis) == 0:
            print("\nNão existem imóveis disponíveis.")

        else:
            # Preparar os dados dos imóveis disponíveis para apresentação em tabela
            dados_imoveis = []

            for imovel in disponiveis:
                numero_apartamento = ", " + imovel[12] if imovel[12] else ""
                morada = f"{imovel[10]}, {imovel[11]}{numero_apartamento}, {imovel[14]}"

                dados_imoveis.append((
                    imovel[0], imovel[1], imovel[2], imovel[4],
                    f"{imovel[5]:.2f} €",
                    imovel[6] if imovel[6] is not None else "Sem contrato",
                    imovel[9], morada, "[bold green]Disponível[/bold green]"
                ))

            mostrar_tabela(
                "IMÓVEIS DISPONÍVEIS",
                ["ID", "Tipo", "Quartos", "Estado", "Renda",
                 "Duração", "Proprietário", "Morada", "Situação"],
                dados_imoveis
            )

    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis disponiveis.", e)
        Logs_erros.logs_erro(1010,'Erro de Validacao', 'Erro ao consultar imoveis disponiveis', pathlogs)
        return

    finally:
        if conexao is not None:
            conexao.close()

        input("\nPressione Enter para voltar ao menu...")


def consultar_imoveis_alugados():
# Estabelecer ligação à base de dados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
        # Consultar apenas os imoveis com status arrendado
        # Para que a informação consultada apareça de forma amigavel, junto dados como nome do proprietário, inquilino e os detalhes da morada
        cursor.execute("SELECT imoveis.*, proprietarios.nome_completo, inquilinos.nome_completo, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.codigo_postal, moradas.cidade FROM imoveis " \
        "JOIN moradas ON imoveis.id_morada = moradas.id JOIN proprietarios ON imoveis.nif_proprietario = proprietarios.nif JOIN inquilinos ON imoveis.nif_inquilino = inquilinos.nif WHERE situacao = 'Arrendada'")
        arrendados = cursor.fetchall()

        if len(arrendados) == 0:
            print("\nNão existem imóveis arrendados.")

        else:
            # Preparar os dados dos imóveis arrendados para apresentação em tabela
            dados_imoveis = []

            for imovel in arrendados:
                numero_apartamento = ", " + imovel[14] if imovel[14] else ""
                morada = f"{imovel[12]}, {imovel[13]}{numero_apartamento}, {imovel[16]}"

                dados_imoveis.append((
                    imovel[0], imovel[1], imovel[2], imovel[4],
                    f"{imovel[5]:.2f} €",
                    imovel[6] if imovel[6] is not None else "Sem contrato",
                    imovel[10], imovel[11], morada,
                    "[bold red]Arrendada[/bold red]"
                ))

            mostrar_tabela(
                "IMÓVEIS ARRENDADOS",
                ["ID", "Tipo", "Quartos", "Estado", "Renda",
                 "Duração", "Proprietário", "Inquilino",
                 "Morada", "Situação"],
                dados_imoveis
            )

    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis arrendados.", e)
        Logs_erros.logs_erro(1011,'Erro de Validacao', 'Erro ao consultar imoveis arrendados', pathlogs)
        return

    finally:
        if conexao is not None:
            conexao.close()

        input("\nPressione Enter para voltar ao menu...")

def alterar_dados_imovel():
    # Permitir cancelar a operação através da palavra "voltar"
    try:
        return _alterar_dados_imovel()
    except OperacaoCancelada:
        informar_cancelamento()


def _alterar_dados_imovel ():
    #Adicionar opções de alterações como: Duracao, estado ou renda
    imovel_selecionado = selecionar_imovel(permitir_voltar=True)
    if imovel_selecionado is None:
        return

    id_imovel_selecionado = imovel_selecionado[0]
    alteracao_guardada = False  # Indica se já foi guardada alguma alteração na base de dados

    while True:
        opcoes = [
            "1.Alterar duração do contrato",
            "2.Alterar estado do imovel",
            "3. Alterar valor da renda",
            "4. Alterar tipo do imóvel",
            "5. Alterar número de quartos",
            "0. Terminar edição" if alteracao_guardada else "0. Voltar ao menu anterior"
        ]

        if not alteracao_guardada:
            print("\nAntes de guardar a primeira alteração, pode escrever 'voltar' para cancelar.")

        pergunta = [
            inquirer.List('alteracao',
                message="Indique o que deseja editar nesse imovel",
                choices=opcoes,
            )
        ]

        selecao = inquirer.prompt(pergunta)
        if selecao is None:
            return

        opcao_escolhida = selecao["alteracao"][0]
        if opcao_escolhida == "1":
            #Adicionar validação
            while True:
                if alteracao_guardada:
                    nova_duracao = input("Informe a nova duraçao do contrato: ").strip()
                    if nova_duracao.lower() == "voltar":
                        print("Já existem alterações guardadas. Termine a edição através da opção 0.")
                        continue
                else:
                    nova_duracao = pedir_input("Informe a nova duraçao do contrato: ")
                break

            if alteracoes_imovel(id_imovel_selecionado, "duracao", f"'{nova_duracao}'"):
                alteracao_guardada = True

        elif opcao_escolhida == "2":
            pergunta_estado = [
                inquirer.List('estado',
                    message="Indique o novo estado do imovel",
                    choices=["Novo", "Usado", "Mau Estado", "Remodelado"],
                )
            ]

            respo_novo_estado = inquirer.prompt(pergunta_estado)
            if respo_novo_estado is None:
                continue
            novo_estado = f"'{respo_novo_estado['estado']}'"

            if alteracoes_imovel(id_imovel_selecionado, "estado", novo_estado):
                alteracao_guardada = True

        elif opcao_escolhida == "3":
            nova_renda = fornecer_validar_renda("Indique o novo valor de renda (€): ", permitir_cancelamento=not alteracao_guardada)

            if alteracoes_imovel(id_imovel_selecionado, "renda", nova_renda):
                alteracao_guardada = True
                print(f"Valor da renda alterado com sucesso. Novo valor {nova_renda}")

        elif opcao_escolhida == "4":
            pergunta_estado = [
                inquirer.List('tipo',
                    message="Indique o novo estado do imovel",
                    choices=["Apartamento", "Moradia", "Quinta"],
                )
            ]

            resposta = inquirer.prompt(pergunta_estado)
            if resposta is None:
                continue
            novo_tipo = f"'{resposta['tipo']}'"

            if alteracoes_imovel(id_imovel_selecionado, "tipo", novo_tipo):
                alteracao_guardada = True

        elif opcao_escolhida == "5":
            while True:
                if alteracao_guardada:
                    num_quartos = input("Informe o novo número de quartos: ").strip()
                    if num_quartos.lower() == "voltar":
                        print("Já existem alterações guardadas. Termine a edição através da opção 0.")
                        continue
                else:
                    num_quartos = pedir_input("Informe o novo número de quartos: ")
                break

            if alteracoes_imovel(id_imovel_selecionado, "quartos", num_quartos):
                alteracao_guardada = True

        elif opcao_escolhida == "0":
            if alteracao_guardada:
                print("\nEdição terminada. As alterações efetuadas foram guardadas.")
            else:
                informar_cancelamento()
            break

#Funcao permite atualizar informações do imovel com base do Id, coluna e novo valor passado por argumento
def alteracoes_imovel(imovel_id, coluna, novo_valor):
    #Estabelecer ligação à base de dados
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
        #Coloca os argumentos da funcao na chamada de update para a base de dados.
        cursor.execute(f"UPDATE imoveis SET {coluna} = {novo_valor} WHERE id = {int(imovel_id)}")
        conexao.commit()
        return True

    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis disponiveis.", e)
        Logs_erros.logs_erro(1012,'Erro de Validacao', 'Erro ao consultar imoveis disponiveis', pathlogs)
        return False
    
    finally:
        if conexao is not None:
            conexao.close()

#Lista os imoveis com base no filtro passado por argumento. Caso vazio, lista sem filtro
def selecionar_imovel(filtro = "", permitir_voltar=False):
    #Estabelecer ligação à base de dados
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    escolhas = {} #Usado para criar um dicionário com as opções: id do imóvel, e morada contendo rua, número de porta e apartamento, cidade e renda do imovel
    sql = "SELECT imoveis.id, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.cidade, imoveis.renda FROM imoveis JOIN moradas ON imoveis.id_morada = moradas.id"

    if filtro != "":
        sql = sql + f" WHERE {filtro}"

    try:
        #Listar ID do imóvel, informacao da morada e a renda
        cursor.execute(sql)
        imoveis = cursor.fetchall()

        #Definir opções de escolhas para o utilizador
        for imovel in imoveis:
            numero_apartamento = ""
            if imovel[3]:
                numero_apartamento = ", "+imovel[3] 
            morada = f"{imovel[1]}, {imovel[2]}{numero_apartamento}, {imovel[4]}"
            escolhas[morada]= imovel

    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis disponiveis.", e)
        Logs_erros.logs_erro(1012,'Erro de Validacao', 'Erro ao consultar imoveis disponiveis', pathlogs)
        return
    
    finally:
        if conexao is not None:
            conexao.close()

    # Permitir regressar ao menu anterior antes de selecionar o imóvel a editar
    if permitir_voltar:
        escolhas["0. Voltar ao menu anterior"] = None

    pergunta = [
        inquirer.List('imovel',
            message="Indique o imóvel que deseja editar",
            choices=escolhas.keys(),
        )
    ]

    selecao = inquirer.prompt(pergunta)
    if selecao is None:
        return None
    morada_escolhida = selecao["imovel"]
    if permitir_voltar and morada_escolhida == "0. Voltar ao menu anterior":
        informar_cancelamento()
        return None
    print(f"Imóvel na morada \"{morada_escolhida} selecionado")
    imovel_selecionado = escolhas[morada_escolhida]

    return imovel_selecionado

#Essa função captura a entrada do utilizador para o numero de quartos
#Utilizada tanto para alteração quanto criação de imóveis
def fornecer_validar_quartos():
    while True:
        try:
            quartos = int(pedir_input("Número de quartos: ").strip())

            if quartos < 0:
                print("O número de quartos não pode ser negativo.")
                Logs_erros.logs_erro(1013,'Erro de Validacao', 'Erro de input do numero de quartos', pathlogs)
                continue

            return quartos

        except ValueError:
            print("Introduza um número inteiro válido para os quartos.")
            Logs_erros.logs_erro(1013,'Erro de Validacao', 'Erro de input do numero de quartos', pathlogs)

#Essa função captura a entrada do utilizador para o valor da renda
#Utilizada tanto para alteração quanto criação de imóveis
def fornecer_validar_renda(messagem, permitir_cancelamento=True):
    # Validar o valor mensal da renda
    while True:
        try:
            # Converter o valor introduzido num número decimal
            # .replace(",", ".") permite introduzir a vírgula como separador decimal
            if permitir_cancelamento:
                valor = pedir_input(messagem)
            else:
                valor = input(messagem).strip()
                if valor.lower() == "voltar":
                    print("Já existem alterações guardadas. Termine a edição através da opção 0.")
                    continue
            renda = float(valor.replace(",", "."))

            # Verificar se a renda é positiva e finita, rejeitando valores negativos, zero, infinito e NaN
            if renda <= 0 or not math.isfinite(renda):
                print("A renda deve ser um valor positivo e finito.")
                Logs_erros.logs_erro(1014,'Erro de Validacao', 'Valor de renda não aceite', pathlogs)
                continue
            return renda

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para a renda.")
            Logs_erros.logs_erro(1014,'Erro de Validacao', 'Valor de renda não aceite', pathlogs)

#Atribui um inquilino existente num imóvel Disponível
def atribuir_imovel_inquilino():
    # Permitir cancelar a operação através da palavra "voltar".
    try:
        return _atribuir_imovel_inquilino()
    except OperacaoCancelada:
        informar_cancelamento()


def _atribuir_imovel_inquilino():
    print("\nEscreva 'voltar' em qualquer campo para cancelar a operação.")
    #Retorna o imóvel disponível escolhido pelo o utilizador
    imovel_selecionado = selecionar_imovel("situacao = 'Disponível'")
    imovel_renda = imovel_selecionado[5] #Pega a sexta coluna da consulta anterior
    imovel_id = imovel_selecionado[0] #Pega a primeira coluna que é o id do imovel

    nif = pedir_input("Informe o NIF do inquilino: ") #Pede o nif do inquilino ao utilizador

    #Efetua a busca do inquilino filtrando pelo nif
    inquilino = buscar_inquilino(nif)

    #Quando a busca não encontrar um inquilino nos encerramos a função
    if inquilino is None:
        print("Inquilino não encontrado. Registre-o primeiro")
        return

    #A busca retorna o id do imovel, caso seja tem um id significa que o inquilino já tem imóvel
    if inquilino[7] is not None:
        print("Inquilino já atribuido a um imovel")
        return

    #A renda do imovel não pode ultrapassar 60% do ordenado do inquilino
    inquilinos_ordenado = inquilino[6]
    #Calcular se o ordenado atende ao requisito
    limite_maximo = inquilinos_ordenado * 0.60

    if imovel_renda > limite_maximo:
        print("Atribuição negada por conta da renda")
        return

    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()
    try:
        #Atualizar a situação do imovel para arrendada e incluir o nif do inquilino
        cursor.execute(
            """
                UPDATE imoveis 
                SET nif_inquilino = ?, situacao = 'Arrendada'
                WHERE id = ?
            """,
            (nif, imovel_id),
        )
        #Confirmar atribuição
        conexao.commit()
        print("Inquilino atribuído o sucesso!")
    finally:
        #Fechar a conexão
        if conexao is not None:
            conexao.close()

#Retorno um único inquilino mais o id do imóvel associado a ele
def buscar_inquilino(nif):
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()
    try:
        #O select usa o left join para garantir que caso nao exista imovel para o inquilino retorne null
        cursor.execute(f"SELECT inquilinos.*, imoveis.id FROM inquilinos LEFT JOIN imoveis ON imoveis.nif_inquilino = inquilinos.nif WHERE nif = {nif}")
        inquilino = cursor.fetchone()
        
        return inquilino
    except:
        print("Erro na procura de inquilino")
        Logs_erros.logs_erro(1015,'Erro de Validacao', 'Erro na procura de inquilino', pathlogs)
        return None
    finally:
        if conexao is not None:
            conexao.close()

#Atualiza o imovel arrendado para diponível e remove o inquilino
def encerrar_contrato_arrendamento():
    #Retorna o imóvel arrendado escolhido pelo o utilizador
    imovel_selecionado = selecionar_imovel("situacao = 'Arrendada'")
    imovel_id = imovel_selecionado[0]

    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()
    try:
        #Atualizar a base de dados
        cursor.execute(f"UPDATE imoveis SET nif_inquilino = NULL, situacao = 'Disponível' WHERE id = {imovel_id}")

        #Confirmar atribuição
        conexao.commit()
        print("Contrato encerrado!")
    finally:
        #Fechar a conexão
        if conexao is not None:
            conexao.close()