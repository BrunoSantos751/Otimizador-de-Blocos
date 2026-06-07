import os
import sys
from optimizer import optimize

# Códigos de cor ANSI para formatação do terminal
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

def print_header(title):
    print(f"\n{CYAN}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 60}{RESET}\n")

def print_diff(step_name, prev_lines, new_lines):
    print(f"{YELLOW}{BOLD} Passo: {step_name}{RESET}")
    print(f"{WHITE}{'-' * 45}{RESET}")
    
    # Simula um diff simples
    prev_set = set(prev_lines)
    new_set = set(new_lines)
    
    # Mostra o código resultante com cores para o que foi removido ou alterado
    # Como é uma transformação passo a passo, comparamos as linhas.
    # Para fins de visualização didática, vamos exibir a lista anterior e a nova.
    print(f"{BLUE} Código Anterior:{RESET}")
    for line in prev_lines:
        if line not in new_set:
            print(f"  {RED}- {line}{RESET}")
        else:
            print(f"    {line}")
            
    print(f"\n{GREEN} Código Novo / Transformado:{RESET}")
    for line in new_lines:
        if line not in prev_set:
            print(f"  {GREEN}+ {line}{RESET}")
        else:
            print(f"    {line}")
    print(f"{WHITE}{'-' * 45}{RESET}\n")

def display_optimization_process(code_str, live_out=None):
    # Executa a otimização
    optimized_insts, history = optimize(code_str, live_out)
    
    print_header("PROCESSO DE OTIMIZAÇÃO DE BLOCO BÁSICO")
    
    # Exibe o código original
    print(f"{CYAN}{BOLD}Código de Entrada:{RESET}")
    print(code_str.strip())
    print()
    
    # Exibe cada passo de transformação
    for i in range(1, len(history)):
        prev_step = history[i-1]
        curr_step = history[i]
        print_diff(curr_step["step"], prev_step["instructions"], curr_step["instructions"])
        
    # Resultados Finais e Estatísticas
    orig_lines = [line.strip() for line in code_str.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
    final_lines = [str(inst) for inst in optimized_insts]
    
    orig_count = len(orig_lines)
    final_count = len(final_lines)
    reduction = ((orig_count - final_count) / orig_count) * 100 if orig_count > 0 else 0
    
    print_header("RESULTADO FINAL")
    print(f"{GREEN}{BOLD}Código Otimizado:{RESET}")
    for line in final_lines:
        print(f"  {GREEN}{line}{RESET}")
    print()
    
    print(f"{MAGENTA}{BOLD}Estatísticas de Redução:{RESET}")
    print(f"  • Instruções originais: {orig_count}")
    print(f"  • Instruções otimizadas: {final_count}")
    print(f"  • Redução de tamanho: {reduction:.1f}%")
    print(f"{CYAN}{'=' * 60}{RESET}\n")

def get_preset_cases():
    return {
        "1": {
            "title": "Constant Folding & Propagation Básico",
            "code": "a = 2\nb = 3\nc = a + b\nd = c * 4\nreturn d",
            "live_out": []
        },
        "2": {
            "title": "Eliminação de Código Morto (DCE) Simples",
            "code": "x = 10\ny = 20\nz = x + 5\nunused_var = 500\nreturn z",
            "live_out": []
        },
        "3": {
            "title": "Ponto Fixo (Múltiplas Interações Complexas)",
            "code": "a = 10\nb = 20\nc = a + b\nd = c * 2\ne = d + 100\nreturn c",
            "live_out": []
        }
    }

def main():
    # Inicialização opcional de cores de terminal no Windows
    if sys.platform == "win32":
        os.system("color")
        
    presets = get_preset_cases()
    
    while True:
        print(f"{CYAN}{BOLD}=== OTIMIZADOR DE BLOCOS BÁSICOS (Compiladores) ==={RESET}")
        print("Escolha uma opção para executar:")
        print(f" {GREEN}1{RESET} - Caso de Teste 1 ({presets['1']['title']})")
        print(f" {GREEN}2{RESET} - Caso de Teste 2 ({presets['2']['title']})")
        print(f" {GREEN}3{RESET} - Caso de Teste 3 ({presets['3']['title']})")
        print(f" {GREEN}4{RESET} - Digitar Instruções Personalizadas (Três Endereços)")
        print(f" {GREEN}5{RESET} - Sair")
        
        choice = input(f"\n{BOLD}Opção > {RESET}").strip()
        
        if choice in presets:
            case = presets[choice]
            display_optimization_process(case["code"])
            input("Pressione Enter para voltar ao menu...")
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "4":
            print(f"\n{YELLOW}Digite o código linear (três endereços). Digite uma linha em branco ou 'FIM' para finalizar:{RESET}")
            user_lines = []
            while True:
                line = input()
                if line.strip().upper() == "FIM" or line.strip() == "":
                    break
                user_lines.append(line)
            
            if not user_lines:
                print(f"{RED}Nenhum código digitado.{RESET}\n")
                continue
                
            code_str = "\n".join(user_lines)
            
            live_out_str = input("Variáveis vivas de saída (separadas por vírgula, ex: x,y) [Opcional]: ").strip()
            live_out = [v.strip() for v in live_out_str.split(',') if v.strip()] if live_out_str else None
            
            try:
                display_optimization_process(code_str, live_out)
            except Exception as e:
                print(f"\n{RED}Erro durante processamento: {e}{RESET}\n")
                
            input("Pressione Enter para voltar ao menu...")
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "5":
            print(f"\n{CYAN}Obrigado por usar o Otimizador de Blocos! Finalizando...{RESET}\n")
            break
        else:
            print(f"\n{RED}Opção inválida! Tente novamente.{RESET}\n")

if __name__ == "__main__":
    main()
