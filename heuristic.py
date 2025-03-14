def custom_heuristic(csp, var, value, assignment):
    """
    Heurística customizada para o problema do armazém.
    Prioriza waves que utilizem menos corredores e maximizem a quantidade de itens.

    Args:
        csp: O CSP do armazém.
        var: Variável sendo avaliada (um pedido).
        value: Valor sendo atribuído à variável (True ou False).
        assignment: Atribuição parcial atual.

    Returns:
        Um valor numérico que representa a qualidade da atribuição.
    """

    # Criar uma wave temporária com a nova atribuição
    temp_assignment = assignment.copy()
    temp_assignment[var] = value
    wave_orders = [order for order, include in temp_assignment.items() if include]

    # Verificar se a wave é válida
    is_valid, selected_corridors = csp.is_wave_valid(wave_orders)

    if not is_valid:
        return float('inf')  # Penalizar atribuições inválidas

    # Calcular a função objetivo
    objective = csp.objective_function(wave_orders, selected_corridors)

    # Penalizar o uso de mais corredores
    num_corridors = len(selected_corridors)
    corridor_penalty = 0.5 * num_corridors  # Aumentei a penalidade!

    # Combinação da função objetivo e da penalidade (minimizar a combinação)
    heuristic_value = -objective + corridor_penalty  # Maximiza o objetivo, minimiza corredores

    return heuristic_value