# -*- encoding: UTF-8
"""
Deducciones del impuesto a las ganancias
"""
from decimal import Decimal

# Constantes correspondientes a las deducciones
CONYUGE = 0
HIJOS = 1
PADRES_Y_OTROS = 2
#CREDITO_HIPOTECARIO = 3
#SEGURO_DE_VIDA = 4
#DONACIONES = 5
#MEDICINA_PREPAGA = 6
#HOSPITALIZACION = 7
#SEPELIO = 8
#SEGURO_RETIRO = 9
#EMPLEADO_DOMESTICO = 10
#DEDUCCION_ESPECIAL_REL = 11
#DEDUCCION_ESPECIAL_AUTON = 12
#GANANCIA_NO_IMPONIBLE = 13

DEDUCCION_ESPECIAL_REL = 3
DEDUCCION_ESPECIAL_AUTON = 4
GANANCIA_NO_IMPONIBLE = 5


class Deduccion(object):
    """
    Clase con la lógica de deducciones, controla que la deducción a ser
    aplicada no exceda el máximo.
    """

    #TODO: Hacer algo con esta clase, calcular el máximo, etc.
    def __init__(self, tipo, cantidad=None, maximo=None, autonomo=True, 
                 relacion_de_dependencia=True):
        self.tipo = tipo
        self.cantidad = cantidad
        self._max = maximo
        self._autonomo = autonomo
        self._rel_de_dep = relacion_de_dependencia


# Deducciones anuales (Art. 23)
POSIBLES_DEDUCCIONES = [
    Deduccion(u'Cónyuge', Decimal('10000.0')),
    Deduccion(u'Hijos', Decimal('5000.0')),
    Deduccion(u'Padres y otros', Decimal('3750.0')),
    #    Deduccion(u'Crédito hipotecario', maximo='20000.0'),
    #    Deduccion(u'Seguro de vida', maximo='996.23'),
    #    Deduccion(u'Donaciones', maximo='{bruto_anual} * 0.05'),
    #    Deduccion(u'Prepagas médicas', maximo='{bruto_anual} * 0.05'),
    #    Deduccion(u'Honorarios de hospitalización',
    #              maximo='{bruto_anual} * 0.05'),
    #    Deduccion(u'Gastos de sepelio', maximo='996.23'),
    #    Deduccion(u'Seguro de retiro privados', maximo='1261.16'),
    #    Deduccion(u'Empleados domésticos', maximo='9000.0'),
    Deduccion(u'Deducción especial (inc e)', Decimal('43200'), 
              autonomo=False),
    Deduccion(u'Deducción especial (inc c)', Decimal('9000.0'), 
              relacion_de_dependencia=False),
    Deduccion(u'Ganancia no imponible', Decimal('9000.0')),
]
