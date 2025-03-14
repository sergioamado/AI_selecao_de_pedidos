from WarehouseCSP import WarehouseCSP
from csp import backtracking_search, min_conflicts, mac, mrv, lcv, first_unassigned_variable, unordered_domain_values, num_legal_values, no_inference
from heuristic import custom_heuristic

# 1. Definir Instância do Problema (usando o exemplo dado)
orders = [0, 1, 2, 3, 4]
items = [0, 1, 2, 3, 4]
corridors = [0, 1, 2, 3, 4]

units_per_order_item = {
    (0, 0): 3, (0, 2): 1,
    (1, 1): 1, (1, 3): 1,
    (2, 2): 1, (2, 4): 2,
    (3, 0): 1, (3, 2): 2, (3, 3): 1, (3, 4): 1,
    (4, 1): 1
}

units_per_corridor_item = {
    (0, 0): 2, (0, 1): 1, (0, 2): 1, (0, 4): 1,
    (1, 0): 2, (1, 1): 1, (1, 2): 2, (1, 4): 1,
    (2, 1): 2, (2, 4): 2, (2, 3): 1,
    (3, 0): 2, (3, 1): 1, (3, 3): 1, (3, 4): 1,
    (4, 1): 1, (4, 2): 2, (4, 3): 1, (4, 4): 2
}

LB = 5
UB = 12

# 2. Criar CSP
csp = WarehouseCSP(orders, items, corridors, units_per_order_item, units_per_corridor_item, LB, UB)

# 3. Resolver o CSP (Min Conflicts)
# Para conseguir um melhor resultado, o min_conflicts foi usado com uma heurística
# customizada.
print("\n--- Resolvendo com Min Conflicts ---")
solution_min_conflicts = min_conflicts(csp, max_steps=1000, heuristic=custom_heuristic)

if solution_min_conflicts is None:
    print("Nao encontrou solucao com Min Conflicts")
else:
    # 5. Analisar e Imprimir a Solução
    wave_orders = [order for order, include in solution_min_conflicts.items() if include]
    is_valid, selected_corridors = csp.is_wave_valid(wave_orders)

    if is_valid:
        objective_value = csp.objective_function(wave_orders, selected_corridors)
        print("Wave de pedidos:", wave_orders)
        print("Corredores selecionados:", selected_corridors)
        print("Valor objetivo:", objective_value)
    else:
        print("Nenhuma solução viável encontrada com Min Conflicts.")

def conflict(csp, var, val, assignment):
    """Return the number of conflicts var=val has with other variables."""
    
    def get_wave_orders(assignment):
        return [order for order, include in assignment.items() if include]
    
    def is_valid_state(assignment):
        wave_orders = get_wave_orders(assignment)
        is_valid, selected_corridors = csp.is_wave_valid(wave_orders)
        return is_valid
    
    temp_assignment = assignment.copy()
    temp_assignment[var] = val
    
    return not is_valid_state(temp_assignment)

# 4. Resolver o CSP (Backtracking Search)
#   * É importante resetar os domínios da CSP
print("\n--- Resolvendo com Backtracking Search ---")

csp.curr_domains = None  # Resetando os domínios

def lcv_backtracking(var, assignment, csp):
        return sorted(csp.choices(var), key=lambda val: conflict(csp, var, val, assignment))
solution_backtracking = backtracking_search(csp,
                                            select_unassigned_variable=mrv,
                                            order_domain_values=lcv_backtracking,
                                            inference=mac)

if solution_backtracking is None:
    print("Nao encontrou solucao com Backtracking Search")
else:
    # 5. Analisar e Imprimir a Solução
    wave_orders = [order for order, include in solution_backtracking.items() if include]
    is_valid, selected_corridors = csp.is_wave_valid(wave_orders)

    if is_valid:
        objective_value = csp.objective_function(wave_orders, selected_corridors)
        print("Wave de pedidos:", wave_orders)
        print("Corredores selecionados:", selected_corridors)
        print("Valor objetivo:", objective_value)
    else:
        print("Nenhuma solução viável encontrada com Backtracking Search.")