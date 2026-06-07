import re

class Instruction:
    def __init__(self, raw_str, target=None, op=None, arg1=None, arg2=None, is_return=False):
        self.raw_str = raw_str       # Representação original da string
        self.target = target         # Variável de destino (string) ou None
        self.op = op                 # Operador (string) ou None
        self.arg1 = arg1             # Primeiro operando (var ou constante)
        self.arg2 = arg2             # Segundo operando (var, constante ou None)
        self.is_return = is_return   # Flag indicando se é retorno

    def copy(self):
        return Instruction(
            raw_str=self.raw_str,
            target=self.target,
            op=self.op,
            arg1=self.arg1,
            arg2=self.arg2,
            is_return=self.is_return
        )

    def __str__(self):
        if self.is_return:
            if self.arg1 is not None:
                return f"return {self._operand_str(self.arg1)}"
            return "return"
        elif self.op is not None:
            if self.arg2 is not None:
                return f"{self.target} = {self._operand_str(self.arg1)} {self.op} {self._operand_str(self.arg2)}"
            else:
                return f"{self.target} = {self.op} {self._operand_str(self.arg1)}"
        else:
            if self.target is not None:
                return f"{self.target} = {self._operand_str(self.arg1)}"
            return self._operand_str(self.arg1)

    def _operand_str(self, val):
        if isinstance(val, bool):
            return "True" if val else "False"
        return str(val)


def is_const(val):
    return isinstance(val, (int, float, bool))


def parse_val(val_str):
    val_str = val_str.strip()
    if val_str.lower() == 'true':
        return True
    if val_str.lower() == 'false':
        return False
    # Tenta int
    try:
        if val_str.startswith('+'):
            return int(val_str[1:])
        return int(val_str)
    except ValueError:
        pass
    # Tenta float
    try:
        return float(val_str)
    except ValueError:
        pass
    # Caso contrário, trata como variável
    return val_str


def parse_expression(expr_str):
    expr_str = expr_str.strip()
    
    # 1. Se for um valor simples (constante direta ou variável)
    if expr_str.lower() in ("true", "false"):
        return None, parse_val(expr_str), None
    if re.match(r'^[-+]?\d+$', expr_str):
        return None, int(expr_str), None
    if re.match(r'^[-+]?\d*\.\d+$', expr_str) or re.match(r'^[-+]?\d+\.\d*$', expr_str):
        return None, float(expr_str), None
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr_str):
        return None, expr_str, None

    # 2. Operadores binários ordenados para evitar casamento parcial indesejado
    operators = [
        "==", "!=", "<=", ">=", "//", "**",
        "+", "-", "*", "/", "%", "<", ">"
    ]
    
    for op in operators:
        # Encontra o operador que não seja um sinal unário
        idx = expr_str.find(op)
        while idx != -1:
            # Se for '-', verifica se é unário (está no começo ou logo após outro operador)
            if op == "-" and (idx == 0 or expr_str[:idx].strip() == "" or expr_str[:idx].strip()[-1] in "+-*/%<=!>&|"):
                idx = expr_str.find(op, idx + 1)
                continue
            
            left_str = expr_str[:idx].strip()
            right_str = expr_str[idx + len(op):].strip()
            
            if left_str and right_str:
                return op, parse_val(left_str), parse_val(right_str)
            
            idx = expr_str.find(op, idx + 1)

    # Operadores booleanos de texto com word boundaries
    for op in ["and", "or"]:
        pattern = rf"\b{op}\b"
        match = re.search(pattern, expr_str)
        if match:
            idx = match.start()
            left_str = expr_str[:idx].strip()
            right_str = expr_str[match.end():].strip()
            if left_str and right_str:
                return op, parse_val(left_str), parse_val(right_str)

    # 3. Operadores unários
    unary_ops = ["-", "not", "+"]
    for op in unary_ops:
        if op == "not":
            pattern = rf"^not\b\s*(.+)$"
            match = re.match(pattern, expr_str)
            if match:
                arg = parse_val(match.group(1).strip())
                return op, arg, None
        else:
            if expr_str.startswith(op):
                arg_str = expr_str[len(op):].strip()
                if arg_str:
                    return op, parse_val(arg_str), None

    # Fallback: se não identificar, assume atribuição direta
    return None, parse_val(expr_str), None


def parse_instructions(code_str):
    instructions = []
    lines = code_str.strip().split('\n')
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        try:
            # Caso return
            if line.startswith("return"):
                parts = line.split(None, 1)
                if len(parts) > 1:
                    arg = parse_val(parts[1])
                    instructions.append(Instruction(line, arg1=arg, is_return=True))
                else:
                    instructions.append(Instruction(line, is_return=True))
                continue
            
            # Caso atribuição normal
            if "=" not in line:
                # Trata como uma expressão sem destino, ou lança erro dependendo da rigidez
                arg = parse_val(line)
                instructions.append(Instruction(line, arg1=arg))
                continue

            target_str, expr_str = line.split("=", 1)
            target = target_str.strip()
            
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', target):
                raise ValueError(f"Nome de variável inválido: '{target}'")
                
            op, arg1, arg2 = parse_expression(expr_str)
            instructions.append(Instruction(line, target=target, op=op, arg1=arg1, arg2=arg2))
            
        except Exception as e:
            raise ValueError(f"Erro na linha {line_num}: '{line}'. Detalhe: {e}")
            
    return instructions


def evaluate_binary(op, a, b):
    try:
        if op == "+": return a + b
        if op == "-": return a - b
        if op == "*": return a * b
        if op == "/":
            if b == 0: return None
            return a / b
        if op == "//":
            if b == 0: return None
            return a // b
        if op == "%":
            if b == 0: return None
            return a % b
        if op == "**": return a ** b
        if op == "==": return a == b
        if op == "!=": return a != b
        if op == "<": return a < b
        if op == "<=": return a <= b
        if op == ">": return a > b
        if op == ">=": return a >= b
        if op == "and": return bool(a and b)
        if op == "or": return bool(a or b)
    except Exception:
        return None
    return None


def evaluate_unary(op, a):
    try:
        if op == "-": return -a
        if op == "+": return +a
        if op == "not": return not a
    except Exception:
        return None
    return None


def constant_folding_pass(instructions):
    constants = {}
    optimized_instructions = []
    changed = False

    for inst in instructions:
        new_inst = inst.copy()
        
        # 1. Propagação de constantes
        # Se os operandos forem variáveis com valor constante conhecido, substitui
        if new_inst.arg1 is not None and not is_const(new_inst.arg1):
            if new_inst.arg1 in constants:
                new_inst.arg1 = constants[new_inst.arg1]
                changed = True
                
        if new_inst.arg2 is not None and not is_const(new_inst.arg2):
            if new_inst.arg2 in constants:
                new_inst.arg2 = constants[new_inst.arg2]
                changed = True

        # 2. Dobramento de Constantes (Folding)
        if new_inst.op is not None:
            if new_inst.arg2 is not None:
                # Operação Binária
                if is_const(new_inst.arg1) and is_const(new_inst.arg2):
                    folded_val = evaluate_binary(new_inst.op, new_inst.arg1, new_inst.arg2)
                    if folded_val is not None:
                        new_inst.op = None
                        new_inst.arg1 = folded_val
                        new_inst.arg2 = None
                        changed = True
            else:
                # Operação Unária
                if is_const(new_inst.arg1):
                    folded_val = evaluate_unary(new_inst.op, new_inst.arg1)
                    if folded_val is not None:
                        new_inst.op = None
                        new_inst.arg1 = folded_val
                        changed = True

        # 3. Atualizar mapa de constantes
        # Se for atribuição de constante simples (ex: x = 10)
        if not new_inst.is_return and new_inst.target is not None:
            if new_inst.op is None and is_const(new_inst.arg1):
                # Se o valor antigo mudou ou é novo
                if constants.get(new_inst.target) != new_inst.arg1:
                    constants[new_inst.target] = new_inst.arg1
            else:
                # Se a variável foi redefinida com algo não constante, removemos do mapa
                if new_inst.target in constants:
                    del constants[new_inst.target]

        optimized_instructions.append(new_inst)

    return optimized_instructions, changed


def dead_code_elimination_pass(instructions, live_out=None):
    if live_out is None:
        live_out = set()
    else:
        live_out = set(live_out)

    # Varre as instruções para encontrar variáveis retornadas que devem começar "vivas"
    for inst in instructions:
        if inst.is_return and inst.arg1 is not None and not is_const(inst.arg1):
            live_out.add(inst.arg1)

    live_vars = set(live_out)
    optimized_instructions = []
    changed = False

    # Varre de trás para frente
    for inst in reversed(instructions):
        if inst.is_return:
            # Retorno sempre vive
            optimized_instructions.append(inst)
            if inst.arg1 is not None and not is_const(inst.arg1):
                live_vars.add(inst.arg1)
        elif inst.target is not None:
            # Atribuição x = ...
            if inst.target in live_vars:
                optimized_instructions.append(inst)
                # Definição mata a liveness da variável antes deste ponto
                live_vars.discard(inst.target)
                # Operandos ficam vivos
                if inst.arg1 is not None and not is_const(inst.arg1):
                    live_vars.add(inst.arg1)
                if inst.arg2 is not None and not is_const(inst.arg2):
                    live_vars.add(inst.arg2)
            else:
                # Não está viva -> código morto!
                changed = True
        else:
            # Instrução sem target (ex: print ou expressão solta), assumimos que tem efeito
            optimized_instructions.append(inst)
            if inst.arg1 is not None and not is_const(inst.arg1):
                live_vars.add(inst.arg1)
            if inst.arg2 is not None and not is_const(inst.arg2):
                live_vars.add(inst.arg2)

    # Restaura a ordem original
    optimized_instructions.reverse()
    return optimized_instructions, changed


def optimize(code_str, live_out=None):
    """
    Executa a otimização de bloco básico aplicando alternadamente Constant Folding/Propagation
    e Dead Code Elimination até que um ponto fixo (nenhuma mudança ocorra) seja atingido.
    """
    instructions = parse_instructions(code_str)
    
    history = []
    history.append({
        "step": "Código Original",
        "instructions": [str(inst) for inst in instructions]
    })

    iteration = 1
    while True:
        # Passo 1: Constant Folding e Propagation
        folded_insts, changed_cf = constant_folding_pass(instructions)
        if changed_cf:
            history.append({
                "step": f"Iteração {iteration} - Constant Folding",
                "instructions": [str(inst) for inst in folded_insts]
            })
            instructions = folded_insts

        # Passo 2: Dead Code Elimination
        dce_insts, changed_dce = dead_code_elimination_pass(instructions, live_out)
        if changed_dce:
            history.append({
                "step": f"Iteração {iteration} - Dead Code Elimination",
                "instructions": [str(inst) for inst in dce_insts]
            })
            instructions = dce_insts

        # Se nenhum passo alterou nada nesta iteração, atingimos o ponto fixo
        if not changed_cf and not changed_dce:
            break
            
        iteration += 1

    return instructions, history
