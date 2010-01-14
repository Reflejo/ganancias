# -*- encoding: UTF-8
"""
Deducciones del impuesto a las ganancias
"""
from decimal import Decimal
import re
import sys

# Constantes correspondientes a las deducciones
CONYUGE = 0
HIJOS = 1
PADRES_Y_OTROS = 2
CREDITO_HIPOTECARIO = 3
SEGURO_DE_VIDA = 4
DONACIONES = 5
MEDICINA_PREPAGA = 6
HOSPITALIZACION = 7
SEPELIO = 8
SEGURO_RETIRO = 9
EMPLEADO_DOMESTICO = 10
ASISTENCIA_SANITARIA = 11
DEDUCCION_ESPECIAL_REL = 12
DEDUCCION_ESPECIAL_AUTON = 13
GANANCIA_NO_IMPONIBLE = 14


class Deduccion(object):
    """
    Clase con la lógica de deducciones, controla que la deducción a ser
    aplicada no exceda el máximo.
    """

    def __init__(self, tipo, cantidad=None, maximo=None, autonomo=True, 
                 relacion_de_dependencia=True):
        if not cantidad and not maximo:
            raise ValueError("La cantidad es siempre necesaria para las "\
                             "deducciones que no son anuales")

        self.tipo = tipo
        self._cantidad = cantidad and Decimal(str(cantidad))
        self._max = maximo
        self._autonomo = autonomo
        self._rel_de_dep = relacion_de_dependencia
        self.ganancias = None

    def _get_cantidad(self):
        # Devuelve la cantidad definida para la deduccion solo si no excede
        # el maximo anual que establece la ley, en ese caso devuelve ese
        # maximo.
        return min(self._cantidad, self.maximo)
    
    def _set_cantidad(self, val):
        # Simplemente guardamos el valor deseado para la deducción
        self._cantidad = val

    def _calcular_maximo(self):
        if not self._max:
            return sys.maxint

        maximo = self._max
        for val in re.findall('{(.*?)}', self._max):
            atributo_ganancias = str(getattr(self.ganancias, val)) 
            maximo = maximo.replace('{%s}' % val, atributo_ganancias)

        if not re.match('^[\d \*\+\.\-/]+$', maximo):
            raise ValueError("Por seguridad la operacion no puede tener "\
                             "otro caracter que no sea numero o un operador")
        
        return Decimal(str(eval(maximo)))

    cantidad = property(_get_cantidad, _set_cantidad)
    maximo = property(_calcular_maximo)


# Deducciones anuales (Art. 23)
POSIBLES_DEDUCCIONES = [
    Deduccion(u'Cónyuge', Decimal('10000.0')),
    Deduccion(u'Hijos', Decimal('5000.0')),
    Deduccion(u'Padres y otros', Decimal('3750.0')),
    Deduccion(u'Crédito hipotecario', maximo='20000.0'),
    Deduccion(u'Seguro de vida', maximo='996.23'),
    Deduccion(u'Donaciones', maximo='{ganancia_neta_anual} * 0.05'),
    Deduccion(u'Prepagas médicas', maximo='{ganancia_neta_anual} * 0.05'),
    Deduccion(u'Honorarios de hospitalización',
              maximo='{ganancia_neta_anual} * 0.05'),
    Deduccion(u'Gastos de sepelio', maximo='996.23'),
    Deduccion(u'Seguro de retiro privados', maximo='1261.16'),
    Deduccion(u'Empleados domésticos', maximo='9000.0'),
    Deduccion(u'Asistencia sanitaria', maximo='0.4 * {_cantidad}'),

    Deduccion(u'Deducción especial (inc e)', Decimal('43200'), 
              autonomo=False),
    Deduccion(u'Deducción especial (inc c)', Decimal('9000.0'), 
              relacion_de_dependencia=False),
    Deduccion(u'Ganancia no imponible', Decimal('9000.0')),
]
