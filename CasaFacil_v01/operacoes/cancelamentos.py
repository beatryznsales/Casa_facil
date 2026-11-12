
# Exceção utilizada para cancelar uma operação
class OperacaoCancelada(Exception): # Criar uma nova classe chamada OperacaoCancelada, onde se o utilizador escrever "voltar" a função gera uma exceção
    pass # Não é necessario escrever nenhuma instrução então usa-se o "pass" para evitar um IndentationError


def pedir_input(mensagem):

    # Pedir ao utilizador que introduza um valor
    valor = input(mensagem).strip()

    # Verificar se o utilizador pretende cancelar a operação
    # lower() permite aceitar "voltar", "VOLTAR" ou "Voltar"
    if valor.lower() == "voltar":
        raise OperacaoCancelada

    # Devolver o valor introduzido para ser validado normalmente
    return valor


def informar_cancelamento():

    # Informar o utilizador de que a operação foi cancelada
    print("\nOperação cancelada. A regressar ao menu anterior.")
