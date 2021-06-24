strArr = ['(A,B,C)', '(B-A,C-B)', '(C,B,A)']
lista = []
lista2 = []
excecao = []
for i in range(1, len(strArr[0])-1, 2):
    lista2.append(strArr[0][i])
lista.append(lista2)
lista2 = []
for u in range(1, len(strArr[1])-1, 4):
    lista2.append(strArr[1][u]+strArr[1][u+1] + strArr[1][u+2])
lista.append(lista2)
lista2 = []
for i in range(1, len(strArr[2])-1, 2):
    lista2.append(strArr[2][i])
lista.append(lista2)
count = 0
for k in range(0, len(lista[2])-1):
    for l in lista[1]:
        if lista[2][k] in l and lista[2][k+1] in l:
            count += 1
        else:
            excecao.append(lista[2][k])
    if count == len(lista[2])-1:
        print('yes')
    else:
        print(excecao[-1])
