import phonenumbers
import datetime
import os
import sqlite3
import math
import inquirer

pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa 
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "../casa_facil.db")

def adicionar_imovel():
    print("\n--- ADICIONAR NOVO IMÓVEL ---")

    # Pedir o NIF do proprietário (Para testes usar o nif: 248516971)
    while True:
        nif_proprietario = input("NIF do proprietário responsável: ").strip()

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if (len(nif_proprietario) != 9 or not nif_proprietario.isascii() or not nif_proprietario.isdigit()):
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
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
            print("Antes de adicionar um imóvel, registe primeiro o seu proprietário no Menu: 3. Gestão de Proprietários.")
            return

        print("\nProprietário encontrado. Pode continuar o registo do imóvel.")

    except sqlite3.Error as e:
        print(f"\nErro ao verificar o proprietário: {e}")
        return

    finally:
        if conexao is not None:
            conexao.close()

    # Recolher e validar os dados da morada
    print("\nIndique os dados da morada do imóvel:")

    # Validar o nome da rua e o número da porta
    while True:
        rua = input("Nome da rua (sem número da porta): ").strip()

        if rua == "":
            print("O nome da rua não pode estar vazio.")
            continue

        if len(rua) > 150:
            print("O nome da rua não pode ultrapassar 150 caracteres.")
            continue

        # Separar as palavras do nome da rua
        palavras_rua = rua.lower().split()

        # Verificar expressões associadas ao número da porta e bloquea-las
        if "," in rua or any(expressao in palavras_rua for expressao in ["nº", "n.º","n.", "número", "numero"]): 
            print("Não deve inserir o número da porta no campo da rua.")
            continue

        # Verificar e bloquear expressões como n123, n123A, nº123 ou n.º123 no inicio da frase
        if any(palavra.startswith(("nº", "n.º")) or (palavra.startswith("n") and (palavra[1:].isdigit() or (len(palavra) > 2 and palavra[1:-1].isdigit() and palavra[-1].isalpha()))) for palavra in palavras_rua):
            print("Não deve inserir o número da porta no campo da rua.")
            continue

        # Verificar se foi introduzido um código postal
        if any(len(palavra) == 8 and palavra[4] == "-" and palavra[:4].isdigit() and palavra[5:].isdigit() for palavra in palavras_rua):
            print("Não deve inserir o código postal no campo da rua.")
            continue

        # Verificar se existem caracteres inválidos, incluindo vírgulas
        if not all(caracter.isalnum() or caracter in " .'-ºª" for caracter in rua):
            print("O nome da rua contém caracteres inválidos.")
            continue

        # Verificar se a rua contém letras
        if not any(caracter.isalpha() for caracter in rua):
            print("O nome da rua deve conter letras.")
            continue

        # Validar o número da porta
        while True:
            num_porta = input("Número da porta (ex.: 25 ou 25A): ").strip().upper()

            if num_porta == "":
                print("O número da porta não pode estar vazio.")

            elif len(num_porta) > 5:
                print("O número da porta não pode ultrapassar 5 caracteres.")

            elif (num_porta.isascii() and num_porta.isdigit() and int(num_porta) > 0):
                break

            elif (num_porta[:-1].isascii() and num_porta[:-1].isdigit() and int(num_porta[:-1]) > 0 and num_porta[-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                break

            else:
                print("Número da porta inválido. Exemplos de números de porta: 25 ou 25A")

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
            print("\n")

            while True:
                resposta = input("Esse número faz parte do nome oficial da rua? (Sim [S]/Não [N]): ").strip().lower()
                if resposta in ["sim", "s"]:
                    break

                elif resposta in ["não", "nao", "n"]:
                    print("Não introduza a morada completa, apenas o nome da rua.")
                    print("Introduza novamente apenas o nome da rua.")
                    break

                else:
                    print("Resposta inválida. Introduza Sim ou Não.")

            if resposta in ["não", "nao", "n"]:
                continue

        break

    # Validar o andar/fração (campo opcional)
    while True:
        num_apartamento = input("Andar/Fração (se houver, ex.: 2.º Esq., R/C ou 3B): ").strip()

        if num_apartamento == "":
            break

        elif len(num_apartamento) > 15:
            print("A identificação do andar/fração não pode ultrapassar 15 caracteres.")

        elif not all(caracter.isalnum() or caracter in " .ºª/-" for caracter in num_apartamento):
            print("A identificação do andar/fração contém caracteres inválidos.")

        elif not any(caracter.isalnum() for caracter in num_apartamento):
            print("A identificação do andar/fração deve conter letras ou números.")

        else:
            break

    # Validar o código postal português
    while True:
        codigo_postal = input("Código postal (1234-567): ").strip()

        partes = codigo_postal.split("-")

        if len(partes) != 2:
            print("Código postal inválido. Utilize o formato 1234-567.")

        elif not (partes[0].isascii() and partes[1].isascii() and partes[0].isdigit() and partes[1].isdigit()):
            print("O código postal deve conter apenas números e um hífen.")

        elif len(partes[0]) != 4 or len(partes[1]) != 3:
            print("Código postal inválido. Utilize o formato 1234-567.")

        elif partes[0][0] == "0":
            print("O código postal não pode começar por zero.")

        else:
            break

    # Validar o nome da cidade  -> podemos adicionar uma API que compara a cidade ao codigo postal? 
    while True:
        cidade = input("Cidade: ").strip()

        if cidade == "":
            print("A cidade não pode estar vazia.")

        elif len(cidade) > 100:
            print("O nome da cidade não pode ultrapassar 100 caracteres.")

        elif not all(caracter.isalpha() or caracter in " '-" for caracter in cidade):
            print("A cidade deve conter apenas letras, espaços, hífenes ou apóstrofos.")

        elif not any(caracter.isalpha() for caracter in cidade):
            print("A cidade deve conter letras.")

        else:
            break

    # Recolher e validar os dados do imóvel
    print("\nIndique os dados do imóvel:")

    # Validar o tipo de imóvel
    while True:
        tipo = input("Tipo de imóvel (Moradia, Apartamento, Quinta): ").strip().lower()

        if tipo in ["moradia", "apartamento", "quinta"]:
            tipo = tipo.capitalize()
            break

        else:
            print("Tipo de imóvel inválido. Escolha Moradia, Apartamento ou Quinta.")

    # Validar o número de quartos
    while True:
        try:
            quartos = int(input("Número de quartos: ").strip())

            if quartos < 0:
                print("O número de quartos não pode ser negativo.")

            else:
                break

        except ValueError:
            print("Introduza um número inteiro válido para os quartos.")

    # Validar o estado do imóvel
    while True:
        estado = input("Estado do imóvel (Nova, Seminova, Usada, Em mau estado): ").strip().lower()

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
            print("\n--- LISTA DE IMÓVEIS ---")

            # Percorrer os imóveis encontrados e apresentar os seus dados
            for imovel in imoveis:
                print("\n" + "-" * 40)
                print(f"ID: {imovel[0]}")
                print(f"Tipo: {imovel[1]}")
                print(f"Número de quartos: {imovel[2]}")
                print(f"Estado: {imovel[3]}")
                print(f"Renda mensal: {imovel[4]:.2f} €")
                print(f"Duração do contrato: {imovel[5] if imovel[5] is not None else 'Sem contrato'}")
                print(f"Situação: {imovel[6]}")
                print(f"NIF do proprietário: {imovel[7]}")

                # Apresentar os dados da morada
                print(f"Rua: {imovel[8]}")
                print(f"Número da porta: {imovel[9]}")
                print(f"Andar/Fração: {imovel[10] if imovel[10] else 'Não aplicável'}")
                print(f"Código postal: {imovel[11]}")
                print(f"Cidade: {imovel[12]}")

                # Apresentar o nome do proprietário
                print(f"Nome do proprietário: {imovel[13]}")

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao consultar imóveis: {e}")

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()

def consultar_imoveis_disponiveis():
# Estabelecer ligação à base de dados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()
    
    try:
        # Consultar apenas os imoveis com status disponível
        # Para que a informação consultada apareça de forma amigavel, junto dados como nome do proprietário e os detalhes da morada
        cursor.execute("SELECT imoveis.*, proprietarios.nome_completo, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.codigo_postal, moradas.cidade " \
        "FROM imoveis JOIN moradas ON imoveis.id_morada = moradas.id JOIN proprietarios ON imoveis.nif_proprietario = proprietarios.nif WHERE situacao = 'Disponível'")
        disponiveis = cursor.fetchall()
        print("\n--- LISTA DE IMOVEIS DISPONÍVEIS ---")
        
        for imovel in disponiveis:

            numero_apartamento = ""  #Como em algumas moradas o número de apartamento ser vazio, utilizo do recurso de impor uma condição para que os número vazios não apareçam no print
            if imovel[12]:
                numero_apartamento = ", "+imovel[12] 

            print("\n" + "-" * 40)
            print(f"ID: {imovel[0]}")
            print(f"Tipo: {imovel[1]}")
            print(f"Quartos: {imovel[2]}")
            print(f"Estado do imóvel: {imovel[4]}")
            print(f"Valor da renda: {imovel[5]}€")
            print(f"Duração do contrato: {imovel[6]}")
            print(f"Nome do proprietário: {imovel[9]}")
            print(f"Morada: {imovel[10]}, {imovel[11]}{numero_apartamento}, {imovel[14]}") #Não apresento a morada completa para que a informação seja apenas a essencial para consulta
            
    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis disponiveis.", e)
        return
    
    finally:
        if conexao is not None:
            conexao.close()

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
        print("\n--- LISTA DE IMOVEIS ARRENDADOS ---")
        
        for imovel in arrendados:

            numero_apartamento = ""  #Como em algumas moradas o número de apartamento ser vazio, utilizo do recurso de impor uma condição para que os número vazios não apareçam no print
            if imovel[14]:
                numero_apartamento = ", "+imovel[14] 

            print("\n" + "-" * 40)
            print(f"ID: {imovel[0]}")
            print(f"Tipo: {imovel[1]}")
            print(f"Quartos: {imovel[2]}")
            print(f"Estado do imóvel: {imovel[4]}")
            print(f"Valor da renda: {imovel[5]}€")
            print(f"Duração do contrato: {imovel[6]}")
            print(f"Nome do proprietário: {imovel[10]}")
            print(f"Nome do inquilino: {imovel[11]}")
            print(f"Morada: {imovel[12]}, {imovel[13]}{numero_apartamento}, {imovel[16]}") #Não apresento a morada completa para que a informação seja apenas a essencial para consulta
            
    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis arrendados.", e)
        return
    
    finally:
        if conexao is not None:
            conexao.close()

def alterar_dados_imovel ():
    #Adicionar opções de alterações como: Duracao, estado ou renda
    id_imovel_selecionado = selecionar_imovel()

    while True:
        pergunta = [
            inquirer.List('alteracao',
                message="Indique o que deseja editar nesse imovel:",
                choices= ["1.Alterar duração do contrato", "2.Alterar estado do imovel", "3. Alterar valor da renda", "0. Voltar"],
            )
        ]
            
        selecao = inquirer.prompt(pergunta)
        opcao_escolhida = selecao["alteracao"][0]
        if opcao_escolhida == "1":
            #Adicionar validação
            nova_duracao = input("Informe a nova duraçao do contrato: ")
            alteracoes_imovel(id_imovel_selecionado, "duracao", f"'{nova_duracao}'")
        elif opcao_escolhida == "2":
            pergunta_estado = [
                inquirer.List('estado',
                    message="Indique o novo estado do imovel:",
                    choices= ["Novo", "Usado", "Mau Estado", "Remodelado"],
                )
            ]
            
            respo_novo_estado = inquirer.prompt(pergunta_estado)
            novo_estado = f"'{respo_novo_estado["estado"]}'"
            
            alteracoes_imovel(id_imovel_selecionado, "estado", novo_estado)
        elif opcao_escolhida == "3":
            nova_renda = fornecer_validar_renda("Indique o novo valor de renda (€): ")
            
            alteracoes_imovel(id_imovel_selecionado, "renda", nova_renda)
        elif opcao_escolhida == "0":
            break
#Utilizado para permitir o usuario alterar valor da renda, estado do imovel ou duração de contrato. A mesma função é chamada para nas três opções
def alteracoes_imovel(imovel_id, coluna, novo_valor):
    #Estabelecer ligação à base de dados
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
        #
        cursor.execute(f"UPDATE imoveis SET {coluna} = {novo_valor} WHERE id = {int(imovel_id)}")
        conexao.commit()

    except sqlite3.Error as e:
        print("\nErro ao verificar imóveis disponiveis.", e)
        return
    
    finally:
        if conexao is not None:
            conexao.close()


def selecionar_imovel():
    #Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()
    
        escolhas = {} #Usado para criar um dicionário com as opções: id do imóvel, e morada contendo rua, número de porta e apartamento e cidade
    
        try:
            #Listar ID do imóvel e morada
            cursor.execute("SELECT imoveis.id, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.cidade FROM imoveis JOIN moradas ON imoveis.id_morada = moradas.id")
            imoveis = cursor.fetchall()
    
            #Definir opções de escolhas para o usuário
            for imovel in imoveis:
                numero_apartamento = ""
                if imovel[3]:
                    numero_apartamento = ", "+imovel[3] 
                imovelId = imovel[0]
                morada = f"{imovel[1]}, {imovel[2]}{numero_apartamento}, {imovel[4]}"
                escolhas[morada]=imovelId
    
        except sqlite3.Error as e:
            print("\nErro ao verificar imóveis disponiveis.", e)
            return
        
        finally:
            if conexao is not None:
                conexao.close()
    
        pergunta = [
            inquirer.List('imovel',
                message="Indique o imóvel que deseja editar:",
                choices=escolhas.keys(),
            )
        ]
    
        selecao = inquirer.prompt(pergunta)
        morada_escolhida = selecao["imovel"]
        print(f"Imóvel na morada \"{morada_escolhida} selecionado")
        id_imovel_selecionado = escolhas[morada_escolhida]

        return id_imovel_selecionado

def fornecer_validar_renda(messagem):
    # Validar o valor mensal da renda
    while True:
        try:
            # Converter o valor introduzido num número decimal
            # .replace(",", ".") permite introduzir a vírgula como separador decimal
            renda = float(input(messagem).strip().replace(",", "."))

            # Verificar se a renda é positiva e finita, rejeitando valores negativos, zero, infinito e NaN
            if renda <= 0 or not math.isfinite(renda):
                print("A renda deve ser um valor positivo e finito.")
                continue
            return renda

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para a renda.")