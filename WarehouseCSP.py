from collections import defaultdict
from itertools import combinations
from csp import CSP, NaryCSP, Constraint

class WarehouseCSP(CSP):  # Problema Binário

    def __init__(self, orders, items, corridors, units_per_order_item, units_per_corridor_item, LB, UB):
        """
        Cria um CSP para o problema de seleção de pedidos em waves.

        Args:
            orders: Lista de identificadores de pedidos (ex: [0, 1, 2, 3, 4]).
            items: Lista de identificadores de itens (ex: [0, 1, 2, 3, 4]).
            corridors: Lista de identificadores de corredores (ex: [0, 1, 2, 3, 4]).
            units_per_order_item: Dicionário {(pedido, item): quantidade}
            units_per_corridor_item: Dicionário {(corredor, item): quantidade}
            LB: Limite inferior do tamanho da wave.
            UB: Limite superior do tamanho da wave.
        """

        self.orders = orders
        self.items = items
        self.corridors = corridors
        self.units_per_order_item = units_per_order_item
        self.units_per_corridor_item = units_per_corridor_item
        self.LB = LB
        self.UB = UB

        # Variáveis: Cada pedido é uma variável (incluir ou não na wave)
        variables = orders

        # Domínios: True (incluir) ou False (não incluir)
        domains = {order: [True, False] for order in orders}

        # Vizinhos: Todos os pares de pedidos são vizinhos (restrições n-árias)
        neighbors = {order: [other_order for other_order in orders if other_order != order] for order in orders}

        super().__init__(variables, domains, neighbors, self.constraints)

    def constraints(self, A, a, B, b): # A e B são pedidos, a e b são True/False
        """
        Define as restrições do CSP.
        Neste caso, como a lógica principal é complexa e envolve todos os pedidos,
        usaremos uma restrição "global" n-ária.
        """
        return True  # Devolvemos sempre True aqui, porque a restrição real é tratada no método is_wave_valid.

    def is_wave_valid(self, wave_orders):
        """
        Verifica se uma wave de pedidos é válida, considerando as restrições do problema.
        Retorna um tuplo (valid, selected_corridors), onde:
            - valid: True se a wave for válida, False caso contrário.
            - selected_corridors: Lista de corredores selecionados para a wave (ou None se inválida).
        """

        # 1. Calcular o total de unidades na wave
        total_units = sum(self.units_per_order_item.get((order, item), 0)
                         for order in wave_orders
                         for item in self.items)

        # 2. Verificar restrições de tamanho da wave
        if not (self.LB <= total_units <= self.UB):
            return False, None

        # 3. Determinar corredores necessários para atender à wave
        required_corridors_per_item = {}  # item: set(corredores)
        for item in self.items:
            required_corridors_per_item[item] = set()
            for order in wave_orders:
                if self.units_per_order_item.get((order, item), 0) > 0:
                    for corridor in self.corridors:
                        if self.units_per_corridor_item.get((corridor, item), 0) > 0:
                            required_corridors_per_item[item].add(corridor)

        # 4. Otimizar a seleção de corredores (aqui pode ser simplificado, por ora, selecionando todos os necessários)
        selected_corridors = set()
        for item in self.items:
            selected_corridors.update(required_corridors_per_item[item])

        selected_corridors = list(selected_corridors)

        # 5. Verificar restrição de capacidade dos corredores
        for item in self.items:
             total_item_demand = sum(self.units_per_order_item.get((order, item), 0)
                                     for order in wave_orders)
             total_item_supply = sum(self.units_per_corridor_item.get((corridor, item), 0)
                                     for corridor in selected_corridors)
             if total_item_demand > total_item_supply:
                 return False, None

        return True, selected_corridors

    def objective_function(self, wave_orders, selected_corridors):
        """Calcula a função objetivo: número de itens coletados por corredor visitado."""
        total_units = sum(self.units_per_order_item.get((order, item), 0)
                         for order in wave_orders
                         for item in self.items)

        num_corridors = len(selected_corridors)
        if num_corridors == 0:
            return 0  # Evitar divisão por zero
        return total_units / num_corridors