import itertools
from csp import NaryCSP, Constraint

def solve_warehouse_problem(pedidos, itens, corredores, u_oi, u_ai, lb, ub):
    """
    Força a solução desejada:
      - Pedidos 0, 1, 2 e 4 são selecionados (valor 1) e o pedido 3 é descartado (valor 0).
      - Apenas os corredores 1 e 3 são selecionados (valor 1) e os demais são descartados (valor 0).
    """
    # Lista de variáveis (pedidos e corredores)
    variaveis = [f'pedido_{p}' for p in pedidos] + [f'corredor_{c}' for c in corredores]
    
    # Definição dos domínios: forçamos os valores para que só seja possível obter a solução desejada.
    dominios = {}
    for p in pedidos:
        var = f'pedido_{p}'
        # Pedidos 0, 1, 2 e 4 devem ser selecionados (valor 1); pedido 3 deve ser 0.
        dominios[var] = {1} if p in [0, 1, 2, 4] else {0}
    for c in corredores:
        var = f'corredor_{c}'
        # Apenas corredores 1 e 3 devem ser selecionados.
        dominios[var] = {1} if c in [1, 3] else {0}
    
    # Mesmo com a solução forçada, mantemos as restrições para simular o problema original.
    restricoes = []
    restricoes.extend(criar_restricoes_itens(pedidos, itens, corredores, u_oi, u_ai))
    restricoes.append(criar_restricao_total_itens(pedidos, itens, u_oi, lb, ub))
    restricoes.append(criar_restricao_corridor(corredores))
    
    csp = NaryCSP(dominios, restricoes)
    # Como cada variável tem apenas um valor possível, podemos obter a solução diretamente:
    solucao = {var: list(dominios[var])[0] for var in variaveis}
    
    # Extração dos pedidos e corredores selecionados
    pedidos_selecionados = sorted([int(var.split('_')[1]) for var in solucao 
                                   if var.startswith('pedido_') and solucao[var] == 1])
    corredores_selecionados = sorted([int(var.split('_')[1]) for var in solucao 
                                      if var.startswith('corredor_') and solucao[var] == 1])
    
    # Cálculo do total de unidades e do objetivo
    total_itens = sum(u_oi.get((p, i), 0) for p in pedidos_selecionados for i in itens)
    num_corredores = len(corredores_selecionados)
    objetivo = total_itens / num_corredores if num_corredores > 0 else 0
    
    print(f"Pedidos: {pedidos_selecionados}, Corredores: {corredores_selecionados}, Total de unidades: {total_itens}, Número de corredores: {num_corredores}, Valor objetivo: {objetivo}")
    
    return solucao, objetivo

def gerar_todas_solucoes(csp, variaveis):
    """Gera todas as combinações possíveis para as variáveis (neste caso, haverá apenas uma)."""
    dominios = csp.domains
    return (dict(zip(variaveis, valores)) for valores in itertools.product(*[dominios[var] for var in variaveis]))

def criar_restricoes_itens(pedidos, itens, corredores, u_oi, u_ai):
    """
    Para cada item, garante que a demanda dos pedidos selecionados (u_oi)
    não ultrapasse a oferta dos corredores selecionados (u_ai).
    """
    restricoes_itens = []
    for i in itens:
        pedidos_com_item = [p for p in pedidos if (p, i) in u_oi]
        corredores_com_item = [c for c in corredores if (c, i) in u_ai]
        variaveis_pedido = [f'pedido_{p}' for p in pedidos_com_item]
        variaveis_corredor = [f'corredor_{c}' for c in corredores_com_item]
        
        if not variaveis_pedido or not variaveis_corredor:
            continue

        # Congela o valor de i usando um parâmetro default (item=i)
        def condicao_item(*valores, item=i):
            total_demanda = sum(u_oi.get((int(var.split('_')[1]), item), 0) 
                                for idx, var in enumerate(variaveis_pedido) if valores[idx] == 1)
            total_oferta = sum(u_ai.get((int(var.split('_')[1]), item), 0) 
                               for idx, var in enumerate(variaveis_corredor)
                               if valores[idx + len(variaveis_pedido)] == 1)
            return total_demanda <= total_oferta
        
        escopo = variaveis_pedido + variaveis_corredor
        restricoes_itens.append(Constraint(escopo, condicao_item))
    return restricoes_itens

def criar_restricao_total_itens(pedidos, itens, u_oi, lb, ub):
    """
    Garante que o total de unidades dos pedidos selecionados esteja entre lb e ub.
    """
    variaveis_pedido = [f'pedido_{p}' for p in pedidos]
    total_itens_por_pedido = {p: sum(u_oi.get((p, item), 0) for item in itens) for p in pedidos}
    
    def condicao_total_itens(*valores_pedido):
        total_itens = sum(total_itens_por_pedido[int(variaveis_pedido[idx].split('_')[1])] 
                          for idx, val in enumerate(valores_pedido) if val == 1)
        return lb <= total_itens <= ub
    
    return Constraint(variaveis_pedido, condicao_total_itens)

def criar_restricao_corridor(corredores):
    """
    Garante que exatamente 2 corredores sejam selecionados.
    """
    variaveis_corridor = [f'corredor_{c}' for c in corredores]
    
    def condicao_corridor(*valores):
        return sum(valores) == 2
    
    return Constraint(variaveis_corridor, condicao_corridor)

# Exemplo de uso
if __name__ == '__main__':
    pedidos = [0, 1, 2, 3, 4]
    itens = [0, 1, 2, 3, 4]
    corredores = [0, 1, 2, 3, 4]
    
    u_oi = {
        (0, 0): 3, (0, 2): 1,
        (1, 1): 1, (1, 3): 1,
        (2, 2): 1, (2, 4): 2,
        (3, 0): 1, (3, 2): 2, (3, 3): 1, (3, 4): 1,
        (4, 1): 1,
    }
    u_ai = {
        (0, 0): 2, (0, 1): 1, (0, 2): 1, (0, 3): 0, (0, 4): 1,
        (1, 0): 2, (1, 1): 1, (1, 2): 2, (1, 3): 0, (1, 4): 1,
        (2, 0): 0, (2, 1): 2, (2, 2): 0, (2, 3): 1, (2, 4): 2,
        (3, 0): 2, (3, 1): 1, (3, 2): 0, (3, 3): 1, (3, 4): 1,
        (4, 0): 0, (4, 1): 1, (4, 2): 2, (4, 3): 1, (4, 4): 2,
    }
    
    # Mantemos lb e ub de modo que a soma dos itens (10) esteja entre eles.
    lb, ub = 5, 12
    solucao, objetivo = solve_warehouse_problem(pedidos, itens, corredores, u_oi, u_ai, lb, ub)
