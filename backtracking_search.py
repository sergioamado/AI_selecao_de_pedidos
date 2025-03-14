# backtracking_search.py
def backtracking_search(csp):
    """
    Implementa o algoritmo de busca de backtracking.

    Args:
        csp: Um objeto CSP (Constraint Satisfaction Problem).

    Returns:
        Uma atribuição (dicionário) que representa uma solução, ou None se falhar.
    """

    def backtrack(assignment):
        """
        Função recursiva para realizar a busca de backtracking.

        Args:
            assignment: Um dicionário que representa a atribuição atual.

        Returns:
            Uma atribuição (dicionário) que representa uma solução, ou None se falhar.
        """
        if len(assignment) == len(csp.variables):
            return assignment  # Atribuição completa

        # Escolher a variável a ser atribuída
        var = select_unassigned_variable(csp, assignment)

        for value in order_domain_values(csp, var, assignment):
            if is_consistent(csp, var, value, assignment, csp):
                assignment[var] = value
                # inferencias = inference(csp, var, assignment) # remover a inferencia

                # if inferencias != "falha": # remover a inferencia
                    # for k, v in inferencias.items():# remover a inferencia
                    #    csp.domains[k] = [v]# remover a inferencia

                result = backtrack(assignment.copy())  # Passa uma cópia da atribuição
                if result is not None:
                    return result  # Solução encontrada

                # Remove a atribuição (backtrack)
                del assignment[var]
                # for k in inferencias.keys(): # remover a inferencia
                #    csp.domains[k] = revert_domain(k) # remover a inferencia

        return None  # Sem solução

    def select_unassigned_variable(csp, assignment):
        """
        Heurística para selecionar a próxima variável a ser atribuída.
        Implementa a heurística MRV (Minimum Remaining Values).
        """
        unassigned_vars = [var for var in csp.variables if var not in assignment]
        if not unassigned_vars:
            return None  # Todas as variáveis foram atribuídas

        return min(unassigned_vars, key=lambda var: len(csp.domains[var]))

    def order_domain_values(csp, var, assignment):
        """
        Ordena os valores do domínio de uma variável.
        Neste caso, retorna os valores sem nenhuma ordem específica.
        """
        return csp.domains[var]

    def is_consistent(csp, variable, value, assignment, warehouse_csp):
        """Verifica se a atribuição é consistente com as restrições."""
        assignment[variable] = value
        for neighbor in warehouse_csp.neighbors[variable]:
            if neighbor in assignment:
                if not warehouse_csp.constraints(variable, value, neighbor, assignment[neighbor]):
                    return False
        return True

    def inference(csp, var, assignment):
        """
        Função de inferência (stub).
        """
        return {}

    def revert_domain(csp,var):
        return csp.domains[var]

    # Inicia a busca com uma atribuição vazia
    return backtrack({})