from csp import CSP, min_conflicts, backtracking_search
import time
#from heuristic import custom_heuristic
#função que não sera mais necessaria

def total_units_in_wave(assignment, orders, variables):
    """Calcula o total de unidades em uma wave."""
    return sum(
        sum(orders[o][i] for i in orders[o])
        for o in variables if assignment.get(o, False)  # Use get com valor padrão
    )


class WarehouseCSP(CSP):
    """
    Modelagem do problema de seleção de pedidos em waves como um CSP.
    """

    def __init__(self, orders, items, corridor_items, LB, UB):
        """
        Construtor do CSP.

        Args:
            orders (dict): Dicionário de pedidos (order_id: items).
            items (dict): Dicionário de itens (item_id: corridors).
            corridor_items (dict): Dicionário de corredores (corridor_id: {item_id: quantity}).
            LB (int): Limite inferior para o tamanho da wave.
            UB (int): Limite superior para o tamanho da wave.
        """
        self.orders = orders
        self.items = items
        self.corridor_items = corridor_items
        self.LB = LB
        self.UB = UB

        # Variáveis: Cada pedido é uma variável (incluir ou não na wave)
        variables = list(orders.keys())

        # Domínios: Cada variável pode ser True (incluir ou não incluir)
        domains = {order_id: [True, False] for order_id in variables}

        # Vizinhos: Todos os pedidos são vizinhos entre si (restrições podem envolver qualquer combinação de pedidos)
        neighbors = {order_id: [v for v in variables if v != order_id] for order_id in variables}

        super().__init__(variables, domains, neighbors, self.constraints)

    def constraints(self, order1, include1, order2, include2, assignment=None):
        """
        Define as restrições do CSP.

        Args:
            order1 (int): ID do primeiro pedido.
            include1 (bool): Indica se o primeiro pedido está na wave.
            order2 (int): ID do segundo pedido.
            include2 (bool): Indica se o segundo pedido está na wave.
            assignment (dict, optional): Atribuição parcial atual. Defaults to None.

        Returns:
            bool: True se a atribuição for consistente, False caso contrário.
        """

        # Cria uma atribuição completa combinando a atribuição parcial com os valores atuais sendo testados
        complete_assignment = {order1: include1, order2: include2}  # Começa com os dois pedidos que estamos avaliando
        if assignment:
            complete_assignment.update(assignment)  # Adiciona a atribuição parcial existente
#wave_orders = [order for order, include in complete_assignment.items() if include]
        # 1. Calcula o total de unidades na wave
        total_units = total_units_in_wave(complete_assignment, self.orders, self.variables)

        # 2. Verifica se os limites da wave são respeitados
        #if total_units < self.LB or total_units > self.UB:
        #    #print(f"Restrição de tamanho da wave falhou: total_units={total_units}, LB={self.LB}, UB={self.UB}")
        #    return False
        
        #wave_orders = [order for order, include in complete_assignment.items() if include]

        # 3. Calcula o conjunto de corredores utilizados pela wave
        wave_items = {}
        for order in self.variables:
            if complete_assignment.get(order, False) == True:  # Usar get para evitar KeyError
                for item, quantity in self.orders[order].items():
                    if item in wave_items:
                        wave_items[item] += quantity
                    else:
                        wave_items[item] = quantity
        #print ("wave_items: ", wave_items)

        corridors = set()
        for item in wave_items:
            corridors.update(self.items[item])
        #print ("corredores: ",corridors)

        # 4. Verifica se há capacidade suficiente nos corredores selecionados
        for item, quantity in wave_items.items():
            total_capacity = sum(self.corridor_items[corridor].get(item, 0) for corridor in corridors)
            if quantity > total_capacity:
                #print(f"Restrição de capacidade falhou: item={item}, quantity={quantity}, total_capacity={total_capacity}")
                return False  # Se não tem capacidade retorna falso

        # 5 Imprimir resultados intermediários
        wave_orders = [order for order, include in complete_assignment.items() if include]
        print("Pedidos selecionados:", wave_orders)
        print("Total de unidades:", total_units)
        print("Número de corredores:", len(corridors))
        print("Valor Objetivo:", self.objective_function(complete_assignment))
        print("-------------------")

        return True
#método is_wave_valid não é necessário pois o console já apresenta o que se busca e já é usado no objecitve_function
#        return True, corridors #Retorna os corredores se a wave for válida

    def objective_function(self, assignment):
      """
      Calcula o valor da função objetivo para uma dada atribuição.
      """
      # Calcula o total de unidades na wave
      total_units = sum(
          sum(self.orders[o][i] for i in self.orders[o])
          for o in self.variables if assignment.get(o) == True
      )
      
      # Calcula o conjunto de corredores utilizados pela wave
      wave_items = {}
      for order in self.variables:
          if assignment.get(order) == True:
              for item, quantity in self.orders[order].items():
                  if item in wave_items:
                      wave_items[item] += quantity
                  else:
                      wave_items[item] = quantity

      corridors = set()
      for item in wave_items:
          corridors.update(self.items[item])

      # Calcula o valor objetivo
      if len(corridors) > 0:
          return total_units / len(corridors)
      else:
          return 0  # Retorna 0 se não houver corredores selecionados

    def display(self, assignment):
        """Exibe a solução de forma mais legível."""
        if assignment is None:
            print("Nenhuma solução encontrada.")
            return

        selected_orders = [order for order, include in assignment.items() if include]
        wave_items = {}
        for order in selected_orders:
            for item, quantity in self.orders[order].items():
                if item in wave_items:
                    wave_items[item] += quantity
                else:
                    wave_items[item] = quantity

        corridors = set()
        for item in wave_items:
            corridors.update(self.items[item])

        print("Pedidos selecionados:", selected_orders)
        print("Itens na wave:", wave_items)
        print("Corredores utilizados:", corridors)
        print("Valor Objetivo:", self.objective_function(assignment))
# heuristic.py
def custom_heuristic(var, value, assignment, csp):
    """
    Heurística customizada para o problema do armazém.
    Prioriza waves que utilizem menos corredores e maximiza a quantidade de itens.

    Args:
        csp: O CSP do armazém.
        var: Variável sendo avaliada (um pedido).
        value: Valor sendo atribuído à variável (True ou False).
        assignment: Atribuição parcial atual.

    Returns:
        Um valor numérico que representa a qualidade da atribuição.
    """

    # 1. Criar uma wave temporária com a nova atribuição
    temp_assignment = assignment.copy()
    temp_assignment[var] = value
    wave_orders = [order for order, include in temp_assignment.items() if include]

    # 2. Verificar se a wave é válida, utilizando o método is_wave_valid
    is_valid, selected_corridors = csp.is_wave_valid(wave_orders)
    #is_valid, selected_corridors = csp.is_wave_valid(wave_orders)

    if value and not is_valid:
        return float('inf')  # Penalizar atribuições inválidas

    # 3. Calcular a função objetivo
    objective = csp.objective_function(temp_assignment)

    # 4. Penalizar o uso de mais corredores
    num_corridors = len(selected_corridors)
    #corridor_penalty = 0.5 * num_corridors  # Aumentei a penalidade!

    # 5. Combinação da função objetivo e da penalidade (minimizar a combinação)
    heuristic_value = objective  # -objective + corridor_penalty  # Maximiza o objetivo, minimiza corredores
    print ( 'heuristic_value: ',heuristic_value, 'objective',objective, 'wave_orders', wave_orders)
    return heuristic_value