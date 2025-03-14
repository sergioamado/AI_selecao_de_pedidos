# min_conflicts.py
import random

def min_conflicts(csp, max_steps=1000):
    """
    Implementação do algoritmo de busca Min-Conflicts.
    """

    # Atribuição inicial aleatória
    current = {}
    for var in csp.variables:
        current[var] = random.choice(csp.domains[var])

    for i in range(max_steps):
        if is_solution(csp, current):
            return current  # Solução encontrada

        # Escolhe uma variável com conflito aleatoriamente
        conflicted = conflicted_vars(csp, current)
        if not conflicted:
            return current  # Solução encontrada (sem conflitos)

        var = random.choice(conflicted)

        # Escolhe um valor para a variável que minimize os conflitos
        value = choose_min_conflict_value(csp, var, current, csp)
        current[var] = value

    return None  # Não encontrou solução dentro do número máximo de passos

def is_solution(csp, assignment):
    """Verifica se a atribuição é uma solução válida para o CSP."""
    for var1 in csp.variables:
        for var2 in csp.neighbors[var1]:
            if var2 in assignment:
                if not csp.constraints(var1, assignment[var1], var2, assignment[var2]):
                    return False
    return True

def conflicted_vars(csp, assignment):
    """
    Retorna uma lista de variáveis que estão em conflito.
    """
    conflicted = []
    for var in csp.variables:
        if num_conflicts(csp, var, assignment, csp) > 0:
            conflicted.append(var)
    return conflicted

def num_conflicts(csp, var, assignment, warehouse_csp):
    """
    Retorna o número de restrições que a variável viola com a atribuição atual.
    """
    conflicts = 0
    for neighbor in warehouse_csp.neighbors[var]:
        if neighbor in assignment:
            if not warehouse_csp.constraints(var, assignment[var], neighbor, assignment[neighbor]):
                conflicts += 1
    return conflicts

def choose_min_conflict_value(csp, var, current, warehouse_csp):
    """
    Escolhe um valor para a variável que minimize o número de conflitos.
    """
    min_conflicts_value = None
    min_conflicts_count = float('inf')

    for value in csp.domains[var]:
        assignment_copy = current.copy()
        assignment_copy[var] = value
        conflicts = 0
        for neighbor in csp.neighbors[var]:
            if neighbor in assignment_copy:
                if not warehouse_csp.constraints(var, assignment_copy[var], neighbor, assignment_copy[neighbor]):
                    conflicts += 1

        if conflicts < min_conflicts_count:
            min_conflicts_count = conflicts
            min_conflicts_value = value

    return min_conflicts_value