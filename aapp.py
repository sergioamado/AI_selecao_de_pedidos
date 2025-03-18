from WarehouseCSP import WarehouseCSP
from csp import min_conflicts, backtracking_search
import time
from heuristic import custom_heuristic
from utils import first

# Definição do problema (Exemplo)
orders = {
    0: {0: 3, 2: 1},
    1: {1: 1, 3: 1},
    2: {2: 1, 4: 2},
    3: {0: 1, 2: 2, 3: 1, 4: 1},
    4: {1: 1}
}

items = {
    0: {0, 1, 3},
    1: {0, 1, 2, 3, 4},
    2: {0, 1, 4, 3},
    3: {1, 2, 3, 4},
    4: {2, 3, 4}
}

corridor_items = {
    0: {0: 2, 1: 1, 2: 1, 4: 1},
    1: {0: 2, 1: 1, 2: 2, 4: 1},
    2: {1: 2, 3: 1, 4: 2},
    3: {0: 2, 1: 1, 3: 1, 4: 1},
    4: {1: 1, 2: 2, 3: 1, 4: 2}
}

LB = 5
UB = 12

def run_csp(search_method="backtracking", custom = False, mrv = False, lcv = False, mac = False):
    """
    Função para executar o CSP com diferentes métodos de busca e exibir os resultados.
    """
    warehouse_csp = WarehouseCSP(orders, items, corridor_items, LB, UB)

    start_time = time.time()

    if search_method == "backtracking":
      if custom:
        def order_domain_function(var, assignment, csp):
            return sorted(csp.domains[var], key=lambda val: custom_heuristic(var, val, assignment,csp))

        solution = backtracking_search(warehouse_csp, order_domain_values=order_domain_function)

      elif (mrv and lcv and mac):
        solution = backtracking_search(warehouse_csp,order_domain_values=lcv, select_unassigned_variable=mrv, inference=mac)
      elif (mrv and lcv):
          solution = backtracking_search(warehouse_csp,order_domain_values=lcv, select_unassigned_variable=mrv)
      else:
        solution = backtracking_search(warehouse_csp)

    elif search_method == "min_conflicts":
        def min_conflicts_value(csp, var, current):
            """
            Retorna o valor que dará a var o menor número de conflitos, usando a heurística customizada.
            """
            return min(csp.domains[var], key=lambda val: custom_heuristic(var, val, current,csp))

        solution = min_conflicts(warehouse_csp)


    end_time = time.time()
    execution_time = end_time - start_time

    print("\n--- Resultados ---")
    print("Método de busca:", search_method)
    if (mrv and lcv and mac):
      print("otimizações:, MRV , LCV e MAC")
    elif (custom):
      print("otimizações:, Custom heuristic")
    elif (mrv and lcv):
       print("otimizações:, MRV e LCV")
    else:
      print("sem otimizações")
    
    print("Tempo de execução:", execution_time, "segundos")
    if solution:
      warehouse_csp.display(solution)
      print("Número de atribuições:", warehouse_csp.nassigns)
    else:
      print("Nenhuma solução encontrada")


# Execução com backtracking
print("Executando com Backtracking Search:")
#run_csp("backtracking")

# Execução com backtracking e heurística customizada
print("\nExecutando com Backtracking Search e heurística customizada:")
run_csp("backtracking", custom=True)

# Execução com min_conflicts
#print("\nExecutando com Min-Conflicts:")
#run_csp("min_conflicts")