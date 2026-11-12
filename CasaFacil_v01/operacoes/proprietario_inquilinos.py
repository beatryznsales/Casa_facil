import phonenumbers
import datetime
import os
import sqlite3
import math
import inquirer
from . import Logs_erros
from .tabelas import mostrar_tabela 
from .cancelamentos import pedir_input, OperacaoCancelada, informar_cancelamento   # Permitir ao utilizador escrever "voltar", nos campos que pedem input, para cancelar a operação e regressar ao menu anterior

pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa 
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "../casa_facil.db") #caminho da base de dados
pathlogs = os.path.join(pasta_programa, "../logs_erros.txt") #caminho dos LOGs de erro


#####################################     FUNÇÕES AUXILIARES DE VALIDAÇÃO    ############################################################################################################################
# Estas funções são utilizadas no registo e na edição de proprietários e inquilinos.

def validar_nome(edicao=False):
    # Pedir e validar o nome completo
    while True:
        if edicao:
            nome = pedir_input("\nNovo nome completo: ").strip()
        else:
            nome = pedir_input("Nome completo: ").strip()

        # Verificar que o nome não pode estar vazio
        if nome == "":
            print("O nome não pode estar vazio.")
            Logs_erros.logs_erro(101,'Nome Invalido', 'O nome esta vazio', pathlogs)
            continue

        # Não podem ter caracteres especiais nem números, apenas letras como acentos, espaços, apóstrofes e hífenes
        if not all(caracter.isalpha() or caracter in "-' " for caracter in nome):
            print("O nome deve conter apenas letras, espaços, apóstrofos e hífenes.")
            Logs_erros.logs_erro(102,'Nome Invalido', 'O nome so pode conter letras, espacos, apostrofos e hifens', pathlogs)
            continue

        # Deve conter pelo menos duas palavras (primeiro e último nome)
        if len(nome.split()) < 2:
            print("Introduza o nome completo. O nome deve conter pelo menos duas palavras.")
            Logs_erros.logs_erro(103,'Nome Invalido', 'O nome deve conter pelo menos duas palavras', pathlogs)
            continue

        # Todas as palavras são adicionadas com a primeira letra maiúscula na base de dados
        nome = " ".join(nome.split()).title()
        return nome


def validar_data_nascimento(tipo_pessoa, edicao=False):
    # Pedir e validar a data de nascimento
    while True:
        if edicao:
            data_nascimento = pedir_input("\nNova data de nascimento (AAAA-MM-DD): ").strip()
        else:
            data_nascimento = pedir_input("Data de nascimento (AAAA-MM-DD): ").strip()

        partes_data = data_nascimento.split("-")

        # Verificar se a data respeita o formato AAAA-MM-DD
        if (len(partes_data) != 3 or
            len(partes_data[0]) != 4 or not partes_data[0].isascii() or not partes_data[0].isdigit() or
            len(partes_data[1]) != 2 or not partes_data[1].isascii() or not partes_data[1].isdigit() or
            len(partes_data[2]) != 2 or not partes_data[2].isascii() or not partes_data[2].isdigit()):

            print("Formato de data invalido. Utilize o formato AAAA-MM-DD.")
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
                Logs_erros.logs_erro(401,'Data Invalida', 'Nao se aceita uma data futura como data de nascimento', pathlogs)
                continue

            # Verificar se tem pelo menos 18 anos e não mais que 123 anos
            elif idade < 18:
                print(f"O {tipo_pessoa} deve ter pelo menos 18 anos.")
                Logs_erros.logs_erro(402,'Data Invalida', 'Idade inferior a 18 anos', pathlogs)
                continue

            elif idade > 123:
                print("A idade introduzida ultrapassa o limite máximo permitido de 123 anos.")
                continue

            return data_nascimento

        except ValueError: # Se o utilizador introduzir datas inválidas, como 2002-02-30, o método strptime() gera um ValueError que é tratado em try/except
            print("Data inválida. Verifique o dia, o mês e o ano introduzidos.")
            Logs_erros.logs_erro(403,'Data Invalida', 'A data nao foi colocada corretamente, ou tem letras ou nao esta completa', pathlogs)


def validar_sexo(edicao=False):
    # Pedir e validar o sexo
    while True:
        if edicao:
            sexo = pedir_input("\nSexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()
        else:
            sexo = pedir_input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

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
            contacto_telefonico = pedir_input("\nNovo contacto telefónico (ex.: +351 912345678): ").strip()
        else:
            contacto_telefonico = pedir_input("Contacto telefónico (ex.: +351 912345678): ").strip()

        # Verificar se o campo está vazio
        if contacto_telefonico == "":
            print("O contacto telefónico não pode estar vazio.")
            Logs_erros.logs_erro(301,'Numero invalido', 'Nao escreveu o numero do contacto', pathlogs)
            continue

        # Verificar se contém apenas algarismos, espaços e o sinal + inicial
        if not all(caracter.isascii() and caracter.isdigit() or caracter == " " for caracter in contacto_telefonico.lstrip("+")) or contacto_telefonico.count("+") > 1 or ("+" in contacto_telefonico and not contacto_telefonico.startswith("+")):
            print("O contacto telefónico contém caracteres inválidos.")
            Logs_erros.logs_erro(302,'Numero invalido', 'O contacto contem caracteres invalidos', pathlogs)
            continue

        try:
            # Interpretar o número, assumindo Portugal quando não existe indicativo
            numero = phonenumbers.parse(contacto_telefonico, "PT")

            # Verificar se o número respeita as regras de numeração do país
            if not phonenumbers.is_valid_number(numero):
                print("Contacto telefónico inválido.")
                Logs_erros.logs_erro(303,'Numero invalido', 'O contacto nao existe', pathlogs)
                continue

            # Guardar o número no formato internacional E.164, incluindo o indicativo do país, sem espaços
            contacto_telefonico = phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.E164)
            return contacto_telefonico

        except phonenumbers.NumberParseException:
            print("Número inválido. Verifique o indicativo e os algarismos introduzidos.")
            Logs_erros.logs_erro(304,'Numero invalido', 'O numero nao foi colocado corretamente, ver indicativo ou algarismos', pathlogs)


def validar_email(edicao=False):
    # Pedir e validar o email
    while True:
        if edicao:
            email = pedir_input("\nNovo email: ").strip()
        else:
            email = pedir_input("Email: ").strip()

        # Verificar se o email está vazio
        if email == "":
            print("O email não pode estar vazio.")
            Logs_erros.logs_erro(201,'Email invalido', 'O campo email esta vazio', pathlogs)
            continue

        # Verificar se o email contém exatamente um símbolo @
        if email.count("@") != 1:
            print("Email inválido. Deve conter exatamente um símbolo @.")
            Logs_erros.logs_erro(202,'Email invalido', 'Deve conter exatamente um simbolo @.', pathlogs)
            continue

        # Separar o email na parte anterior e posterior ao @
        utilizador, dominio = email.split("@")

        # Verificar se ambas as partes estão preenchidas
        if utilizador == "" or dominio == "":
            print("Email inválido. Introduza um endereço completo.")
            Logs_erros.logs_erro(203,'Email invalido', 'Endereço de email incompleto', pathlogs)
            continue

        # Verificar se o domínio (parte depois do @) contém apenas letras, números, pontos e hífenes
        if not all(caracter.isascii() and (caracter.isalnum() or caracter in ".-") for caracter in dominio):
            print("Email inválido. O domínio contém caracteres inválidos.")
            Logs_erros.logs_erro(204,'Email invalido', 'O campo email contem caracteres invalidos', pathlogs)
            continue

        # Verificar se existem espaços no email
        if any(caracter.isspace() for caracter in email):
            print("O email não pode conter espaços.")
            Logs_erros.logs_erro(205,'Email invalido', 'O campo email contem espaços', pathlogs)
            continue

        # Verificar se o domínio contém um ponto
        if "." not in dominio:
            print("Email inválido. O domínio deve conter um ponto.")  # como por exemplo .com, .pt ou .org
            Logs_erros.logs_erro(206,'Email invalido', 'O campo email nao tem o dominio correto', pathlogs)
            continue

        # Verificar se o email contém pontos consecutivos
        if ".." in email:
            print("Email inválido. Não pode conter pontos consecutivos.")
            Logs_erros.logs_erro(207,'Email invalido', 'Pontos consecutivos detetados no email', pathlogs)
            continue

        # Separar o domínio em partes para verificar a posição dos hífenes
        partes_dominio = dominio.split(".")

        # Verificar se alguma parte do domínio começa ou termina com um hífen
        if any(parte.startswith("-") or parte.endswith("-") for parte in partes_dominio):
            print("Email inválido. O domínio não pode começar ou terminar com hífenes.")
            Logs_erros.logs_erro(208,'Email invalido', 'O dominio do email esta a comecar ou terminar com hifenes', pathlogs)
            continue

        # Verificar se as partes do email não começam nem terminam com pontos
        if utilizador.startswith(".") or utilizador.endswith(".") or dominio.startswith(".") or dominio.endswith("."):
            print("Email inválido. As partes do endereço não podem começar ou terminar com um ponto.")
            Logs_erros.logs_erro(209,'Email invalido', 'As partes do endereço estao a começar ou terminar com um ponto', pathlogs)
            continue

        # Verificar se a extensão do domínio contém pelo menos duas letras
        extensao = dominio.split(".")[-1]

        if len(extensao) < 2 or not extensao.isascii() or not extensao.isalpha():
            print("Email inválido. A extensão do domínio deve conter pelo menos duas letras.")
            Logs_erros.logs_erro(210,'Email invalido', 'Extensao do dominio do email incorreta', pathlogs)
            continue

        # Terminar o ciclo quando o email passa todas as validações
        return email


def validar_nif_novo():
    # Pedir e validar o NIF no registo de um novo proprietário ou inquilino
    while True:
        nif = pedir_input("NIF: ").strip()  # Identificador guardado inicialmente como texto

        # Verificar se o NIF contém exatamente 9 dígitos de 0 a 9
        if len(nif) != 9 or not nif.isascii() or not nif.isdigit():
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            Logs_erros.logs_erro(501,'NIF invalido', 'Numero de caracteres diferente de 9', pathlogs)
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
            Logs_erros.logs_erro(502,'NIF invalido', 'Digito de controlo incorreto', pathlogs)
            continue

        return nif


def validar_ordenado(edicao=False):
    # Pedir e validar o ordenado mensal do inquilino
    while True:
        try:
            if edicao:
                ordenado = float(pedir_input("\nNovo ordenado mensal (€): ").strip().replace(",", "."))
            else:
                ordenado = float(pedir_input("Ordenado mensal (€): ").strip().replace(",", "."))

            # Verificar se o ordenado é finito: se for negativo, infinito ou NaN (Not a Number) é bloqueado
            if ordenado < 0 or not math.isfinite(ordenado):  # Pode ser zero no registo, mas não permite arrendar um imóvel
                print("O ordenado mensal deve ser um valor não negativo e finito.")
                Logs_erros.logs_erro(601,'Ordenado invalido', 'Valor inserido negativo ou não finito', pathlogs)
                continue

            return ordenado

        except ValueError:
            # Tratar entradas que não podem ser convertidas para números
            print("Introduza um valor numérico válido para o ordenado.")
            Logs_erros.logs_erro(602,'Ordenado invalido', 'O valor introduzido contem letras', pathlogs)


def procurar_nif_existente(cursor, tabela, tipo_pessoa, operacao):
    # Pedir o NIF até existir na base de dados ou o utilizador cancelar
    # Não é necessário repetir o dígito de controlo: foi validado no registo
    while True:
        nif = pedir_input(f"NIF do {tipo_pessoa} (introduza apenas 0 para cancelar): ").strip()

        if nif == "0":
            print(f"\n{operacao} cancelada.")
            Logs_erros.logs_erro(701,'Operacao cancelada', 'Utilizador cancelou operacao', pathlogs)
            return None

        # Verificar se o NIF contém exatamente 9 dígitos
        if len(nif) != 9 or not nif.isascii() or not nif.isdigit():
            print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
            Logs_erros.logs_erro(702,'Operacao invalida', 'NIF com numero diferente de 9 caracteres', pathlogs)
            continue

        # Confirmar a existência na base de dados
        cursor.execute(f"SELECT nome_completo FROM {tabela} WHERE nif = ?", (int(nif),))
        pessoa = cursor.fetchone()

        if pessoa is None:
            print(f"\nNão existe nenhum {tipo_pessoa} registado com esse NIF.")
            Logs_erros.logs_erro(703,'Operacao invalida', 'Falta de correspondencia de pessoa com o NIF', pathlogs)
            continue

        return nif, pessoa[0]



#####################################     FUNÇÕES PRINCIPAIS DE VALIDAÇÃO    ############################################################################################################################

## Para os Proprietários: as funções de adicionar, consultar, editar e eliminar proprietários são definidas abaixo.

def adicionar_proprietario():
    # Recolher os dados do novo proprietário.
    print("\n--- REGISTAR PROPRIETÁRIO ---")
    print("Escreva 'voltar' em qualquer campo para cancelar a operação.")

    try:
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
    
    except OperacaoCancelada:
        informar_cancelamento()
        return

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
        Logs_erros.logs_erro(704,'Operacao invalida', 'NIF existente na base de dados', pathlogs)

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()   # .rollback() anula as alterações feitas à base de dados que ainda não foram guardadas em .commit()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao registar proprietário: {e}")
        Logs_erros.logs_erro(705,'Operacao invalida', 'Erro ao registar proprietario', pathlogs)

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
            mostrar_tabela(
                "PROPRIETÁRIOS REGISTADOS",
                ["NIF", "Nome", "Data de nascimento", "Sexo", "Contacto telefónico", "Email", "N.º de habitações"],
                proprietarios
            )

    except sqlite3.Error as e:
        print(f"\nErro ao consultar proprietários: {e}")
        Logs_erros.logs_erro(801,'Consulta invalida', 'Erro de consulta de proprietario', pathlogs)

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()
        
        input("\nPressione Enter para voltar ao menu...")


def editar_proprietarios():
    print("\n--- EDITAR DADOS DO PROPRIETÁRIO ---")
    print("Escreva 'voltar' para cancelar a operação.")

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

        # Guardar os novos valores num dicionário. Ainda não são escritos na base de dados.
        novos_valores = {}

        # O inquirer.List devolve apenas uma opção de cada vez.
        # Repetir o menu permite selecionar vários campos antes de confirmar a edição.
        while True:
            menu = [inquirer.List("campos",
                    message="Selecione um campo para alterar ou termine a seleção",
                    choices=["1. Nome completo", "2. Data de nascimento", "3. Sexo", "4. Contacto telefónico", "5. Email", "0. Terminar seleção"])
            ]

            answers = inquirer.prompt(menu)

            # Cancelar a edição se o utilizador interromper o menu
            if answers is None:
                print("\nEdição cancelada. Nenhum dado foi alterado.")
                return

            campo = answers["campos"]  # O List devolve uma string, não uma lista.

            if campo == "0. Terminar seleção":
                break

            if campo == "1. Nome completo":
                novos_valores["nome_completo"] = validar_nome(edicao=True)

            elif campo == "2. Data de nascimento":
                novos_valores["data_nascimento"] = validar_data_nascimento("proprietário", edicao=True)

            elif campo == "3. Sexo":
                novos_valores["sexo"] = validar_sexo(edicao=True)

            elif campo == "4. Contacto telefónico":
                novos_valores["contacto_telefonico"] = validar_contacto_telefonico(edicao=True)

            elif campo == "5. Email":
                novos_valores["email"] = validar_email(edicao=True)

        # Não tentar fazer UPDATE se nenhum campo tiver sido alterado.
        if len(novos_valores) == 0:
            print("\nNão selecionou nenhum campo para alterar.")
            return

        # Apresentar um resumo dos dados que vão ser alterados
        print("\n--- CONFIRMAR ALTERAÇÕES ---\n")
        print(f"NIF do proprietário: {nif}")

        for coluna, valor in novos_valores.items():
            print(f"{coluna}: {valor}")

        print()  # Adicionar uma linha em branco antes da confirmação.

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

    except OperacaoCancelada:
        informar_cancelamento()
        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao editar proprietário: {e}")
        Logs_erros.logs_erro(802,'Erro de edicao bd', 'Erro de edicao de proprietario na bd', pathlogs)

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()
             # Aguardar que o utilizador pressione Enter antes de regressar ao menu



def eliminar_proprietarios():
    print("\n--- ELIMINAR PROPRIETÁRIO ---")
    print("Escreva 'voltar' para cancelar a operação.")

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
            Logs_erros.logs_erro(803,'Operação anulada', 'Operacoes de eliminacao de proprietarios com imoveis existentes sao impossiveis', pathlogs)

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

    except OperacaoCancelada:
        informar_cancelamento()
        if conexao is not None:
            conexao.rollback()

    except sqlite3.IntegrityError:
        # Impedir a eliminação caso existam outras relações protegidas
        print("\nNão foi possível eliminar o proprietário.")
        print("Existem registos associados que impedem a eliminação.")
        Logs_erros.logs_erro(804,'Operação anulada', 'Existem registos em conflito com esta operacao', pathlogs)

        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao eliminar proprietário: {e}")
        Logs_erros.logs_erro(805,'Operação anulada', 'Nao pode eliminar proprietario', pathlogs)

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
    print("Escreva 'voltar' em qualquer campo para cancelar a operação.")

    try:
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

    except OperacaoCancelada:
        informar_cancelamento()
        return

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
        Logs_erros.logs_erro(806,'Operação anulada', 'O NIF já exite na bd inquilino', pathlogs)

        # Anular eventuais alterações não guardadas
        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao registar inquilino: {e}")
        Logs_erros.logs_erro(807,'Operação anulada', 'Erro de registo de inquilino', pathlogs)

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
            # Formatar o ordenado mensal com duas casas decimais, tal como anteriormente.
            dados_inquilinos = []
            for inquilino in inquilinos:
                dados_inquilinos.append((*inquilino[:6], f"{inquilino[6]:.2f} €"))

            mostrar_tabela(
                "INQUILINOS REGISTADOS",
                ["NIF", "Nome", "Data de nascimento", "Sexo", "Contacto telefónico", "Email", "Ordenado mensal"],
                dados_inquilinos
            )

    except sqlite3.Error as e:
        print(f"\nErro ao consultar inquilinos: {e}")
        Logs_erros.logs_erro(808,'Operação anulada', 'Erro ao consultar inquilinos', pathlogs)

    finally:
        # Fechar a ligação à base de dados, caso tenha sido estabelecida
        if conexao is not None:
            conexao.close()

        input("\nPressione Enter para voltar ao menu...")


def editar_inquilinos():
    print("\n--- EDITAR DADOS DO INQUILINO ---")
    print("Escreva 'voltar' para cancelar a operação.")

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

        # Guardar os novos valores num dicionário. Ainda não são escritos na base de dados.
        novos_valores = {}

        # O inquirer.List devolve apenas uma opção de cada vez.
        # Repetir o menu permite selecionar vários campos antes de confirmar a edição.
        while True:
            menu = [inquirer.List("campos",
                    message="Selecione um campo para alterar ou termine a seleção",
                    choices=["1. Nome completo", "2. Data de nascimento", "3. Sexo", "4. Contacto telefónico", "5. Email", "6. Ordenado mensal", "0. Terminar seleção"])
            ]

            answers = inquirer.prompt(menu)

            # Cancelar a edição se o utilizador interromper o menu
            if answers is None:
                print("\nEdição cancelada. Nenhum dado foi alterado.")
                return

            campo = answers["campos"]  # O List devolve uma string, não uma lista.

            if campo == "0. Terminar seleção":
                break

            if campo == "1. Nome completo":
                novos_valores["nome_completo"] = validar_nome(edicao=True)

            elif campo == "2. Data de nascimento":
                novos_valores["data_nascimento"] = validar_data_nascimento("inquilino", edicao=True)

            elif campo == "3. Sexo":
                novos_valores["sexo"] = validar_sexo(edicao=True)

            elif campo == "4. Contacto telefónico":
                novos_valores["contacto_telefonico"] = validar_contacto_telefonico(edicao=True)

            elif campo == "5. Email":
                novos_valores["email"] = validar_email(edicao=True)

            elif campo == "6. Ordenado mensal":
                novos_valores["ordenado_mensal"] = validar_ordenado(edicao=True)

        # Não tentar fazer UPDATE se nenhum campo tiver sido alterado.
        if len(novos_valores) == 0:
            print("\nNão selecionou nenhum campo para alterar.")
            Logs_erros.logs_erro(809,'Operação anulada', 'Nenhum campo selecionado para alteracao', pathlogs)
            return

        # Apresentar um resumo dos dados que vão ser alterados
        print("\n--- CONFIRMAR ALTERAÇÕES ---\n")
        print(f"NIF do inquilino: {nif}")

        for coluna, valor in novos_valores.items():
            if coluna == "ordenado_mensal":
                print(f"{coluna}: {valor:.2f} €")
            else:
                print(f"{coluna}: {valor}")

        print()  # Adicionar uma linha em branco antes da confirmação.

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

    except OperacaoCancelada:
        informar_cancelamento()
        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar erros relacionados com a base de dados
        print(f"\nErro ao editar inquilino: {e}")
        Logs_erros.logs_erro(810,'Operação anulada', 'Erro a editar inquilino', pathlogs)

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()


def eliminar_inquilinos():
    print("\n--- ELIMINAR INQUILINO ---")
    print("Escreva 'voltar' para cancelar a operação.")

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
            Logs_erros.logs_erro(811,'Operação anulada', 'Nao pode eliminar inquilino selecionado', pathlogs)

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

    except OperacaoCancelada:
        informar_cancelamento()
        if conexao is not None:
            conexao.rollback()

    except sqlite3.IntegrityError:
        # Impedir a eliminação caso existam relações protegidas
        print("\nNão foi possível eliminar o inquilino.")
        Logs_erros.logs_erro(811,'Operação anulada', 'Nao pode eliminar inquilino selecionado', pathlogs)
        print("Existem registos associados que impedem a eliminação.")

        if conexao is not None:
            conexao.rollback()

    except sqlite3.Error as e:
        # Tratar outros erros relacionados com a base de dados
        print(f"\nErro ao eliminar inquilino: {e}")
        Logs_erros.logs_erro(811,'Operação anulada', 'Nao pode eliminar inquilino selecionado', pathlogs)

        if conexao is not None:
            conexao.rollback()

    finally:
        # Fechar a ligação à base de dados
        if conexao is not None:
            conexao.close()
