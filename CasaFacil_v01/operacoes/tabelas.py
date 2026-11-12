# Transformar os dados das consultas de listas para tabelas
from rich.console import Console
from rich.table import Table
from rich.text import Text

# Inicializar a consola para apresentar as tabelas
console = Console()


def mostrar_tabela(titulo, colunas, dados):

    # Criar a tabela com um título e uma moldura azul
    tabela = Table(
        title=titulo,
        title_style="bold bright_cyan",
        header_style="bold yellow",
        border_style="bright_blue",
        show_lines=True
    )

    # Adicionar os nomes das colunas à tabela, com apenas os cabeçalhos centrados
    for coluna in colunas:
        tabela.add_column(coluna)

    # Percorrer os registos obtidos da base de dados
    for registo in dados:

        # Converter os valores para texto, substituindo valores nulos por "-"
        valores = []

        for valor in registo:
            if valor is None:
                valores.append("-")
            else:
                valores.append(str(valor))

        # Adicionar uma linha à tabela com os valores do registo
        tabela.add_row(*valores)

    # Apresentar a tabela no terminal
    console.print()
    console.print(tabela)

    # Apresentar o número total de registos consultados
    console.print(f"\nTotal de registos: {len(dados)}", style="dim cyan")
