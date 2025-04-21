"""
Logistics Optimization Model for Offshore Supply
Autor: Pedro Silva
Language: Python (PuLP)
Description: This model aims to minimize the total costs of an offshore supply network,
considering fixed installation costs for distribution centers, operational costs, and transportation costs.
"""

import pulp

# Criação do modelo de otimização
import pulp as pl
import time  


capacidade = Capacidade_Camioes[cenario]
custo_granel_solido = Custo_Transporte["Granel solido",capacidade]
custo_carga_geral = Custo_Transporte["Carga Geral",capacidade]
print(cenario)
print(capacidade)
print(custo_granel_solido)
print(custo_carga_geral)
Capacidade_Recepcao = [Capacidades_Rececao[(cenario, cd)] for cd in Centros_Distribuicao]
print(Capacidade_Recepcao)
Custo_Operacao = [Custos_Operacao[(cenario, cd)] for cd in Centros_Distribuicao]

# Definição do modelo
model = pl.LpProblem("Modelo_Distribuicao_Logistica", pl.LpMinimize)

# Variáveis de decisão
InstalarCD = pl.LpVariable.dicts("InstalarCD", [cd for cd in Centros_Distribuicao], cat="Binary")  # 1 se o CD for instalado, 0 caso contrário
QtdFornecedorCD = pl.LpVariable.dicts("QtdFornecedorCD", [(fornecedor, cd, tipo_carga) for fornecedor in Fornecedores for cd in Centros_Distribuicao for tipo_carga in Tipos_Carga], lowBound=0, cat="Continuous")
QtdCDBase = pl.LpVariable.dicts("QtdCDBase", [(cd, base, tipo_carga) for cd in Centros_Distribuicao for base in Bases_Logisticas for tipo_carga in Tipos_Carga], lowBound=0, cat="Continuous")
VeiculosFornecedorCD = pl.LpVariable.dicts("VeiculosFornecedorCD", [(fornecedor, cd, tipo_carga) for fornecedor in Fornecedores for cd in Centros_Distribuicao for tipo_carga in Tipos_Carga], lowBound=0, cat="Integer")
VeiculosCDBase = pl.LpVariable.dicts("VeiculosCDBase", [(cd, base, tipo_carga) for cd in Centros_Distribuicao for base in Bases_Logisticas for tipo_carga in Tipos_Carga], lowBound=0, cat="Integer")

# Funcao Objetivo
model += (
    pl.lpSum(Custo_Instalacao[cd] * InstalarCD[(cd)] for cd in Centros_Distribuicao) +
    pl.lpSum(Custo_Operacao[(int(cd)-1)] * InstalarCD[(cd)] for cd in Centros_Distribuicao) +
    pl.lpSum(Distancia_Fornecedor_CD[(fornecedor, cd)] * Custo_Transporte[(tipo_carga,capacidade)] * VeiculosFornecedorCD[(fornecedor, cd, tipo_carga)] * capacidade 
             for fornecedor in Fornecedores for cd in Centros_Distribuicao for tipo_carga in Tipos_Carga) +
    pl.lpSum(Distancia_CD_Base[(cd, base)] * Custo_Transporte[(tipo_carga,capacidade )] * VeiculosCDBase[(cd, base, tipo_carga)] * capacidade 
             for cd in Centros_Distribuicao for base in Bases_Logisticas for tipo_carga in Tipos_Carga)
)

# Restricoes
                      
# Restricao de fornecimento: assegurar que cada fornecedor envia a quantidade correta para os CDs
for fornecedor in Fornecedores:
    for tipo_carga in Tipos_Carga:
        model += pl.lpSum(QtdFornecedorCD[(fornecedor, cd, tipo_carga)] for cd in Centros_Distribuicao) <= Quantidade_Fornecedor[(fornecedor, tipo_carga)]

# Restrição de procura nas bases: garantir que a quantidade total enviada para cada base e a correta
for cd in Centros_Distribuicao:
    for tipo_carga in Tipos_Carga:
        model += pl.lpSum(QtdCDBase[(cd, base, tipo_carga)] for base in Bases_Logisticas) == pl.lpSum(QtdFornecedorCD[(fornecedor, cd, tipo_carga)] for fornecedor in Fornecedores)

# Restrição de capacidade dos CDs: limitar a quantidade total recebida pelos CDs com base na capacidade
for cd in Centros_Distribuicao:
    model += pl.lpSum(QtdFornecedorCD[(fornecedor, cd,tipo_carga)] for fornecedor in Fornecedores for tipo_carga in Tipos_Carga) <= InstalarCD[(cd)] * Capacidade_Recepcao[int(cd)-1]

# Restrição de procura nas bases logisticas: garantir que cada base recebe a quantidade correta por tipo de carga
for base in Bases_Logisticas:
    for tipo_carga in Tipos_Carga:
        model += pl.lpSum(QtdCDBase[(cd, base,tipo_carga)] for cd in Centros_Distribuicao) == Procura_Base[(base, tipo_carga)]

# Restrição de veículos entre fornecedor e CD: garantir que a quantidade de veículos é suficiente para transportar a carga (6)(7)
for fornecedor in Fornecedores:
    for cd in Centros_Distribuicao:
        for tipo_carga in Tipos_Carga:
            model += VeiculosFornecedorCD[(fornecedor, cd, tipo_carga)] >= pl.lpSum(QtdFornecedorCD[(fornecedor, cd, tipo_carga)] / capacidade)

# Restrição de veículos entre CD e base: garantir que a quantidade de veículos é suficiente para transportar a carga
for cd in Centros_Distribuicao:
    for base in Bases_Logisticas:
        for tipo_carga in Tipos_Carga:
            model += VeiculosCDBase[(cd, base, tipo_carga)] >= pl.lpSum(QtdCDBase[(cd, base, tipo_carga)] / capacidade)

start_time = time.time()
# Resolver o modelo
model.solve()
print("FO: ", model.objective.value())
end_time = time.time()
execution_time = end_time - start_time
print("Tempo de execução do modelo: {:.2f} segundos".format(execution_time))

# Status do modelo
print("Estado:", pl.LpStatus[model.status])
print(int(sum(InstalarCD[cd].value() for cd in Centros_Distribuicao)))
for cd in Centros_Distribuicao:
    print(InstalarCD[cd].value())

# Número de camioes alocados a cada CD
for cd in Centros_Distribuicao:
    camioes_fornecedor_cd = sum(VeiculosFornecedorCD[(fornecedor, cd, tipo_carga)].value() for fornecedor in Fornecedores for tipo_carga in Tipos_Carga)
    camioes_cd_base = sum(VeiculosCDBase[(cd, base, tipo_carga)].value() for base in Bases_Logisticas for tipo_carga in Tipos_Carga)
    camioes_totais = camioes_fornecedor_cd + camioes_cd_base
    print("CD {}: {:.0f} camiões alocados (Fornecedor -> CD: {:.0f}, CD -> Base: {:.0f})".format(cd, camioes_totais, camioes_fornecedor_cd, camioes_cd_base))


# Calculo dos resultados para cada cenario e impressao individual

numero_cds_abertos = int(sum(InstalarCD[cd].value() for cd in Centros_Distribuicao))
custos_fixos = sum(Custo_Instalacao[cd] * InstalarCD[(cd)].value() for cd in Centros_Distribuicao)
custos_operacionais = sum(Custo_Operacao[(int(cd)-1)] * InstalarCD[(cd)].value() for cd in Centros_Distribuicao)
custos_transporte1 = sum(Distancia_Fornecedor_CD[(fornecedor, cd)] * Custo_Transporte[(tipo_carga,capacidade)] * VeiculosFornecedorCD[(fornecedor, cd, tipo_carga)].value()* capacidade
            for fornecedor in Fornecedores for cd in Centros_Distribuicao for tipo_carga in Tipos_Carga) 
custos_transporte2 = sum(Distancia_CD_Base[(cd, base)] * Custo_Transporte[(tipo_carga,capacidade )] * VeiculosCDBase[(cd, base, tipo_carga)].value() * capacidade
            for cd in Centros_Distribuicao for base in Bases_Logisticas for tipo_carga in Tipos_Carga)
custo_total = custos_fixos + custos_operacionais + custos_transporte1 + custos_transporte2

# Impressao dos resultados de cada cenario
print("Cenario", cenario)
print("  Numero de CDs Abertos:", numero_cds_abertos)
print("  Custos de Funcionamento:", custos_fixos)
print("  Custos Operacionais:", custos_operacionais)
print("  Custos Transporte (1):", custos_transporte1)
print("  Custos Transporte (2):", custos_transporte2)
print("  Custo Total:", custo_total)

# Atualização no Excel (assumindo que as variaveis de saída no edit data estão configuradas)
Numero_CDs_Abertos[cenario] = numero_cds_abertos
Custos_Fixos[cenario] = custos_fixos
for cd in Centros_Distribuicao:
    InstalarCD_Output[(cenario, cd)] = InstalarCD[(cd)].value() 
Custos_Operacionais[cenario] = custos_operacionais
Custos_Transporte1[cenario] = custos_transporte1
Custos_Transporte2[cenario] = custos_transporte2
Custo_Total[cenario] = custo_total

# Imprimir o custo total do objetivo no terminal
print("Objective (Custo Total):", pl.value(model.objective))
