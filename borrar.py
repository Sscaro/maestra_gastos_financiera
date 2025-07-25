import timeit
import unittest
def crear_lista_ciclo(inicio, final):
    lista = []
    for num in range(inicio, final):
        lista.append(num)
    return lista

def lista_comprehension(inicio, final):
    return [valor for valor in range(inicio, final)]

# Usar lambda para que la función no se ejecute inmediatamente
tiempo_ciclo = timeit.timeit(lambda: crear_lista_ciclo(10, 20), number=100)
tiempo_comprehension = timeit.timeit(lambda: lista_comprehension(10, 20), number=100)


print(f"Tiempo usando ciclo for: {tiempo_ciclo:.6f} segundos")
print(f"Tiempo usando comprensión de listas: {tiempo_comprehension:.6f} segundos")
class Pruebas(unittest.TestCase):

    def setUp(self):
        self.esperado = list(range(1, 10))

    def test_crear_lista_ciclo(self):
        self.assertEqual(crear_lista_ciclo(1, 10), self.esperado)

    def test_lista_comprehension(self):
        self.assertEqual(lista_comprehension(1, 10), self.esperado)

    def tearDown(self):
        del self.esperado

if __name__ == "__main__":
    unittest.main(exit=False)