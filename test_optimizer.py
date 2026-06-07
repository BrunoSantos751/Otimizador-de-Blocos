import unittest
from optimizer import (
    parse_instructions,
    constant_folding_pass,
    dead_code_elimination_pass,
    optimize,
    evaluate_binary,
    evaluate_unary
)

class TestOptimizer(unittest.TestCase):

    def test_parser(self):
        code = """
        x = 10
        y = x + 5
        z = -y
        w = a and b
        return z
        """
        insts = parse_instructions(code)
        self.assertEqual(len(insts), 5)
        self.assertEqual(insts[0].target, "x")
        self.assertEqual(insts[0].arg1, 10)
        self.assertIsNone(insts[0].op)

        self.assertEqual(insts[1].target, "y")
        self.assertEqual(insts[1].op, "+")
        self.assertEqual(insts[1].arg1, "x")
        self.assertEqual(insts[1].arg2, 5)

        self.assertEqual(insts[2].target, "z")
        self.assertEqual(insts[2].op, "-")
        self.assertEqual(insts[2].arg1, "y")
        self.assertIsNone(insts[2].arg2)

        self.assertEqual(insts[3].target, "w")
        self.assertEqual(insts[3].op, "and")
        self.assertEqual(insts[3].arg1, "a")
        self.assertEqual(insts[3].arg2, "b")

        self.assertTrue(insts[4].is_return)
        self.assertEqual(insts[4].arg1, "z")

    def test_constant_folding_basic(self):
        code = """
        a = 2 + 3
        b = a * 4
        c = b - 10
        return c
        """
        insts = parse_instructions(code)
        # Primeiro pass de Constant Folding
        folded, changed = constant_folding_pass(insts)
        self.assertTrue(changed)
        
        # O estado esperado após o primeiro pass de folding/propagation:
        # a = 5
        # b = 20 (porque 'a' foi propagada como 5, depois 5 * 4 foi dobrado para 20)
        # c = 10 (porque 'b' foi propagada como 20, depois 20 - 10 foi dobrado para 10)
        # return 10
        self.assertEqual(str(folded[0]), "a = 5")
        self.assertEqual(str(folded[1]), "b = 20")
        self.assertEqual(str(folded[2]), "c = 10")
        self.assertEqual(str(folded[3]), "return 10")

    def test_dead_code_elimination_basic(self):
        code = """
        x = 100
        y = 200
        z = x + 50
        return z
        """
        insts = parse_instructions(code)
        # 'y' não é usada em lugar algum e não é retorno, deve ser eliminada.
        dce, changed = dead_code_elimination_pass(insts, live_out=set())
        self.assertTrue(changed)
        
        # 'y' deve ter sido removida, restando x, z, return z
        self.assertEqual(len(dce), 3)
        targets = [inst.target for inst in dce if inst.target]
        self.assertIn("x", targets)
        self.assertNotIn("y", targets)
        self.assertIn("z", targets)

    def test_fixed_point_optimization(self):
        # Um cenário complexo de interdependência:
        # a e b são constantes
        # c calcula a + b (dobrado para 30)
        # d é código morto, mas calcula c * 2
        # e é código morto e calcula e_var (nunca usado)
        # return c
        code = """
        a = 10
        b = 20
        c = a + b
        d = c * 2
        e = d + 100
        return c
        """
        optimized, history = optimize(code)
        
        # Esperado após otimização completa:
        # a, b, d, e eliminados por serem mortos.
        # Resta apenas:
        # return 30 (ou c = 30; return c)
        # Vamos verificar se as instruções finais contêm apenas o return 30 (ou c = 30 e return c)
        # Na verdade, se 'c' está no return, 'c' é mantido se houver "c = 30" e "return c"
        # Ou se "return c" foi propagado para "return 30", então "c = 30" vira morto e é eliminado.
        # Vamos ver qual o comportamento exato:
        # Pass 1 CF:
        # a = 10
        # b = 20
        # c = 30
        # d = 60
        # e = 160
        # return 30  (o return c vira return 30)
        # Pass 2 DCE:
        # Como o return é 'return 30', 'c' não está na lista de live_out nem é operand do return.
        # Portanto, a, b, c, d, e são todos considerados mortos e eliminados!
        # Resta apenas:
        # return 30
        
        self.assertEqual(len(optimized), 1)
        self.assertTrue(optimized[0].is_return)
        self.assertEqual(optimized[0].arg1, 30)

    def test_division_by_zero(self):
        # Garante que não quebra o compilador com divisão por zero, apenas mantém a instrução
        code = """
        x = 5 / 0
        return x
        """
        optimized, history = optimize(code)
        # Deve manter a instrução original ou falhar graciosamente no folding
        self.assertEqual(len(optimized), 2)
        self.assertEqual(optimized[0].op, "/")
        self.assertEqual(optimized[0].arg1, 5)
        self.assertEqual(optimized[0].arg2, 0)

    def test_booleans_and_comparisons(self):
        code = """
        a = 10
        b = 20
        c = a < b
        d = not c
        return d
        """
        optimized, history = optimize(code)
        # a = 10, b = 20 -> c = True -> d = False -> return False
        # Todos eliminados por DCE exceto o return
        self.assertEqual(len(optimized), 1)
        self.assertTrue(optimized[0].is_return)
        self.assertEqual(optimized[0].arg1, False)

if __name__ == '__main__':
    unittest.main()
