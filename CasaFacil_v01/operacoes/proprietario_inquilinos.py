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


#####################################     FUNÇÕES AUXILIARES DE VALIDAÇÃO    ############################################################################################################################
# Estas funções são utilizadas no registo e na edição de proprietários e inquilinos.

def validar_nome(edicao=False):
    # Pedir e validar o nome completo
    while True:
        if edicao:
            nome = input("\nNovo nome completo: ").strip()
        else:
            nome = input("Nome completo: ").strip()

        # Verificar que o nome não pode estar vazio
        if nome == "":
            print("O nome não pode estar vazio.")
            continue

        # Não podem ter caracteres especiais nem números, apenas letras como acentos, espaços, apóstrofes e hífenes
        if not all(caracter.isalpha() or caracter in "-' " for caracter in nome):
            print("O nome deve conter apenas letras, espaços, apóstrofos e hífenes.")
            continue

        # Deve conter pelo menos duas palavras (primeiro e último nome)
        if len(nome.split()) < 2:
            print("Introduza o nome completo. O nome deve conter pelo menos duas palavras.")
            continue

        # Todas as palavras são adicionadas com a primeira letra maiúscula na base de dados
        nome = " ".join(nome.split()).title()
        return nome


def validar_data_nascimento(tipo_pessoa, edicao=False):
    # Pedir e validar a data de nascimento
    while True:
        if edicao:
            data_nascimento = input("\nNova data de nascimento (AAAA-MM-DD): ").strip()
        else:
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
            hoje = datetime.date.today()

            # Calcular a idade do proprietário ou inquilino
            idade = hoje.year - data.year

            # Subtrair um ano à idade caso ainda não tenha feito anos este ano
            if (hoje.month, hoje.day) < (data.month, data.day):
                idade -= 1

            # Verificar se a data de nascimento não é futura
            if data > hoje:
                print("A data de nascimento não pode ser futura.")
                continue

            # Verificar se tem pelo menos 18 anos e não mais que 123 anos
            elif idade < 18:
                print(f"O {tipo_pessoa} deve ter pelo menos 18 anos.")
                continue

            elif idade > 123:
                print("A idade introduzida ultrapassa o limite máximo permitido de 123 anos.")
                continue

            return data_nascimento

        except ValueError: # Se o utilizador introduzir datas inválidas, como 2002-02-30, o método strptime() gera um ValueError que é tratado em try/except
            print("Data inválida. Verifique o dia, o mês e o ano introduzidos.")


def validar_sexo(edicao=False):
    # Pedir e validar o sexo
    while True:
        if edicao:
            sexo = input("\nSexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()
        else:
            sexo = input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

        # Verificar se a opção introduzida é válida
        if sexo not in ["MASCULINO", "FEMININO", "OUTRO", "MASCULINO (M)", "FEMININO (F)", "OUTRO (O)", "MASCULINO(M)", "FEMININO(F)", "OUTRO(O)", "M", "F", "O"]:
            print("Sexo inválido. Utilize Masculino (M), Feminino (F) ou Outro (O).")
            continue

        # Uniformizar os valores para guardar apenas M, F ou O na base de dados
        if sexo in ["MASCULINO", "MASCULINO (M)", "MASCULINO(M)"]:
            sexo = "M"

        elif sexo in ["FEMININO", "FEMININO (F)", "FEMININO(F)"]:
            sexo = "F"

        elif sexo in ["OUTRO", "OUTRO (O)", "OUTRO(O)"]:
            sexo = "O"

        # Terminar o ciclo após validar e uniformizar o valor
        return sexo


def validar_contacto_telefonico(edicao=False):
    # Pedir e validar o contacto telefónico
    # Permite números de telefone fixos e móveis, portugueses e estrangeiros
    while True:
        if edicao:
            contacto_telefonico = input("\nNovo contacto telefónico (ex.: +351 912345678): ").strip()
        else:
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
            return contacto_telefonico

        except phonenumbers.NumberParseException:
            print("Número inválido. Verifique o indicativo e os algarismos introduzidos.")


def validar_email(edicao=False):
    # Pedir e validar o email
    while True:
        if edicao:
            email = input("\nNovo email: ").strip()
        else:
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
        extensao = dominio.split(".")[-1]

        if len(extensao) < 2 or not extensao.isascii() or not extensao.isalpha():
            print("Email inválido. A extensão do domínio deve conter pelo menos duas letras.")
            continue

        # Terminar o ciclo quando o email passa todas as validações
        return email


def validar_nif_novo():
    # Pedir e validar o NIF no registo de um novo proprietário ou inquilino
    while True:
        nif = input("NIF: ").strip()  # Identificador guardado inicialmente como texto

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if len(nif) != 9 or not nif.isascii() or not nif.isdigit():
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            continue

        # Calcular o dígito de controlo do NIF para verificar se o NIF é matematicamente válido em Portugal
        # Nota - o NIF português tem um dígito de controlo calculado a partir dos oito primeiros dígitos (módulo 11)
        soma = 0
        for i in range(8):
            soma += int(nif[i]) * (9 - i)

        resto = soma % 11
        if resto < 2:
            digito_controlo = 0
        else:
            digito_controlo = 11 - resto

        # Comparar o dígito calculado com o último dígito do NIF
        if digito_controlo != int(nif[8]):
            print("NIF inválido. O dígito de controlo não está correto.")
            continue

        return nif


def validar_ordenado(edicao=False):
    # Pedir e validar o ordenado mensal do inquilino
    while True:
        try:
            if edicao:
                ordenado = float(input("\nNovo ordenado mensal (€): ").strip().replace(",", "."))
            else:
                ordenado = float(input("Ordenado mensal (€): ").strip().replace(",", "."))

            # Verificar se o ordenado é finito: se for negativo, infinito ou NaN (Not a Number) é bloqueado
            if ordenado < 0 or not math.isfinite(ordenado):  # Pode ser zero no registo, mas não permite arrendar um imóvel
                print("O ordenado mensal deve ser um valor não negativo e finito.")
                continue

            return ordenado

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para o ordenado.")


def procurar_nif_existente(cursor, tabela, tipo_pessoa, operacao):
    # Pedir o NIF até existir na base de dados ou o utilizador cancelar
    # Não é necessário repetir o dígito de controlo: foi validado no registo
    while True:
        nif = input(f"NIF do {tipo_pessoa} (introduza apenas 0 para cancelar): ").strip()

        if nif == "0":
            print(f"\n{operacao} cancelada.")
            return None

        # Verificar se o NIF contém exatamente 9 dígitos
        if len(nif) != 9 or not nif.isascii() or not nif.isdigit():
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            continue

        # Confirmar a existência na base de dados
        cursor.execute(f"SELECT nome_completo FROM {tabela} WHERE nif = ?", (int(nif),))
        pessoa = cursor.fetchone()

        if pessoa is None:
            print(f"\nNão existe nenhum {tipo_pessoa} registado com esse NIF.")
            continue

        return nif, pessoa[0]



#####################################     FUNÇÕES PRINCIPAIS DE VALIDAÇÃO    ############################################################################################################################

## Para os Proprietários: as funções de adicionar, consultar, editar e eliminar proprietários são definidas abaixo.

def adicionar_proprietario():
    # Recolher os dados do novo proprietário.
    print("\n--- REGISTAR PROPRIETÁRIO ---")

    # Pedir e validar o nome completo
    nome = validar_nome()

    # Pedir e validar o NIF
    nif = validar_nif_novo()

    # Pedir e validar a data de nascimento
    data_nascimento = validar_data_nascimento("proprietário")

    # Pedir e validar o sexo
    sexo = validar_sexo()

    # Pedir e validar o contacto telefónico
    contacto_telefonico = validar_contacto_telefonico()

    # Pedir e validar o email
    email = validar_email()

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
        
        input("\nPressione Enter para voltar ao menu...")


def editar_proprietarios():
    print("\n--- EDITAR DADOS DO PROPRIETÁRIO ---")

    # Inicializar a variável de ligação à base de dados
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Pedir e verificar o NIF do proprietário, repetindo a pergunta se não existir
        resultado = procurar_nif_existente(cursor, "proprietarios", "proprietário", "Edição")

        if resultado is None:
            return

        nif, nome = resultado

        print(f"\nProprietário encontrado: {nome}")
        print(f"NIF: {nif}")

        # Apresentar os campos que podem ser alterados
        menu = [inquirer.Checkbox("campos",
                message="Selecione os campos que pretende alterar",
                choices=["1. Nome completo", "2. Data de nascimento", "3. Sexo", "4. Contacto telefónico", "5. Email"])]

        answers = inquirer.prompt(menu)

        # Cancelar a edição se o utilizador interromper o menu
        if answers is None:
            print("\nEdição cancelada.")
            return

        campos_selecionados = answers["campos"]

        # Verificar se foi selecionado pelo menos um campo
        if len(campos_selecionados) == 0:
            print("\nNão selecionou nenhum campo para alterar.")
            return

        novos_valores = {} # Guardar os novos valores num dicionário

        # Percorrer os campos selecionados e pedir os novos valores
        for campo in campos_selecionados:

            # Editar o nome completo
            if campo == "1. Nome completo":
                novos_valores["nome_completo"] = validar_nome(edicao=True)

            # Editar a data nascimento
            elif campo == "2. Data de nascimento":
                novos_valores["data_nascimento"] = validar_data_nascimento("proprietário", edicao=True)

            # Editar o sexo
            elif campo == "3. Sexo":
                novos_valores["sexo"] = validar_sexo(edicao=True)

            # Editar o contacto telefonico
            elif campo == "4. Contacto telefónico":
                novos_valores["contacto_telefonico"] = validar_contacto_telefonico(edicao=True)

            # Editar o email
            elif campo == "5. Email":
                novos_valores["email"] = validar_email(edicao=True)

        # Apresentar um resumo dos dados que vão ser alterados
        print("\n--- CONFIRMAR ALTERAÇÕES ---")
        print(f"NIF do proprietário: {nif}")

        for coluna, valor in novos_valores.items():
            print(f"{coluna}: {valor}")

        # Pedir confirmação antes de atualizar a base de dados
        confirmacao = [inquirer.List("confirmar",
            message="Confirma que pretende guardar todas estas alterações?",
            choices=["Sim", "Não"],
            default="Não")]  

        resposta = inquirer.prompt(confirmacao)

        # Cancelar sem guardar qualquer alteração
        if resposta is None or resposta["confirmar"] == "Não":
            print("\nEdição cancelada. Nenhum dado foi alterado.")
            return

        # Preparar os campos a atualizar na instrução SQL
        atualizacoes = []

        for coluna in novos_valores:
            atualizacoes.append(f"{coluna} = ?")

        # Juntar os campos separados por vírgulas
        campos_sql = ", ".join(atualizacoes)

        # Obter os novos valores pela mesma ordem dos campos
        valores_sql = list(novos_valores.values())

        # Acrescentar o NIF para identificar o proprietário
        valores_sql.append(int(nif))

        # Atualizar todos os campos selecionados numa única instrução SQL
        cursor.execute(
            f"UPDATE proprietarios SET {campos_sql} WHERE nif = ?",
            valores_sql
        )

        # Guardar todas as alterações na base de dados
        conexao.commit()

        print("\nDados do proprietário atualizados com sucesso!")

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao editar proprietário: {e}")

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()
             # Aguardar que o utilizador pressione Enter antes de regressar ao menu



def eliminar_proprietarios():
    print("\n--- ELIMINAR PROPRIETÁRIO ---")

    # Inicializar a variável de ligação à base de dados
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)

        # Ativar a verificação das chaves estrangeiras
        conexao.execute("PRAGMA foreign_keys = ON")

        cursor = conexao.cursor()

        # Pedir e verificar o NIF do proprietário, repetindo a pergunta se não existir
        resultado = procurar_nif_existente(cursor, "proprietarios", "proprietário", "Eliminação")

        if resultado is None:
            return

        nif, nome = resultado

        print(f"\nProprietário encontrado: {nome}")
        print(f"NIF: {nif}")

        # Verificar se o proprietário tem imóveis associados
        cursor.execute("SELECT COUNT(*) FROM imoveis WHERE nif_proprietario = ?", (int(nif),))

        numero_imoveis = cursor.fetchone()[0]

        # Impedir a eliminação se existirem imóveis associados
        if numero_imoveis > 0:
            print("\nNão é possível eliminar este proprietário.")

            if numero_imoveis == 1:
                print("Existe 1 imóvel associado a este proprietário.")
            else:
                print(f"Existem {numero_imoveis} imóveis associados a este proprietário.")

            print("É necessário eliminar primeiro os imóveis associados.")
            return

        # Pedir confirmação antes de eliminar o proprietário
        confirmacao = [inquirer.List("confirmar",
                message="Confirma que pretende eliminar este proprietário?",
                choices=["Sim", "Não"],
                default="Não")
        ]

        resposta = inquirer.prompt(confirmacao)

        # Cancelar a operação se o utilizador selecionar Não ou interromper o menu
        if resposta is None or resposta["confirmar"] == "Não":
            print("\nEliminação cancelada. Nenhum dado foi eliminado.")
            return

        # Eliminar o proprietário identificado pelo NIF
        cursor.execute("DELETE FROM proprietarios WHERE nif = ?", (int(nif),))

        # Guardar a alteração na base de dados
        conexao.commit()

        print("\nProprietário eliminado com sucesso!")

    except sqlite3.IntegrityError:
        # Impedir a eliminação caso existam outras relações protegidas
        print("\nNão foi possível eliminar o proprietário.")
        print("Existem registos associados que impedem a eliminação.")

        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao eliminar proprietário: {e}")

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()

#####################################################################################################################################################

## Para os Inquilinos: as funções de adicionar, consultar, editar e eliminar inquilinos são definidas abaixo.


def adicionar_inquilino():
    # Recolher os dados do novo inquilino.
    print("\n--- REGISTAR INQUILINO ---")

    # Pedir e validar o nome completo
    nome = validar_nome()

    # Pedir e validar o NIF
    nif = validar_nif_novo()

    # Pedir e validar a data de nascimento
    data_nascimento = validar_data_nascimento("inquilino")

    # Pedir e validar o sexo
    sexo = validar_sexo()

    # Pedir e validar o contacto telefónico
    contacto_telefonico = validar_contacto_telefonico()

    # Pedir e validar o email
    email = validar_email()

    # Pedir e validar o ordenado mensal
    ordenado = validar_ordenado()

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

        input("\nPressione Enter para voltar ao menu...")


def editar_inquilinos():
    print("\n--- EDITAR DADOS DO INQUILINO ---")

    # Inicializar a variável de ligação à base de dados
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Pedir e verificar o NIF do inquilino, repetindo a pergunta se não existir
        resultado = procurar_nif_existente(cursor, "inquilinos", "inquilino", "Edição")

        if resultado is None:
            return

        nif, nome = resultado

        print(f"\nInquilino encontrado: {nome}")
        print(f"NIF: {nif}")

        # Apresentar os campos que podem ser alterados
        menu = [inquirer.Checkbox("campos",
                message="Selecione os campos que pretende alterar",
                choices=["1. Nome completo", "2. Data de nascimento", "3. Sexo", "4. Contacto telefónico", "5. Email", "6. Ordenado mensal"])
        ]

        answers = inquirer.prompt(menu)

        # Cancelar a edição se o utilizador interromper o menu
        if answers is None:
            print("\nEdição cancelada.")
            return

        campos_selecionados = answers["campos"]

        # Verificar se foi selecionado pelo menos um campo
        if len(campos_selecionados) == 0:
            print("\nNão selecionou nenhum campo para alterar.")
            return

        novos_valores = {}  # Guardar os novos valores num dicionário

        # Percorrer os campos selecionados e pedir os novos valores
        for campo in campos_selecionados:

            # Editar o nome completo
            if campo == "1. Nome completo":
                novos_valores["nome_completo"] = validar_nome(edicao=True)

            # Editar a data nascimento
            elif campo == "2. Data de nascimento":
                novos_valores["data_nascimento"] = validar_data_nascimento("inquilino", edicao=True)

            # Editar o sexo
            elif campo == "3. Sexo":
                novos_valores["sexo"] = validar_sexo(edicao=True)

            # Editar o contacto telefonico
            elif campo == "4. Contacto telefónico":
                novos_valores["contacto_telefonico"] = validar_contacto_telefonico(edicao=True)

            # Editar o email
            elif campo == "5. Email":
                novos_valores["email"] = validar_email(edicao=True)

            # Editar o ordenado mensal
            elif campo == "6. Ordenado mensal":
                novos_valores["ordenado_mensal"] = validar_ordenado(edicao=True)

        # Apresentar um resumo dos dados que vão ser alterados
        print("\n--- CONFIRMAR ALTERAÇÕES ---")
        print(f"NIF do inquilino: {nif}")

        for coluna, valor in novos_valores.items():
            if coluna == "ordenado_mensal":
                print(f"{coluna}: {valor:.2f} €")
            else:
                print(f"{coluna}: {valor}")

        # Pedir confirmação antes de atualizar a base de dados
        confirmacao = [inquirer.List("confirmar",
                message="Confirma que pretende guardar todas estas alterações?",
                choices=["Sim", "Não"],
                default="Não")
        ]

        resposta = inquirer.prompt(confirmacao)

        # Cancelar sem guardar qualquer alteração
        if resposta is None or resposta["confirmar"] == "Não":
            print("\nEdição cancelada. Nenhum dado foi alterado.")
            return

        # Preparar os campos a atualizar na instrução SQL
        atualizacoes = []

        for coluna in novos_valores:
            atualizacoes.append(f"{coluna} = ?")

        # Juntar os campos separados por vírgulas
        campos_sql = ", ".join(atualizacoes)

        # Obter os novos valores pela mesma ordem dos campos
        valores_sql = list(novos_valores.values())

        # Acrescentar o NIF para identificar o inquilino
        valores_sql.append(int(nif))

        # Atualizar todos os campos selecionados numa única instrução SQL
        cursor.execute(
            f"UPDATE inquilinos SET {campos_sql} WHERE nif = ?",
            valores_sql
        )

        # Guardar todas as alterações na base de dados
        conexao.commit()

        print("\nDados do inquilino atualizados com sucesso!")

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao editar inquilino: {e}")

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()


def eliminar_inquilinos():
    print("\n--- ELIMINAR INQUILINO ---")

    # Inicializar a variável de ligação à base de dados
    conexao = None

    try:
        # Estabelecer ligação à base de dados
        conexao = sqlite3.connect(base_de_dados)

        # Ativar a verificação das chaves estrangeiras
        conexao.execute("PRAGMA foreign_keys = ON")

        cursor = conexao.cursor()

        # Pedir e verificar o NIF do inquilino, repetindo a pergunta se não existir
        resultado = procurar_nif_existente(cursor, "inquilinos", "inquilino", "Eliminação")

        if resultado is None:
            return

        nif, nome = resultado

        print(f"\nInquilino encontrado: {nome}")
        print(f"NIF: {nif}")

        # Verificar se o inquilino tem imóveis associados
        cursor.execute(
            "SELECT COUNT(*) FROM imoveis WHERE nif_inquilino = ?",
            (int(nif),)
        )

        numero_imoveis = cursor.fetchone()[0]

        # Impedir a eliminação se existirem imóveis associados
        if numero_imoveis > 0:
            print("\nNão é possível eliminar este inquilino.")

            if numero_imoveis == 1:
                print("Existe 1 imóvel associado a este inquilino.")
            else:
                print(f"Existem {numero_imoveis} imóveis associados a este inquilino.")

            print("É necessário encerrar primeiro os arrendamentos associados.")
            return

        # Pedir confirmação antes de eliminar o inquilino
        confirmacao = [inquirer.List("confirmar",
                message="Confirma que pretende eliminar este inquilino?",
                choices=["Sim", "Não"],
                default="Não")
        ]

        resposta = inquirer.prompt(confirmacao)

        # Cancelar a operação se o utilizador selecionar Não ou interromper o menu
        if resposta is None or resposta["confirmar"] == "Não":
            print("\nEliminação cancelada. Nenhum dado foi eliminado.")
            return

        # Eliminar o inquilino identificado pelo NIF
        cursor.execute("DELETE FROM inquilinos WHERE nif = ?", (int(nif),))

        # Guardar a alteração na base de dados
        conexao.commit()

        print("\nInquilino eliminado com sucesso!")

    except sqlite3.IntegrityError:
        # Impedir a eliminação caso existam relações protegidas
        print("\nNão foi possível eliminar o inquilino.")
        print("Existem registos associados que impedem a eliminação.")

        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao eliminar inquilino: {e}")

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()
