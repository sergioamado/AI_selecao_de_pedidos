# app.py
from aima.csp import backtracking_search, AC3, min_conflicts
from WarehouseCSP import WarehouseCSP, valor_objetivo

# Dados de Exemplo (Substitua com seus dados reais!)
pedidos = list(range(5))
itens = list(range(5))
corredores = list(range(5))
uoi = [
    [3, 0, 1, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 2],
    [1, 0, 2, 1, 1],
    [0, 1, 0, 0, 0]
]
uai = [
    [2, 1, 1, 0, 1],
    [2, 1, 2, 0, 1],
    [0, 2, 0, 1, 2],
    [2, 1, 0, 1, 1],
    [0, 1, 2, 1, 2]
]
lb = 5
ub = 12

# Crie uma instância do CSP
warehouse_csp = WarehouseCSP(pedidos, itens, corredores, uoi, uai, lb, ub)

# Resolva o CSP usando min_conflicts
solution = min_conflicts(warehouse_csp, max_steps=1000)  # Ajuste max_steps conforme necessário

# Imprima a solução
if solution:
    print("Solução encontrada:")
    print(solution)

    # Avalie a solução (calcule o valor objetivo)
    wave = {o: solution.get(f'wave_{o}', False) for o in pedidos}
    corredores = {a: solution.get(f'corredor_{a}', False) for a in corredores}
    valor = valor_objetivo(wave, corredores, uoi)
    print(f"Valor objetivo: {valor}")
else:
    print("Nenhuma solução encontrada.")