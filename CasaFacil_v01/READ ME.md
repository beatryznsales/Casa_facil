**# VERIFICAR CODIGO POSTAL** 



import json

import urllib.request

import urllib.error





else:

&#x20;       # Consultar a GEO API PT para verificar a existência do código postal.

&#x20;       url = f"https://json.geoapi.pt/cp/{codigo\_postal}"



&#x20;       try:

&#x20;           with urllib.request.urlopen(url, timeout=5) as resposta:

&#x20;               dados\_postais = json.load(resposta)



&#x20;           # Confirmar que a resposta corresponde ao código postal introduzido.

&#x20;           if dados\_postais.get("CP") != codigo\_postal:

&#x20;               print("Não foi possível confirmar o código postal.")

&#x20;               continue



&#x20;           print("Código postal encontrado com sucesso!")

&#x20;           break



&#x20;       except urllib.error.HTTPError as e:

&#x20;           if e.code == 404:

&#x20;               print("O código postal não foi encontrado na base de dados.")

&#x20;           else:

&#x20;               print("Não foi possível consultar o serviço de códigos postais.")

&#x20;               return



&#x20;       except (urllib.error.URLError, TimeoutError, OSError,

&#x20;               ValueError, UnicodeDecodeError):

&#x20;           print("Erro de comunicação ou de leitura dos dados do serviço.")

&#x20;           print("Não foi possível validar o código postal. Tente novamente mais tarde.")

&#x20;           return





**# VERIFICAR NIF**



**Código**

if (len(nif\_proprietario) != 9 or not nif\_proprietario.isascii() or not nif\_proprietario.isdigit()):



\# "or" pois basta que uma das condições não se apresente para que o NIF seja rejeitado

\# "!=" quando se pretende que seja diferente de

\# ".isascii()" verifica se todos os caracteres pertencem à tabela ASCII

\# ".isdigit()" verifica se todos os caracteres são dígitos numéricos, mas também aceita exponenciais ^2.

\# "continue" interrompe a iteração atual do ciclo while True e inicia uma nova, permitindo pedir novamente o NIF ao utilizador



Nota: a combinação de ambos permite garantir que só são aceites algoritmos de 0 a 9.



**Código**

soma = 0

for i in range(8):

&#x20;   soma += int(nif\_proprietario\[i]) \* (9 - i)



\# Nota: o NIF (Número de Identificação Fiscal) português tem um dígito de controlo: o nono dígito é calculado a partir dos oito primeiros dígitos através de um algoritmo módulo 11.

\# "for i in range(8)" percorre os índices de 0 a 7, correspondentes aos primeiros 8 algarismos

\# "nif\_proprietario\[i]" obtém o algarismo do NIF na **posição i**

\# "int()" converte o algarismo de texto para número inteiro

\# "(9 - i)" calcula o peso a aplicar ao algarismo, começando em 9 e terminando em 2

\# "soma +=" adiciona o resultado da multiplicação ao valor acumulado na variável soma.



Nota: não usei range(9) pois, apesar de NIF ter 9 algarismos, o último digito é o de controlo (calculado a partir dos primeiros 8 algarismos).



**Código**

resto = soma % 11



\# % devolve o resto da divisão inteira

\# o algoritmo de validação do NIF português se baseia no módulo 11



**Código**

if resto < 2:

&#x20;   digito\_controlo = 0

else:

&#x20;   digito\_controlo = 11 - resto



\# se o resto for 0 ou 1, o dígito de controlo é 0

\# se o resto for igual ou superior a 2, o dígito de controlo é calculado subtraindo o resto a 11



**Código**

if digito\_controlo != int(nif\_proprietario\[8]): 

&#x20;           print("NIF inválido. O dígito de controlo não está correto.")

&#x20;           continue



\# fica \[8] uma vez que o python começa em 0, ou seja o nono e ultimo digito fica na posição 8





