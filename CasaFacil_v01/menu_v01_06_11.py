
# Para phonenumbers, inquirer e rich e todos os imports, deve-se preparar um ficheiro requirements.txt para facilitar a instalação dessas dependências nos computadores externos

import os
from operacoes.imoveis import *
from operacoes.proprietario_inquilinos import *
import inquirer # O módulo inquirer facilita a criação de listas de opções, prompts e outros elementos de interface de linha de comando.

from rich.console import Console  # Utilizar rich em conjunto com o inquirer para personalizar o menu
from rich.panel import Panel
from rich.text import Text

import sys
sys.path.append(os.path.realpath(".")) # Adicionar o directorio de trabalho ao módulo de procura do python, permitindo importar modulos locais e scripts sem ter de instalar


console = Console() # Inicializar a consola para apresentar os elementos gráficos do rich

# Obter o caminho completo da pasta onde o programa está guardado

# __file__ identifica o ficheiro Python em execução
# os.path.abspath() obtém o caminho absoluto desse ficheiro
# os.path.dirname() devolve a pasta onde o ficheiro está guardado
pasta_programa = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho da base de dados na pasta do programa
# os.path.join() junta o caminho da pasta ao nome do ficheiro
base_de_dados = os.path.join(pasta_programa, "casa_facil.db")


#####################################     FUNÇÃO AUXILIAR PARA OS MENUS     ############################################################################################################################


def mostrar_cabecalho(titulo):

    # Criar o nome da aplicação, centrado dentro da moldura
    texto = Text("CASAFÁCIL LDA.", style="bold bright_cyan", justify="center")

    # Criar uma moldura 
    painel = Panel(
        texto,
        title=" SISTEMA DE GESTÃO IMOBILIÁRIA ",
        title_align="center",
        border_style="bright_blue",
        padding=(0, 5),
        width=52
    )

    # Apresentar o cabeçalho no terminal
    console.print()
    console.print(painel)

    # Apresentar o título do menu 
    console.print(f"\n{titulo}", style="bold bright_cyan")

    # Apresentar as instruções de navegação e uma linha separadora
    console.print("Use ↑ ↓ para navegar e Enter para selecionar.", style="dim yellow")
    console.print("─" * 52, style="bright_blue\n")


########## O menu principal precisa ficar abaixo das funções, para que estas possam ser chamadas quando o utilizador escolher a opção correspondente no menu.

#####################################     MENU PRINCIPAL     ############################################################################################################################

def menu_principal():

    # Menu principal da aplicação - o utilizador fica no menu principal até escolher a opção de sair da aplicação
    # Permite escolher entre a gestão de imóveis, inquilinos e proprietários, ou sair da aplicação

    while True:
        
        # Limpar o terminal sempre que o menu é apresentado
        os.system("cls" if os.name == "nt" else "clear")

        mostrar_cabecalho("⫶☰  MENU PRINCIPAL")

        menu = [inquirer.List('opcao',
                message="Escolha o que quer fazer",
                choices=["1. Gestão de Imóveis", "2. Gestão de Inquilinos", "3. Gestão de Proprietários", "0. Sair"]
            )
        ]

        answers = inquirer.prompt(menu)

        # Terminar o menu se o utilizador cancelar
        if answers is None:
            break

        opcao = answers['opcao'][0]  # Extrair o primeiro caractere da opção selecionada

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
            wait = input()
            break

        elif opcao == "":
            print("Não introduziu nenhuma opção. Tente novamente.")

        else:
            print("Opção inválida! Escolha um número entre 0 e 3.")


#####################################     MENU DOS IMÓVEIS     ############################################################################################################################

def menu_imoveis():

    while True:

        os.system("cls" if os.name == "nt" else "clear")

        mostrar_cabecalho("🏠︎ GESTÃO DE IMÓVEIS")

        menu = [inquirer.List('opcao',
                message="Escolha o que quer fazer",
                choices=["1. Adicionar imóvel", "2. Consultar todos os imóveis", "3. Consultar imóveis disponíveis", "4. Consultar imóveis alugados", "5. Alterar dados de um imóvel", "6. Atribuir imóvel a um inquilino", "7. Encerrar contrato de arrendamento", "0. Voltar ao menu principal"]
            )
        ]

        answers = inquirer.prompt(menu)

        # Terminar o menu se o utilizador cancelar
        if answers is None:
            break

        opcao = answers['opcao'][0]  # Extrair o primeiro caractere da opção selecionada

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

        elif opcao == "6":
            atribuir_imovel_inquilino()

        elif opcao == "7":
            encerrar_contrato_arrendamento()

        elif opcao == "0":
            break

        elif opcao == "":
            print("Não introduziu nenhuma opção. Tente novamente.")

        else:
            print("Opção inválida!")


#####################################     MENU DOS PROPRIETÁRIOS     ############################################################################################################################

def menu_proprietarios():

    while True:

        os.system("cls" if os.name == "nt" else "clear")

        mostrar_cabecalho("𖨆 GESTÃO DE PROPRIETÁRIOS")

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


#####################################     MENU DOS INQUILINOS     ############################################################################################################################

def menu_inquilinos():

    while True:

        os.system("cls" if os.name == "nt" else "clear")

        mostrar_cabecalho("𖨆𖨆 GESTÃO DE INQUILINOS")

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


# Chamar o menu principal quando o programa é executado
menu_principal()
