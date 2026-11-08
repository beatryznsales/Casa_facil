## questionary ou inquirer
#### Adicionar uma contagem para que sempre que um imovel seja adicionado, o proprietario ganhe +1 no numero de imoveis que este tenha
#### validar todos os inputs pedidos pelo código
### Colocar o os.system() para limpar o terminal
## Editar informações: Permitir editar os dados das tabelas para as 3 entidades
## Adicionar erros LOG

# Para phonenumbers e questionary, deve-se preparar um ficheiro requirements.txt para facilitar a instalação dessas dependências nos computadores externos

import phonenumbers
import datetime
import os
import sqlite3
import math

# Obter o caminho completo da pasta onde o programa está guardado

# __file__ identifica o ficheiro Python em execução
# os.path.abspath() obtém o caminho absoluto desse ficheiro
# os.path.dirname() devolve a pasta onde o ficheiro está guardado
pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa 
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "casa_facil.db")

#####################################     DEFINIÇÃO DAS FUNÇÕES     ############################################################################################################################

## Para os Imóveis: as funções de adicionar, consultar, alterar e atribuir imóveis a inquilinos são definidas abaixo.


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
        num_andar = input("Andar/Fração (se houver, ex.: 2.º Esq., R/C ou 3B): ").strip()

        if num_andar == "":
            break

        elif len(num_andar) > 15:
            print("A identificação do andar/fração não pode ultrapassar 15 caracteres.")

        elif not all(caracter.isalnum() or caracter in " .ºª/-" for caracter in num_andar):
            print("A identificação do andar/fração contém caracteres inválidos.")

        elif not any(caracter.isalnum() for caracter in num_andar):
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


    # Validar o valor mensal da renda
    while True:
        try:
            # Converter o valor introduzido num número decimal
            # .replace(",", ".") permite introduzir a vírgula como separador decimal
            renda = float(input("Valor mensal da renda (€): ").strip().replace(",", "."))

            # Verificar se a renda é positiva e finita, rejeitando valores negativos, zero, infinito e NaN
            if renda <= 0 or not math.isfinite(renda):
                print("A renda deve ser um valor positivo e finito.")
                continue

            # Terminar o ciclo quando a renda passa todas as validações
            break

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para a renda.")


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
        cursor.execute("INSERT INTO moradas(rua, num_porta, num_andar, codigo_postal, cidade) VALUES (?, ?, ?, ?, ?)", (rua, num_porta, num_andar, codigo_postal, cidade))

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
                   moradas.rua, moradas.num_porta, moradas.num_andar,
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




#####################################################################################################################################################

## Para os Proprietários: as funções de adicionar e consultar proprietários são definidas abaixo.

def adicionar_proprietario():
    # Recolher os dados do novo proprietário.
    print("\n--- REGISTAR PROPRIETÁRIO ---")

    # Pedir e validar o nome completo do proprietario
    while True:
        nome = input("Nome completo: ").strip()

        # Verificar que o não pode estar vazio
        if nome == "":
            print("O nome não pode estar vazio.")
            continue

        # Não podem ter caracteres especiais nem números, apenas letras como acentos, espaços, apóstrofes e hifens
        if not all(caracter.isalpha() or caracter in "-' " for caracter in nome):     # .isalpha() verifica se o caracter é uma letra, incluindo letras acentuadas
            print("O nome deve conter apenas letras, espaços e hífens.")
            continue

        # Deve conter pelo menos duas palavras (primeiro e último nome)
        if len(nome.split()) < 2:   # .split() para dividir o nome em palavras. Ignora espaços consecutivos
            print("Introduz o nome completo. O nome deve conter pelo menos duas palavras.")
            continue

        # Todas as palavras são adicionadas com a primeira letra maiuscula na base de dados
        nome = " ".join(nome.split()).title()   # .join() junta o espaço " " com o nome dividido por palavras. Colocar a primeira letra de cada palavra em maiusculas com .title()
        break

    
    # Pedir e validar o NIF do proprietario
    while True:
        nif = input("NIF: ").strip() # o input não pede logo o NIF como inteiro, por ser um identificador e não um numero para fazer calculos (evita a introdução de valores como +123456789)

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if (len(nif) != 9 or not nif.isascii() or not nif.isdigit()):
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            continue

        # Calcular o dígito de controlo do NIF para verificar se o NIF do proprietário é matematicamente válido em Portugal
        # Nota - o NIF (Número de Identificação Fiscal) português tem um dígito de controlo: o nono dígito é calculado 
        # a partir dos oito primeiros dígitos através de um algoritmo módulo 11
        # Referência: https://nif-express.com/pt/pt/guides/portuguese-nif-number-format

        soma = 0  # Criar a variável soma com o valor inicial 0 para que acumule os resultados

        for i in range(8): # Multiplicar os oito primeiros dígitos por 9, 8, 7, 6, 5, 4, 3 e 2, por esta ordem, e somar os resultados
            soma += int(nif[i]) * (9 - i) # forma abreviada de escrever soma = soma + int(nif[i]) * (9 - i)

        resto = soma % 11 # Dividir a soma por 11 e guardar o resto (%), pois algoritmo de validação do NIF português baseia-se no módulo 11

        if resto < 2: # Se o resto for 0 ou 1, o dígito de controlo é 0
            digito_controlo = 0
        else: # Caso contrário, o dígito de controlo é 11 menos o resto
            digito_controlo = 11 - resto

        # Comparar o dígito calculado com o último dígito do NIF introduzido pelo utilizador
        if digito_controlo != int(nif[8]): # fica [8] uma vez que o python começa em 0, ou seja, o nono e último digito fica na posição [8]
            print("NIF inválido. O dígito de controlo não está correto.") 
            continue

        break  # NIF passou a validação (não significa que esteja atribuido) e a leitura do restante codigo avança

    # Pedir e validar a data de nascimento
    while True:
        data_nascimento = input("Data de nascimento (AAAA-MM-DD): ").strip()

        partes_data = data_nascimento.split("-")

        # Verificar se a data respeita o formato AAAA-MM-DD
        if (len(partes_data) != 3 or
            len(partes_data[0]) != 4 or not partes_data[0].isascii() or not partes_data[0].isdigit() or
            len(partes_data[1]) != 2 or not partes_data[1].isascii() or not partes_data[1].isdigit() or
            len(partes_data[2]) != 2 or not partes_data[2].isascii() or not partes_data[2].isdigit()):

            print("Formato de data inválido. Utilize o formato AAAA-MM-DD.")
            continue

        try: 
            # Converter a data de nascimento, introduzida como texto (string), num objeto de data
            # .strptime() converte uma string num objeto datetime e interpreta o texto segundo o formato indicado: %Y (ano), %m (mês) e %d (dia)
            # O método .date() permite obter apenas a data, sem a componente da hora.
            data = datetime.datetime.strptime(data_nascimento, "%Y-%m-%d").date()   

            # Obter a data atual
            hoje = datetime.date.today()   # A classe date permite trabalhar apenas com datas, sem considerar as horas

            # Calcular a idade do proprietário
            idade = hoje.year - data.year

            # Subtrair um ano à idade caso o proprietário ainda não tenha feito anos este ano
            if (hoje.month, hoje.day) < (data.month, data.day):
                idade -= 1

            # Verificar se a data de nascimento não é futura
            if data > hoje:
                print("A data de nascimento não pode ser futura.")
                continue

            # Verificar se o proprietário tem pelo menos 18 anos
            elif idade < 18:
                print("O proprietário deve ter pelo menos 18 anos.")
                continue

            break

        except ValueError: # Se o utilizador introduzir datas inválidas, como 2002-02-30, o método strptime() gera um ValueError que é tratado em try/except
            print("Data inválida. Verifique o dia, o mês e o ano introduzidos.")


    # Pedir e validar o sexo do proprietário.
    while True:
        sexo = input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

        # Verificar se a opção introduzida é válida.
        if sexo not in ["MASCULINO", "FEMININO", "OUTRO", "MASCULINO (M)", "FEMININO (F)", "OUTRO (O)", "MASCULINO(M)", "FEMININO(F)", "OUTRO(O)", "M", "F", "O"]:
            print("Sexo inválido. Utilize Masculino (M), Feminino (F) ou Outro (O).")
            continue

        # Uniformizar os valores para guardar apenas M, F ou O na base de dados.
        if sexo in ["MASCULINO", "MASCULINO (M)", "MASCULINO(M)"]:
            sexo = "M"

        elif sexo in ["FEMININO", "FEMININO (F)", "FEMININO(F)"]:
            sexo = "F"

        elif sexo in ["OUTRO", "OUTRO (O)", "OUTRO(O)"]:
            sexo = "O"

        # Terminar o ciclo após validar e uniformizar o valor.
        break


    # Pedir e validar o contacto telefónico do proprietário  --> ANTENÇÃO: Na BD considerar como contacto telefonico uma vez que não detecta diferença entre telemoveis e números fixos
    while True:
        contacto_telefonico = input("Contacto telefónico (ex.: +351 912345678): ").strip()

        # Verificar se o campo está vazio
        if contacto_telefonico == "":
            print("O contacto telefónico não pode estar vazio.")
            continue

        # Verificar se contém apenas algarismos, espaços e o sinal + inicial
        if not all(caracter.isascii() and caracter.isdigit() or caracter == " " for caracter in contacto_telefonico.lstrip("+")) or contacto_telefonico.count("+") > 1 or ("+" in contacto_telefonico and not contacto_telefonico.startswith("+")):
            print("O contacto telefónico contém caracteres inválidos.")
            continue

        try:
            # Interpretar o número, assumindo Portugal quando não existe indicativo
            numero = phonenumbers.parse(contacto_telefonico, "PT")  # .parse() interpreta o número introduzido e separa as suas componentes: indicativo e número nacional

            # Verificar se o número respeita as regras de numeração do país
            if not phonenumbers.is_valid_number(numero):
                print("Contacto telefónico inválido.")
                continue

            # Guardar o número no formato internacional
            # Formatar o contacto telefónico segundo o padrão internacional E.164, incluindo o indicativo do país e o número nacional, sem espaços.
            contacto_telefonico = phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.E164)
            break

        except phonenumbers.NumberParseException:
            print("Número inválido. Verifique o indicativo e os algarismos introduzidos.")
        

    # Pedir e validar o email do proprietário
    while True:
        email = input("Email: ").strip()

        # Verificar se o email está vazio
        if email == "":
            print("O email não pode estar vazio.")
            continue

        # Verificar se o email contém exatamente um símbolo @
        if email.count("@") != 1:
            print("Email inválido. Deve conter exatamente um símbolo @.")
            continue

        # Separar o email na parte anterior e posterior ao @
        utilizador, dominio = email.split("@")

        # Verificar se ambas as partes estão preenchidas
        if utilizador == "" or dominio == "":
            print("Email inválido. Introduza um endereço completo.")
            continue

        # Verificar se o domínio (parte depois do @) contém apenas letras, números, pontos e hífenes
        if not all(caracter.isascii() and (caracter.isalnum() or caracter in ".-") for caracter in dominio):
            print("Email inválido. O domínio contém caracteres inválidos.")
            continue

        # Verificar se existem espaços no email
        if any(caracter.isspace() for caracter in email):
            print("O email não pode conter espaços.")
            continue

        # Verificar se o domínio contém um ponto
        if "." not in dominio:
            print("Email inválido. O domínio deve conter um ponto.")  # como por exemplo .com, .pt ou .org
            continue

        # Verificar se o email contém pontos consecutivos
        if ".." in email:
            print("Email inválido. Não pode conter pontos consecutivos.")
            continue

        # Separar o domínio em partes para verificar a posição dos hífenes
        partes_dominio = dominio.split(".")

        # Verificar se alguma parte do domínio começa ou termina com um hífen
        if any(parte.startswith("-") or parte.endswith("-") for parte in partes_dominio):
            print("Email inválido. O domínio não pode começar ou terminar com hífenes.")
            continue

        # Verificar se as partes do email não começam nem terminam com pontos
        if utilizador.startswith(".") or utilizador.endswith(".") or dominio.startswith(".") or dominio.endswith("."):
            print("Email inválido. As partes do endereço não podem começar ou terminar com um ponto.")
            continue

        # Verificar se a extensão do domínio contém pelo menos duas letras 
        extensao = dominio.split(".")[-1]  #.split(".") divide o domínio em partes, utilizando o ponto como separador e [-1] obtem o último elemento da lista que fica guardado em extensão

        if len(extensao) < 2 or not extensao.isascii() or not extensao.isalpha():
            print("Email inválido. A extensão do domínio deve conter pelo menos duas letras.")
            continue

        # Terminar o ciclo quando o email passa todas as validações
        break

    num_habitacoes = 0  # O proprietário começa sem imóveis registados
    
    # Inicializar a variável de ligação à base de dados antes do try para verificar em finally se a mesma foi estabelecida
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Inserir os dados na tabela de proprietários
        cursor.execute("INSERT INTO proprietarios (nif, nome_completo, data_nascimento, sexo, contacto_telefonico, email, N_habitacoes_registadas) VALUES (?, ?, ?, ?, ?, ?, ?)", (nif, nome, data_nascimento, sexo, contacto_telefonico, email, num_habitacoes))

        # Guardar as alterações na base de dados
        conexao.commit()
        print("\nProprietário inserido na base de dados com sucesso!")

    except sqlite3.IntegrityError:
        # Tratar erros relacionados com restrições da base de dados
        print("\nErro! Não foi possível registar o proprietário. Verifique se o NIF já existe.")

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()   # .rollback() anula as alterações feitas à base de dados que ainda não foram guardadas em .commit()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao registar proprietário: {e}")

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()


def consultar_proprietarios():
    # Consultar os proprietários registados na base de dados

    # Inicializar a variável de ligação à base de dados antes do try, para verificar no finally se a ligação foi estabelecida
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM proprietarios ORDER BY nome_completo")
        proprietarios = cursor.fetchall()

        if len(proprietarios) == 0:
            print("\nNão existem proprietários registados.")

        else:
            print("\n--- LISTA DE PROPRIETÁRIOS ---")

            for proprietario in proprietarios:
                print("\n" + "-" * 40)
                print(f"NIF: {proprietario[0]}")
                print(f"Nome: {proprietario[1]}")
                print(f"Data de nascimento: {proprietario[2]}")
                print(f"Sexo: {proprietario[3]}")
                print(f"Telemóvel: {proprietario[4]}")
                print(f"Email: {proprietario[5]}")
                print(f"Número de habitações: {proprietario[6]}")

    except sqlite3.Error as e:
        print(f"\nErro ao consultar proprietários: {e}")

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()

#####################################################################################################################################################

## Para os Inquilinos: as funções de adicionar e consultar inquilinos são definidas abaixo.


def adicionar_inquilino():
    # Recolher os dados do novo inquilino.
    print("\n--- REGISTAR INQUILINO ---")

    # Pedir e validar o nome completo do inquilino
    while True:
        nome = input("Nome completo: ").strip()

        # Verificar se o nome está vazio
        if nome == "":
            print("O nome não pode estar vazio.")
            continue

        # Permitir apenas letras, incluindo acentos, espaços, apóstrofos e hífenes
        if not all(caracter.isalpha() or caracter in "-' " for caracter in nome):
            print("O nome deve conter apenas letras, espaços, apóstrofos e hífenes.")
            continue

        # Verificar se o nome contém pelo menos duas palavras
        if len(nome.split()) < 2:
            print("Introduza o nome completo. O nome deve conter pelo menos duas palavras.")
            continue

        # Colocar a primeira letra de cada palavra em maiúscula
        nome = " ".join(nome.split()).title()
        break

    # Pedir e validar o NIF do inquilino
    while True:
        nif = input("NIF: ").strip()

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if (len(nif) != 9 or not nif.isascii() or not nif.isdigit()):
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            continue

        # Calcular o dígito de controlo do NIF 
        soma = 0  

        # Multiplicar os primeiros 8 dígitos pelos pesos de 9 a 2
        for i in range(8):
            soma += int(nif[i]) * (9 - i)

        # Calcular o resto da divisão da soma por 11
        resto = soma % 11

        # Determinar o dígito de controlo
        if resto < 2:
            digito_controlo = 0
        else:
            digito_controlo = 11 - resto

        # Comparar o dígito calculado com o último dígito do NIF
        if digito_controlo != int(nif[8]):
            print("NIF inválido. O dígito de controlo não está correto.")
            continue

        # Terminar o ciclo quando o NIF passa as validações
        break

    # Pedir e validar a data de nascimento
    while True:
        data_nascimento = input("Data de nascimento (AAAA-MM-DD): ").strip()

        partes_data = data_nascimento.split("-")

        # Verificar se a data respeita o formato AAAA-MM-DD
        if (len(partes_data) != 3 or
            len(partes_data[0]) != 4 or not partes_data[0].isascii() or not partes_data[0].isdigit() or
            len(partes_data[1]) != 2 or not partes_data[1].isascii() or not partes_data[1].isdigit() or
            len(partes_data[2]) != 2 or not partes_data[2].isascii() or not partes_data[2].isdigit()):

            print("Formato de data inválido. Utilize o formato AAAA-MM-DD.")
            continue

        try:
            # Converter o texto num objeto datetime e obter apenas a data
            data = datetime.datetime.strptime(data_nascimento, "%Y-%m-%d").date()

            # Obter a data atual
            hoje = datetime.date.today()

            # Calcular a idade do inquilino
            idade = hoje.year - data.year

            # Subtrair um ano se ainda não tiver feito anos este ano
            if (hoje.month, hoje.day) < (data.month, data.day):
                idade -= 1

            # Verificar se a data de nascimento não é futura
            if data > hoje:
                print("A data de nascimento não pode ser futura.")
                continue

            # Verificar se o inquilino tem pelo menos 18 anos
            elif idade < 18:
                print("O inquilino deve ter pelo menos 18 anos.")
                continue

            break

        except ValueError:
            # Tratar datas inexistentes, como 2002-02-30
            print("Data inválida. Verifique o dia, o mês e o ano introduzidos.")

    # Pedir e validar o sexo do inquilino
    while True:
        sexo = input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

        # Verificar se a opção introduzida é válida
        if sexo not in ["MASCULINO", "FEMININO", "OUTRO", "MASCULINO (M)", "FEMININO (F)", "OUTRO (O)", "MASCULINO(M)", "FEMININO(F)", "OUTRO(O)", "M", "F", "O"]:
            print("Sexo inválido. Utilize Masculino (M), Feminino (F) ou Outro (O).")
            continue

        # Uniformizar os valores para guardar apenas M, F ou O
        if sexo in ["MASCULINO", "MASCULINO (M)", "MASCULINO(M)"]:
            sexo = "M"

        elif sexo in ["FEMININO", "FEMININO (F)", "FEMININO(F)"]:
            sexo = "F"

        elif sexo in ["OUTRO", "OUTRO (O)", "OUTRO(O)"]:
            sexo = "O"

        break

    # Pedir e validar o contacto telefónico do inquilino
    # Permite números de telefone fixos e móveis, portugueses e estrangeiros
    while True:
        contacto_telefonico = input("Contacto telefónico (ex.: +351 912345678): ").strip()

        # Verificar se o campo está vazio
        if contacto_telefonico == "":
            print("O contacto telefónico não pode estar vazio.")
            continue

        # Verificar se contém apenas algarismos, espaços e o sinal + inicial
        if not all(caracter.isascii() and caracter.isdigit() or caracter == " " for caracter in contacto_telefonico.lstrip("+")) or contacto_telefonico.count("+") > 1 or ("+" in contacto_telefonico and not contacto_telefonico.startswith("+")):
            print("O contacto telefónico contém caracteres inválidos.")
            continue

        try:
            # Interpretar o número, assumindo Portugal quando não existe indicativo
            numero = phonenumbers.parse(contacto_telefonico, "PT")

            # Verificar se o número respeita as regras de numeração do país
            if not phonenumbers.is_valid_number(numero):
                print("Contacto telefónico inválido.")
                continue

            # Guardar o número no formato internacional E.164, incluindo o indicativo do país, sem espaços
            contacto_telefonico = phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.E164)
            break

        except phonenumbers.NumberParseException:
            print("Número inválido. Verifique o indicativo e os algarismos introduzidos.")

    # Pedir e validar o email do inquilino
    while True:
        email = input("Email: ").strip()

        # Verificar se o email está vazio
        if email == "":
            print("O email não pode estar vazio.")
            continue

        # Verificar se contém exatamente um símbolo @
        if email.count("@") != 1:
            print("Email inválido. Deve conter exatamente um símbolo @.")
            continue

        # Separar o email na parte anterior e posterior ao @
        utilizador, dominio = email.split("@")

        # Verificar se ambas as partes estão preenchidas
        if utilizador == "" or dominio == "":
            print("Email inválido. Introduza um endereço completo.")
            continue

        # Verificar se o domínio contém apenas letras, números, pontos e hífenes
        if not all(caracter.isascii() and (caracter.isalnum() or caracter in ".-") for caracter in dominio):
            print("Email inválido. O domínio contém caracteres inválidos.")
            continue

        # Verificar se existem espaços no email
        if any(caracter.isspace() for caracter in email):
            print("O email não pode conter espaços.")
            continue

        # Verificar se o domínio contém um ponto
        if "." not in dominio:
            print("Email inválido. O domínio deve conter um ponto.")
            continue

        # Verificar se existem pontos consecutivos
        if ".." in email:
            print("Email inválido. Não pode conter pontos consecutivos.")
            continue

        # Separar o domínio em partes para verificar os hífenes
        partes_dominio = dominio.split(".")

        # Verificar se alguma parte começa ou termina com hífen
        if any(parte.startswith("-") or parte.endswith("-") for parte in partes_dominio):
            print("Email inválido. O domínio não pode começar ou terminar com hífenes.")
            continue

        # Verificar se as partes do email começam ou terminam com pontos
        if utilizador.startswith(".") or utilizador.endswith(".") or dominio.startswith(".") or dominio.endswith("."):
            print("Email inválido. As partes do endereço não podem começar ou terminar com um ponto.")
            continue

        # Obter a extensão do domínio (última parte após o ponto)
        extensao = dominio.split(".")[-1]

        # Verificar se a extensão contém pelo menos duas letras
        if len(extensao) < 2 or not extensao.isascii() or not extensao.isalpha():
            print("Email inválido. A extensão do domínio deve conter pelo menos duas letras.")
            continue

        break

    # Pedir e validar o ordenado mensal do inquilino
    while True:
        try:
            # Converter o valor introduzido num número decimal
            ordenado = float(input("Ordenado mensal (€): ").strip().replace(",", ".")) # .replace(",", ".") permite introduzir a vírgula como separador decimal

            # Verificar se o ordenado é finito: se for negativo, infinito ou NaN (Not a Number) é bloqueado
            if ordenado < 0 or not math.isfinite(ordenado): # ordenado pode ser zero ao adicionar o inquilino na base de dados, mas nao o vai permitir arrendar um imovel
                print("O ordenado deve ser um valor não negativo e finito.")
                continue

            # Terminar o ciclo quando o ordenado passa todas as validações
            break

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para o ordenado.")

    
    # Inicializar a variável de ligação à base de dados antes do try para verificar no finally se a ligação foi estabelecida
    conexao = None
    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Inserir os dados na tabela de inquilinos
        cursor.execute("INSERT INTO inquilinos (nif, nome_completo, data_nascimento, sexo, contacto_telefonico, email, ordenado_mensal) VALUES (?, ?, ?, ?, ?, ?, ?)", (nif, nome, data_nascimento, sexo,
              contacto_telefonico, email, ordenado))

        # Guardar as alterações na base de dados
        conexao.commit()
        print("\nInquilino registado com sucesso!")

    except sqlite3.IntegrityError:
        # Tratar erros relacionados com restrições da base de dados
        print("\nErro! Não foi possível registar o inquilino. Verifique se o NIF já existe.")

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao registar inquilino: {e}")

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()


def consultar_inquilinos():
    # Consultar todos os inquilinos registados na base de dados

    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Consultar os inquilinos por ordem alfabética do nome completo
        cursor.execute("SELECT * FROM inquilinos ORDER BY nome_completo")
        inquilinos = cursor.fetchall()

        if len(inquilinos) == 0:
            print("\nNão existem inquilinos registados.")

        else:
            print("\n--- LISTA DE INQUILINOS ---")

            for inquilino in inquilinos:
                print("\n" + "-" * 40)
                print(f"NIF: {inquilino[0]}")
                print(f"Nome: {inquilino[1]}")
                print(f"Data de nascimento: {inquilino[2]}")
                print(f"Sexo: {inquilino[3]}")
                print(f"Telemóvel: {inquilino[4]}")
                print(f"Email: {inquilino[5]}")
                print(f"Ordenado mensal: {inquilino[6]:.2f} €")

    except sqlite3.Error as e:
        print(f"\nErro ao consultar inquilinos: {e}")

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()



########## O menu principal precisa ficar abaixo das funções, para que estas possam ser chamadas quando o utilizador escolher a opção correspondente no menu.
#####################################     MENU PRINCIPAL     ############################################################################################################################

def menu_principal():

    # Menu principal da aplicação - o utilizador fica no menu principal até escolher a opção de sair da aplicação.
    # Permite escolher entre a gestão de imóveis, inquilinos e proprietários, ou sair da aplicação.
    
    #os.system('cls')
    
    while True:
        print("\n" + "=" * 40)
        print("       CASAFÁCIL LDA. - GESTÃO DE IMÓVEIS")
        print("=" * 40)
        print("1. Gestão de Imóveis")
        print("2. Gestão de Inquilinos")
        print("3. Gestão de Proprietários")
        print("0. Sair")
        print("=" * 40)
 
        opcao = input("Escolha uma opção: ").strip()
 
 
        if opcao == "1":
            menu_imoveis()
 
        elif opcao == "2":
            menu_inquilinos()
 
        elif opcao == "3":
            menu_proprietarios()

        elif opcao == "0":
            print("\n A sair da aplicação CasaFácil, LDA. Obrigado(a) por utilizar o nosso software!")
            break

        elif opcao == "":
            print("Não introduziu nenhuma opção. Tente novamente.")
 
        else:
            print("Opção inválida! Escolha um número entre 0 e 3.")

# pesquisar modulo inquirer

def menu_imoveis():
    while True:
        #os.system('cls')  # limpar o terminar
        print("\n" + "=" * 40)
        print("\n--- GESTÃO DE IMÓVEIS ---")
        print("=" * 40)

        print("1. Adicionar imóvel")
        print("2. Consultar todos os imóveis")
        #print("3. Consultar imóveis disponíveis")
        #print("4. Consultar imóveis alugados")
        #print("5. Alterar dados de um imóvel")
        #print("6. Atribuir imóvel a um inquilino")
        #print("7. Encerrar contrato de arrendamento")
        print("0. Voltar ao menu principal")

        print("=" * 40)
 
        opcao = input("Escolha uma opção: ").strip() 
 
        if opcao == "1":
            adicionar_imovel()

        elif opcao == "2":
            consultar_imoveis()

        #elif opcao == "3":
            #consultar_imoveis_disponiveis()

        #elif opcao == "4":
            #consultar_imoveis_alugados()

        #elif opcao == "5":
            #alterar_dados_imovel()

        #elif opcao == "6":
            #atribuir_imovel_inquilino()

        #elif opcao == "7":
            #encerrar_contrato_arrendamento()

        elif opcao == "0":
            break

        elif opcao == "":
            print("Não introduziu nenhuma opção. Tente novamente.")

        else:
            print("Opção inválida!")
 
 
def menu_inquilinos():
    while True:
        print("\n--- GESTÃO DE INQUILINOS ---")
        print("1. Registar inquilino")
        print("2. Consultar todos os inquilinos")
        print("0. Voltar ao menu principal")
 
        opcao = input("Escolha uma opção: ")
 
        if opcao == "1":
            adicionar_inquilino()

        elif opcao == "2":
            consultar_inquilinos()

        elif opcao == "0":
            break

        else:
            print("Opção inválida!")
 
 
def menu_proprietarios():
    while True:
        print("\n--- GESTÃO DE PROPRIETÁRIOS ---")
        print("1. Registar proprietário")
        print("2. Consultar todos os proprietários")
        print("0. Voltar ao menu principal")
 
        opcao = input("Escolha uma opção: ")
 
        if opcao == "1":
            adicionar_proprietario()

        elif opcao == "2":
            consultar_proprietarios()

        elif opcao == "0":
            break

        else:
            print("Opção inválida!")

menu_principal() # de forma a que o menu principal seja chamado quando o programa é executado, iniciando a aplicação.

