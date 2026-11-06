

import datetime
import os
import sqlite3

# Obter o caminho completo da pasta onde o programa está guardado.

# __file__ identifica o ficheiro Python em execução.
# os.path.abspath() obtém o caminho absoluto desse ficheiro.
# os.path.dirname() devolve a pasta onde o ficheiro está guardado.
pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa.
# os.path.join() junta o caminho da pasta ao nome do ficheiro.
base_de_dados = os.path.join(pasta_programa, "casa_facil.db")

#####################################     DEFINIÇÃO DAS FUNÇÕES     ############################################################################################################################

## Para os Imóveis: as funções de adicionar, consultar, alterar e atribuir imóveis a inquilinos são definidas abaixo.

def adicionar_imovel():       # Colocar limites para que em "Rua" não seja possível colocar números, e em "Cidade" não seja possível colocar números nem caracteres especiais.
    print("\n--- ADICIONAR NOVO IMÓVEL ---")
   
    # 1. Recolher dados da morada
    print("\nIndique os dados da morada do imóvel:")
    rua = input("Rua: ").strip()        #  
    num_porta = input("Número da porta: ").strip()
    num_apartamento = input("Número do apartamento (se houver): ").strip()
    codigo_postal = input("Código Postal: ").strip() # verificar ifen e fazer split pelo mesmo.
    cidade = input("Cidade: ").strip()
 
    # 2. Recolher dados do imóvel
    print("\nIndique os dados do imóvel:")
    tipo = input("Tipo de imóvel: ").strip()
   
    while True:
        try:
            quartos = int(input("Número de quartos: "))
            break
        except ValueError:
            print("Por favor, insira um número válido para os quartos.")
           
    estado = input("Estado do imóvel (ex: Nova, Usada ou Mau estado): ").strip()
   
    while True:
        try:
            renda = float(input("Valor da renda: "))
            break
        except ValueError:
            print("Por favor, insira um valor numérico válido para a renda.")
           
    duracao = input("Duração do contrato (ex: 6 meses, 1 ano): ").strip()
    situacao = input("Situação (ex: Disponível, Arrendada): ").strip()
   
    while True:
        nif_proprietario = input("NIF do proprietário responsável: ").strip()
        if nif_proprietario.isdigit() and len(nif_proprietario) == 9:
            nif_proprietario = int(nif_proprietario)
            break
        print("NIF inválido. Deve conter exatamente 9 dígitos numéricos.")
 
    # 3. Inserir na Base de Dados
    try:
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()
       
        # Verificar se o proprietário existe antes de associar o imóvel
        cursor.execute("SELECT nif FROM proprietarios WHERE nif = ?", (nif_proprietario,))
        if not cursor.fetchone():
            print(f"\nErro: Não existe nenhum proprietário registado com o NIF {nif_proprietario}.")
            print("Deve registar primeiro o proprietário antes de adicionar o imóvel.")
            conexao.close()
            return
 
        # Inserir primeiro a morada para obter o ID gerado automaticamente (autoincrement)
        cursor.execute("""
            INSERT INTO moradas (rua, num_porta, num_apartamento, codigo_postal, cidade)
            VALUES (?, ?, ?, ?, ?)
        """, (rua, num_porta, num_apartamento, codigo_postal, cidade))
       
        id_morada = cursor.lastrowid  # Captura o ID da morada que acabou de ser criada
 
        # Inserir o imóvel associando a morada criada e o proprietário
        cursor.execute("""
            INSERT INTO imoveis (tipo, quartos, id_morada, estado, renda, duracao, situacao, nif_proprietario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tipo, quartos, id_morada, estado, renda, duracao, situacao, nif_proprietario))
 
        conexao.commit()
        print("\nImóvel e respetiva morada adicionados com sucesso à base de dados!")
 
    except sqlite3.Error as e:
        print(f"\nErro ao aceder à base de dados: {e}")
    conexao.close()


def consultar_imoveis():   ### ATENCAO: melhorar a consulta com JOIN para mostrar os detalhes da morada, do inquilino e do proprietário, em vez de apenas os IDs. ###
    # Estabelecer ligação à base de dados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
        # Consultar todos os imóveis registados.
        cursor.execute("SELECT * FROM imoveis")
        
        #SELECT imoveis.id, imoveis.tipo, imoveis.quartos, imoveis.estado, imoveis.renda, imoveis.duracao, imoveis.situacao, imoveis.nif_proprietario, moradas.rua, moradas.num_porta, moradas.num_apartamento, moradas.codigo_postal, moradas.cidade
        #FROM imoveis JOIN moradas ON imoveis.id_morada = moradas.id

        imoveis = cursor.fetchall()

        if len(imoveis) == 0:
            print("\nNão existem imóveis registados.")

        else:
            print("\n--- LISTA DE IMÓVEIS ---")

            for imovel in imoveis:
                print("\n" + "-" * 40)
                print(f"ID: {imovel[0]}")
                print(f"Tipo: {imovel[1]}")
                print(f"Número de quartos: {imovel[2]}")
                print(f"ID da morada: {imovel[3]}")
                print(f"Estado: {imovel[4]}")
                print(f"Renda mensal: {imovel[5]:.2f} €")
                print(f"Duração do contrato: {imovel[6]}")
                print(f"Situação: {imovel[7]}")
                print(f"NIF do proprietário: {imovel[8]}")

    except sqlite3.Error as e:
        print(f"Erro ao consultar imóveis: {e}")

    finally:
        # Fechar a ligação à base de dados.
        conexao.close()



#####################################################################################################################################################

## Para os Proprietários: as funções de adicionar e consultar proprietários são definidas abaixo.

def adicionar_proprietario():
    # Recolher os dados do novo proprietário.
    print("\n--- REGISTAR PROPRIETÁRIO ---")

    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (AAAA-MM-DD): ").strip()
    sexo = input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

    # Validar o NIF.
    while True:
        nif = input("NIF: ").strip()

        if nif.isdigit() and len(nif) == 9:
            nif = int(nif)
            break
        else:
            print("NIF inválido! Deve conter 9 dígitos.")

    telemovel = input("Número de telemóvel: ").strip()
    email = input("Email: ").strip()

    # O proprietário começa sem imóveis registados.
    num_habitacoes = 0

    try:
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Inserir os dados na tabela de proprietários.
        cursor.execute("""
            INSERT INTO proprietarios
            (nif, nome_completo, data_nascimento, sexo,
             numero_telemovel, email, N_habitacoes_registadas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nif, nome, data_nascimento, sexo,
              telemovel, email, num_habitacoes))

        conexao.commit()
        print("\nProprietário inserido na base de dados com sucesso!")

    except sqlite3.IntegrityError:
        print("\nErro! Já existe um proprietário com esse NIF.")

    except sqlite3.Error as e:
        print(f"\nErro ao registar proprietário: {e}")

    finally:
        if 'conexao' in locals():
            conexao.close()


def consultar_proprietarios():
    # Consultar os proprietários registados na base de dados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
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
        conexao.close()

#####################################################################################################################################################

## Para os Inquilinos: as funções de adicionar e consultar inquilinos são definidas abaixo.


def adicionar_inquilino():
    # Recolher os dados do novo inquilino.
    print("\n--- REGISTAR INQUILINO ---")

    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (AAAA-MM-DD): ").strip()
    sexo = input("Sexo (Masculino (M)/Feminino (F)/Outro (O)): ").strip().upper()

    # Validar o NIF.
    while True:
        nif = input("NIF: ").strip()

        if nif.isdigit() and len(nif) == 9:
            nif = int(nif)
            break
        else:
            print("NIF inválido! Deve conter 9 dígitos.")

    telemovel = input("Número de telemóvel: ").strip()
    email = input("Email: ").strip()

    # Validar o ordenado mensal.
    while True:
        try:
            ordenado = float(input("Ordenado mensal (€): ").replace(",", "."))

            if ordenado >= 0:
                break
            else:
                print("O ordenado não pode ser negativo.")

        except ValueError:
            print("Introduza um valor numérico válido.")

    try:
        conexao = sqlite3.connect(base_de_dados)
        cursor = conexao.cursor()

        # Inserir os dados na tabela de inquilinos.
        cursor.execute("""
            INSERT INTO inquilinos
            (nif, nome_completo, data_nascimento, sexo,
             numero_telemovel, email, ordenado_mensal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nif, nome, data_nascimento, sexo,
              telemovel, email, ordenado))

        conexao.commit()
        print("\nInquilino registado com sucesso!")

    except sqlite3.IntegrityError:
        print("\nErro! Já existe um inquilino com esse NIF.")

    except sqlite3.Error as e:
        print(f"\nErro ao registar inquilino: {e}")

    finally:
        if 'conexao' in locals():
            conexao.close()



def consultar_inquilinos():
    # Consultar todos os inquilinos registados.
    conexao = sqlite3.connect(base_de_dados)
    cursor = conexao.cursor()

    try:
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

