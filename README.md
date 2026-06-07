# Otimizador de Blocos Básicos: Constant Folding & Dead Code Elimination

Este projeto foi desenvolvido para a avaliação prática da disciplina **Componentes de Compiladores** no curso de **Ciência da Computação** da **Unima - Afya**. O objetivo é aplicar os conceitos de otimização de código sobre uma lista de instruções lineares (código de três endereços) usando as técnicas de:
- **Constant Folding** (Dobramento de Constantes)
- **Constant Propagation** (Propagação de Constantes)
- **Dead Code Elimination - DCE** (Eliminação de Código Morto)

---

## 👥 Autores (Grupo)

- **Bruno Santos Moraes**
- **Fabio Fernandes Reis Filho**
- **João Honório Barbosa**

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3 (compatível com Python 3.6 ou superior)
- **Biblioteca para PDF:** `reportlab` (utilizada para a geração local do Relatório Técnico)
- **Biblioteca para Testes:** `unittest` (módulo nativo do Python)

---

## 🚀 Como Executar o Projeto

Nenhum compilador ou setup complexo é necessário, pois o otimizador foi desenvolvido utilizando a biblioteca padrão do Python.

### 1. Verificar Instalação do Python
Certifique-se de que o Python 3 está instalado em seu computador. No terminal, execute:
```bash
python --version
```

### 2. Executar a Interface Interativa (CLI)
A CLI permite demonstrar a otimização passo a passo em tempo real com diffs coloridos. Você pode escolher entre 3 casos de teste padrão ou digitar o seu próprio bloco de instruções.

Execute o comando:
```bash
python main.py
```
**Opções no menu:**
- `1`, `2` ou `3` para rodar os casos de teste didáticos pré-configurados (nota: estes três casos já estão analisados no relatório).
- `4` para digitar seu próprio código TAC interativamente.
- `5` para sair do programa.

---

### 3. Digitar Instruções Personalizadas (Opção 4).
Ao escolher a opção `4`, você poderá testar suas próprias sequências de instruções de três endereços. 

#### Como usar:
1. Digite uma instrução por linha e pressione **Enter**.
2. Deixe uma **linha em branco** (ou digite `FIM`) e pressione **Enter** para finalizar a inserção do código.
3. Insira as **Variáveis vivas de saída (Live-Out)** (opcional):
   - **O que significa?** São as variáveis locais que você precisa que continuem existindo ao final do bloco.
   - Se o seu código tiver uma linha de retorno (ex: `return c`), o otimizador automaticamente detectará `c` como viva e a preservará.
   - Caso seu código **não** possua um `return`, digite o nome das variáveis que quer preservar separadas por vírgula (ex: `x,y`). Se deixar em branco e o código não tiver `return`, a Eliminação de Código Morto (DCE) assumirá que nada é necessário e apagará todo o seu código!

#### Exemplo de Código TAC para Testar:
Copie e cole o bloco a seguir na opção `4` para testar o comportamento do otimizador:
```text
x = 100
y = x / 2
z = y + 10
a = 50
b = a * 2
c = b - z
return c
```
*Após colar o código e finalizar com Enter, o otimizador irá propagar e dobrar os valores até retornar `return 40` e remover todas as variáveis intermediárias redundantes por serem código morto!*

---

## 🧪 Como Executar os Testes Automatizados

O projeto acompanha testes unitários cobrindo o parser, folding de expressões, retropropagação de liveness (DCE) e tratamento de exceções.

Para rodar a suíte de testes:
```bash
python -m unittest test_optimizer.py
```

---

## ⚙️ Estrutura dos Arquivos

1. **`optimizer.py`**: O núcleo lógico do compilador (classe `Instruction`, parser de expressões de três endereços e os passes de simplificação que iteram até atingir o ponto fixo).
2. **`main.py`**: A CLI interativa do terminal com diffs coloridos passo a passo.
3. **`test_optimizer.py`**: A suíte de testes automáticos do módulo.
4. **`Relatorio_Tecnico.pdf`**: O relatório técnico em formato PDF.

