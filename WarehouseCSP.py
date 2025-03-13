#WarehouseCSP.py
from csp import CSP, AC3, backtracking_search
import itertools

def restricao_tamanho_wave(wave, lb, ub, uoi):
    """
    Verifica se o tamanho da wave (número total de itens) está dentro dos limites.

    Args:
        wave (dict): Um dicionário onde as chaves são os pedidos e os valores são booleanos (True se o pedido está na wave, False caso contrário).
        lb (int): Limite inferior para o número total de itens na wave.
        ub (int): Limite superior para o número total de itens na wave.
        uoi (list of lists): Uma matriz onde uoi[o][i] é o número de unidades do item i solicitado pelo pedido o.

    Returns:
        bool: True se a restrição for satisfeita, False caso contrário.
    """
    total_itens = 0
    for o in wave:  # Itera sobre os pedidos
        if wave[o]:  # Se o pedido está na wave
            for i in range(len(uoi[o])):  # Itera sobre os itens do pedido
                total_itens += uoi[o][i]
    print(f"restricao_tamanho_wave: total_itens={total_itens}, lb={lb}, ub={ub}")  #linha para depuração
    return lb <= total_itens <= ub

def restricao_capacidade_corredores(wave, corredores, uoi, uai):
    """
    Verifica se os corredores selecionados têm capacidade suficiente para atender à demanda por cada item na wave.

    Args:
        wave (dict): Um dicionário onde as chaves são os pedidos e os valores são booleanos (True se o pedido está na wave, False caso contrário).
        corredores (dict): Um dicionário onde as chaves são os corredores e os valores são booleanos (True se o corredor é usado, False caso contrário).
        uoi (list of lists): Uma matriz onde uoi[o][i] é o número de unidades do item i solicitado pelo pedido o.
        uai (list of lists): Uma matriz onde uai[a][i] é o número de unidades do item i disponível no corredor a.

    Returns:
        bool: True se a restrição for satisfeita, False caso contrário.
    """
    num_itens = len(uai[0]) # Descobre o número de itens
    for i in range(num_itens):  # Para cada item
        demanda_total = 0
        for o in wave:  # Para cada pedido
            if wave[o]:  # Se o pedido está na wave
                demanda_total += uoi[o][i] # Adiciona a demanda do item i para este pedido

        oferta_total = 0
        for a in corredores: # Para cada corredor
            if corredores[a]:  # Se o corredor está sendo usado
                oferta_total += uai[a][i] # Adiciona a oferta do item i neste corredor
        print(f"restricao_capacidade_corredores: item={i}, demanda={demanda_total}, oferta={oferta_total}")  # Linha para depuração

        if demanda_total > oferta_total:
            return False  # Se a demanda excede a oferta, a restrição não é satisfeita

    return True

def restricao_coerencia_pedidos_corredores(wave, corredores, uoi, uai):
    """
    Garante que, se um pedido está na wave, pelo menos um corredor que contenha algum dos itens desse pedido seja selecionado.

    Args:
        wave (dict): Um dicionário onde as chaves são os pedidos e os valores são booleanos (True se o pedido está na wave, False caso contrário).
        corredores (dict): Um dicionário onde as chaves são os corredores e os valores são booleanos (True se o corredor é usado, False caso contrário).
        uoi (list of lists): Uma matriz onde uoi[o][i] é o número de unidades do item i solicitado pelo pedido o.
        uai (list of lists): Uma matriz onde uai[a][i] é o número de unidades do item i disponível no corredor a.

    Returns:
        bool: True se a restrição for satisfeita, False caso contrário.
    """
    for o in wave:  # Para cada pedido
        if wave[o]:  # Se o pedido está na wave
            itens_do_pedido = [i for i in range(len(uoi[o])) if uoi[o][i] > 0] # Lista os itens do pedido
            corredor_atende_pedido = False
            for a in corredores: # Para cada corredor
                if corredores[a]: # Se o corredor está selecionado
                    for item in itens_do_pedido:
                        if uai[a][item] > 0: #se o corredor possui o item
                            corredor_atende_pedido = True
                            break
                if corredor_atende_pedido:
                    break
            print(f"restricao_coerencia_pedidos_corredores: pedido={o}, corredor_atende_pedido={corredor_atende_pedido}")  # Linha para depuração
            if not corredor_atende_pedido:
                return False  # Nenhum corredor atende o pedido

    return True

def valor_objetivo(wave, corredores, uoi):
    """
    Calcula o valor objetivo: número de itens coletados por corredor visitado.

    Args:
        wave (dict): Um dicionário onde as chaves são os pedidos e os valores são booleanos (True se o pedido está na wave, False caso contrário).
        corredores (dict): Um dicionário onde as chaves são os corredores e os valores são booleanos (True se o corredor é usado, False caso contrário).
        uoi (list of lists): Uma matriz onde uoi[o][i] é o número de unidades do item i solicitado pelo pedido o.

    Returns:
        float: O valor objetivo.
    """
    total_itens = 0
    for o in wave:
        if wave[o]:
            for i in range(len(uoi[o])):
                total_itens += uoi[o][i]

    num_corredores = sum(1 for a in corredores if corredores[a])

    if num_corredores == 0:
        return 0  # Evita divisão por zero

    return total_itens / num_corredores

class WarehouseCSP(CSP):
    def __init__(self, pedidos, itens, corredores, uoi, uai, lb, ub):
        self.pedidos = pedidos
        self.itens = itens
        self.corredores = corredores
        self.uoi = uoi
        self.uai = uai
        self.lb = lb
        self.ub = ub

        # Defina as variáveis do CSP
        variables = []
        for pedido in self.pedidos:
            variables.append(f'wave_{pedido}')
        for corredor in self.corredores:
            variables.append(f'corredor_{corredor}')
        self.variables = variables

        # Defina os domínios das variáveis
        domains = {}
        for variable in self.variables:
            if 'wave' in variable:
                domains[variable] = [0, 1]  # Domínio binário
            elif 'corredor' in variable:
                domains[variable] = [0, 1]  # Domínio binário
        self.domains = domains

        # Defina os vizinhos
        self.neighbors = self.define_neighbors()

        # Chame o construtor da classe pai (CSP)
        CSP.__init__(self, self.variables, self.domains, self.neighbors, self.constraints)

    def define_neighbors(self):
        """
        Define os vizinhos de cada variável.  Para este problema, consideramos que todas as variáveis
        são vizinhas umas das outras, pois a escolha de um pedido afeta a necessidade de corredores
        e vice-versa.

        Retorna:
            dict: Um dicionário onde as chaves são as variáveis e os valores são conjuntos de vizinhos.
        """
        neighbors = {}
        for var in self.variables:
            neighbors[var] = set(self.variables) - {var}  # Todos são vizinhos
        return neighbors

    def constraints(self, A, a, B, b):
        """
        Implementa as restrições do problema.

        Args:
            A (str): Nome da variável A.
            a (bool): Valor atribuído à variável A.
            B (str): Nome da variável B.
            b (bool): Valor atribuído à variável B.

        Retorna:
            bool: True se a restrição for satisfeita, False caso contrário.
        """

        # Se as variáveis são as mesmas, não há restrição para verificar
        if A == B:
            return True

        # Cria um dicionário de atribuições com as duas variáveis sendo verificadas
        assignment = {A: a, B: b}

        # Extrai as informações sobre os pedidos e corredores das variáveis
        wave = {}
        for pedido in self.pedidos:
            wave_key = f'wave_{pedido}'
            if wave_key in assignment:
                wave[pedido] = assignment[wave_key]
            else:
                wave[pedido] = 0

        corredores = {}
        for corredor in self.corredores:
            corredor_key = f'corredor_{corredor}'
            if corredor_key in assignment:
                corredores[corredor] = assignment[corredor_key]
            else:
                corredores[corredor] = 0

        print(f"constraints: A={A}, a={a}, B={B}, b={b}")
        print(f"constraints: wave={wave}, corredores={corredores}")  # Linha para depuração
        # Aplica as restrições
        if not restricao_tamanho_wave(wave, self.lb, self.ub, self.uoi):
            return False

        if not restricao_capacidade_corredores(wave, corredores, self.uoi, self.uai):
            return False

        if not restricao_coerencia_pedidos_corredores(wave, corredores, self.uoi, self.uai):
            return False

        return True

# Dados de Exemplo (Substitua com seus dados reais!)
pedidos = [0, 1, 2, 3, 4]  # IDs dos pedidos
itens = [0, 1, 2, 3, 4]  # IDs dos itens
corredores = [0, 1, 2, 3, 4]  # IDs dos corredores
uoi = [  # Unidades do item i no pedido o
    [3, 0, 1, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 2],
    [1, 0, 2, 1, 1],
    [0, 1, 0, 0, 0]
]
uai = [  # Unidades do item i no corredor a
    [2, 1, 1, 0, 1],
    [2, 1, 2, 0, 1],
    [0, 2, 0, 1, 2],
    [2, 1, 0, 1, 1],
    [0, 1, 2, 1, 2]
]
lb = 5  # Limite inferior do tamanho da wave
ub = 12 # Limite superior do tamanho da wave

# Crie uma instância do CSP
warehouse_csp = WarehouseCSP(pedidos, itens, corredores, uoi, uai, lb, ub)

# Resolva o CSP usando backtracking_search
solution = backtracking_search(warehouse_csp)

# Imprima a solução
if solution:
    print("Solução encontrada:")
    print(solution)

    # Avalie a solução (calcule o valor objetivo)
    wave = {int(var.split('_')[1]): solution[var] for var in solution if var.startswith('wave_')}
    corredores = {int(var.split('_')[1]): solution[var] for var in solution if var.startswith('corredor_')}
    valor = valor_objetivo(wave, corredores, uoi)
    print(f"Valor objetivo: {valor}")
else:
    print("Nenhuma solução encontrada.")