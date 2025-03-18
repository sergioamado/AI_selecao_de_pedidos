def custom_heuristic(var, value, assignment, csp):
    """
    Heurística customizada para o problema do armazém.
    Prioriza waves que utilizem menos corredores e maximiza a quantidade de itens.

    Args:
        var: Variável sendo avaliada (um pedido).
        value: Valor sendo atribuído à variável (True ou False).
        assignment: Atribuição parcial atual.
        csp: O CSP do armazém (instância de WarehouseCSP).

    Returns:
        Um valor numérico que representa a qualidade da atribuição.
    """

    # 1. Criar uma wave temporária com a nova atribuição
    temp_assignment = assignment.copy()
    temp_assignment[var] = value
    wave_orders = [order for order, include in temp_assignment.items() if include]

    # 2. Verificar se a wave é válida
    is_valid, selected_corridors = csp.is_wave_valid(wave_orders)

    # Penalizar atribuições inválidas
    if value and not is_valid:
        return float('inf')

    # Calcular a função objetivo
    objective = csp.objective_function(temp_assignment)

    # Penalizar o uso de mais corredores
    num_corridors = len(selected_corridors)
    corridor_penalty = 0.5 * num_corridors

    # Combinar a função objetivo e a penalidade (minimizar a combinação)
    heuristic_value = objective #-objective + corridor_penalty  # Maximize objective, minimize corridors

    print('heuristic_value: ', heuristic_value, 'objective', objective, 'corridor_penalty', corridor_penalty, 'wave_orders', wave_orders)
    return heuristic_value