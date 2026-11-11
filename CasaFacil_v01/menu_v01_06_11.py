## inquirer
#### Adicionar uma contagem para que sempre que um imovel seja adicionado, o proprietario ganhe +1 no numero de imoveis que este tenha
#### validar todos os inputs pedidos pelo código
### Colocar o os.system() para limpar o terminal
## Editar informações: Permitir editar os dados das tabelas para as 3 entidades
## Adicionar erros LOG

# Para phonenumbers e inquirer, deve-se preparar um ficheiro requirements.txt para facilitar a instalação dessas dependências nos computadores externos

import os
from operacoes.imoveis import *
from operacoes.proprietario_inquilinos import *
import inquirer   
import sys
sys.path.append(os.path.realpath(".")) # adiciona o directorio de trabalho ao módulo de procura do python, permitindo importar modulos locais e scripts sem ter de instalar

# Obter o caminho completo da pasta onde o programa está guardado

# __file__ identifica o ficheiro Python em execução
# os.path.abspath() obtém o caminho absoluto desse ficheiro
# os.path.dirname() devolve a pasta onde o ficheiro está guardado
pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa 
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "casa_facil.db")

########## O menu principal precisa ficar abaixo das funções, para que estas possam ser chamadas quando o utilizador escolher a opção correspondente no menu.
#####################################     MENU PRINCIPAL     ############################################################################################################################

def menu_principal():

    # Menu principal da aplicação - o utilizador fica no menu principal até escolher a opção de sair da aplicação.
    # Permite escolher entre a gestão de imóveis, inquilinos e proprietários, ou sair da aplicação.
    
    if os.name == "nt":   # Limpar o terminal de forma compativel a diferentes sistemas operativos
        os.system("cls")
    else:
        os.system("clear")
    
    while True:
        print("\n" + "=" * 40)
        print("   CASAFÁCIL LDA. - GESTÃO DE IMÓVEIS")
        print("=" * 40)
        print("") 
        print("Use as setas ⬆ ⬇︎ para navegar no Menu.") 
        print("")
       

        #print("1. Gestão de Imóveis")
        #print("2. Gestão de Inquilinos")
        #print("3. Gestão de Proprietários")
       # print("0. Sair")
        #print("=" * 40)
 
        #opcao = input("Escolha uma opção: ").strip()
        menu=[inquirer.List('opcao',
                            message="Escolha o que quer fazer",
                            choices=["1. Gestão de Imóveis", "2. Gestão de Inquilinos","3. Gestão de Proprietários","0. Sair"]
            ),
        ]

        answers = inquirer.prompt(menu)
        opcao = answers['opcao'][0]  # Extrair o primeiro caractere da string selecionada, que corresponde à opção escolhida (1, 2, 3 ou 0)



        if opcao == "1":
            menu_imoveis()
 
        elif opcao == "2":
            menu_inquilinos()
 
        elif opcao == "3":
            menu_proprietarios()

        elif opcao == "0":
            print(" A sair da aplicação CasaFácil, LDA. Obrigado(a) por utilizar o nosso software!")
            print("""\n        Coded by Beatryz Souza, Filipa Nogueira and Vívian Santos.""")
            print("\n")
            break

        elif opcao == "":
            print("Não introduziu nenhuma opção. Tente novamente.")
 
        else:
            print("Opção inválida! Escolha um número entre 0 e 3.")

#modulo inquirer - aplicado para criar menus interativos no terminal, permitindo ao utilizador escolher opções de forma mais intuitiva e visualmente agradável. O módulo inquirer facilita a criação de listas de opções, prompts e outros elementos de interface de linha de comando.


def menu_imoveis():

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    
    while True:
        print("\n--- GESTÃO DE IMÓVEIS ---")

        menu=[inquirer.List('opcao',
            message="Escolha o que quer fazer",
            choices=["1. Adicionar imóvel", "2. Consultar todos os imóveis","3. Consultar imóveis disponíveis", "4. Consultar imóveis alugados", "5. Alterar dados de um imóvel", "6. Atribuir imóvel a um inquilino", "7. Encerrar contrato de arrendamento", "0. Voltar ao menu principal"]
            ),
        ]
        answers = inquirer.prompt(menu)
        opcao = answers['opcao'][0]  # Extrair o primeiro caractere da string selecionada, que corresponde à opção escolhida (1, 2, 3 ou 0)
                 
        if opcao == "1":
            adicionar_imovel()

        elif opcao == "2":
            consultar_imoveis()

        elif opcao == "3":
            consultar_imoveis_disponiveis()

        elif opcao == "4":
            consultar_imoveis_alugados()

        elif opcao == "5":
            alterar_dados_imovel()

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

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


    while True:

        menu=[inquirer.List('opcao',
                    message="\n--- GESTÃO DE INQUILINOS ---",
                    choices=["1. Registar inquilino", "2. Consultar todos os inquilinos","0. Voltar ao menu principal"]
                ),
            ]
        answers = inquirer.prompt(menu)
        opcao = answers['opcao'][0]  # Extrair o primeiro caractere da string selecionada, que corresponde à opção escolhida (1, 2, 3 ou 0)

 
        if opcao == "1":
            adicionar_inquilino()

        elif opcao == "2":
            consultar_inquilinos()

        elif opcao == "0":
            break

        else:
            print("Opção inválida!")


def menu_proprietarios():

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


    while True:

        print("\n--- GESTÃO DE PROPRIETÁRIOS ---")

        menu = [inquirer.List("opcao",
                message="Escolha o que quer fazer",
                choices=["1. Registar proprietário", "2. Consultar todos os proprietários", "3. Editar dados de um proprietário", "4. Eliminar proprietário", "0. Voltar ao menu principal"]
            )
        ]

        answers = inquirer.prompt(menu)

        if answers is None: # Terminar o menu se o utilizador cancelar
            break

        opcao = answers["opcao"][0] # Extrair o primeiro caractere da opção selecionada

        if opcao == "1":
            adicionar_proprietario()

        elif opcao == "2":
            consultar_proprietarios()

        elif opcao == "3":
            editar_proprietarios()

        elif opcao == "4":
            eliminar_proprietarios()

        elif opcao == "0":
            break


def menu_inquilinos():

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


    while True:

        print("\n--- GESTÃO DE INQUILINOS ---")

        menu = [inquirer.List("opcao",
                message="Escolha o que quer fazer",
                choices=["1. Registar inquilino", "2. Consultar todos os inquilinos", "3. Editar dados de um inquilino", "4. Eliminar inquilino", "0. Voltar ao menu principal"]
            )
        ]

        answers = inquirer.prompt(menu)

        if answers is None: # Terminar o menu se o utilizador cancelar
            break

        opcao = answers["opcao"][0] # Extrair o primeiro caractere da opção selecionada

        if opcao == "1":
            adicionar_inquilino()

        elif opcao == "2":
            consultar_inquilinos()

        elif opcao == "3":
            editar_inquilinos()

        elif opcao == "4":
            eliminar_inquilinos()

        elif opcao == "0":
            break

menu_principal() # de forma a que o menu principal seja chamado quando o programa é executado, iniciando a aplicação.

