# -*- encoding: UTF-8
"""
Módulo para calcular el impuesto a las ganancias. Se tiene en cuenta aportes,
y las deducciones correspondientes al art. 23. 

Valores actualizados a Enero de 2010.

Ejemplo:

    # Puede ser o autónomo o relación de dependencia por defecto, la segunda
    # opción es utilizada.
    >>> ganancias = Ganancias(8000, autonomo=False, aguinaldo=True)
    >>> ganancias.bruto_anual
    104000

    # Aportes de enero
    >>> for aporte, monto in ganancias.meses[0].aportes:
    ...     print "Aporte de %s = $%.2f" % (apote, monto)
    Aporte de Jubilación = $880.00
    Aporte de INSSJP = $240.00
    Aporte de Obra Social = $240.00

    # Agregamos algunas deducciones y calculamos el impuesto
    >>> ganancias.agregar_deduccion(PADRES_Y_OTROS)
    >>> ganancias.agregar_deduccion(PADRES_Y_OTROS)
    >>> ganancias.calcular_ganancias()
    >>> print "Impuesto Enero: $%.2f" % (ganancias.meses[0].impuesto_ganancias)
    Impuesto Enero: $191.43

    # El aguinaldo también es calculado
    >>> print "Impuesto Junio: $%.2f" % (ganancias.meses[5].impuesto_ganancias)
    Impuesto Junio: $821.73
"""

from decimal import Decimal
from bisect import bisect_left
from deduccion import *

# Alicuotas fijas separadas en rangos salariales (%, excedente, fijo)
ALICUOTAS = [
    (Decimal('0.09'), Decimal('0.0'), Decimal('0.0')),
    (Decimal('0.14'), Decimal('10000.0'), Decimal('900.0')),
    (Decimal('0.19'), Decimal('20000.0'), Decimal('2300.0')),
    (Decimal('0.23'), Decimal('30000.0'), Decimal('4200.0')),
    (Decimal('0.27'), Decimal('60000.0'), Decimal('11100.0')),
    (Decimal('0.31'), Decimal('90000.0'), Decimal('19200.0')),
    (Decimal('0.35'), Decimal('120000.0'), Decimal('28500.0')),
]

# Aportes mensuales
APORTES = [
    (u'Jubilación', Decimal('0.11')),
    (u'INSSJP', Decimal('0.03')),
    (u'Obra Social', Decimal('0.03')),
]


class Ganancias(object):
    """
    Calcula el impuesto a las ganancias, basado en el sueldo de todo el año.
    Por defecto uno lo instancia con un sueldo y este se aplica a todos los
    meses del año, si es necesario cambiar alguno puede hacerse en la lista
    meses.

    Ejemplo:
        >>> ganancias = Ganancias(7800, autonomo=False, aguinaldo=True)
        # Recibió un bono de un sueldo en Marzo, se mantienen 
        # las deducciones pero se cambia el bruto
        >>> ganancias.cambiar_mes(3, ganancias.meses[2] * 2)
    """

    def __init__(self, sueldo_bruto, autonomo=False, aguinaldo=True):
        self._autonomo = autonomo
        self._deducciones = []
        self._con_aguinaldo = aguinaldo
        # Para calcular ganancias, necesitamos los sueldos de todo el año
        self.meses = [Sueldo(sueldo_bruto) for i in xrange(12)]

        self._calcular_aguinaldo()

    def _calcular_aguinaldo(self):
        # Calcular aguinaldo si corresponde.
        if self._con_aguinaldo:
            # El aguinaldo corresponde a la mitad del mayor sueldo
            sueldo_maximo = max(self.meses)

            # Primero agregamos el aguinaldo asumiendo que lo tiene
            self.meses[5] += sueldo_maximo / 2
            self.meses[11] += sueldo_maximo / 2

            # Los ciclos son semestrales
            for ciclo in (6, 12):
                idx = ciclo - 6
                meses = len([suel for suel in self.meses[idx:ciclo] if suel])
                if meses != 6:
                    self.meses[ciclo - 1] *= meses / 6

    def cambiar_mes(self, mes, sueldo, bonos=0):
        """
        Modificar el sueldo de un mes. Tener en cuenta que la instancia de 
        sueldo tiene también las deducciones de ese mes.
        """
        if not isinstance(sueldo, Sueldo):
            raise TypeError("El sueldo debe ser una instancia de 'Sueldo'")

        self.meses[mes - 1] = sueldo

    def _impuesto_anual(self):
        # Calcula el impuesto anual como la sumatoria de todos los meses
        impuesto = 0
        for sueldo in self.meses:
            impuesto += sueldo.impuesto_ganancias

        return impuesto

    def _bruto_anual(self):
        # Suma todos los sueldos brutos del año.
        return sum(self.meses).bruto

    def eliminar_deduccion(self, deduccion, mes=None):
        """
        Eliminar una deducción en el mes dado. Si no se especifica ningún
        mes, la acción es repetida en todo el año.
        """
        meses = [mes] if mes else xrange(12)
        for mes in meses:
            self.meses[mes].eliminar_deduccion(deduccion)

    def agregar_deduccion(self, deduccion, cantidad=None, mes=None):
        """
        Agrega una deducción en el mes dado. Si no se especifica ningún
        mes, la acción es repetida en todo el año.
        """
        meses = [mes] if mes else xrange(12)
        for mes in meses:
            self.meses[mes].agregar_deduccion(deduccion, cantidad)

    def calcular_ganancias(self):
        """
        Calcula el impuesto a las ganancias tomando en cuenta las cuentas del
        artículo 23. Y las tablas correspondientes a las alicuotas 
        y deducciones.
        """
        # Agregamos las deducciones correspondientes por ser autónomo o 
        # rel de dependencia (art 23. inc c)
        self.agregar_deduccion(GANANCIA_NO_IMPONIBLE)
        if self._autonomo:
            self.agregar_deduccion(DEDUCCION_ESPECIAL_AUTON)
        else:
            self.agregar_deduccion(DEDUCCION_ESPECIAL_REL)

        neto_acumulado = impuesto_acumulado = 0
        for mes, sueldo in enumerate(self.meses):
            mes += 1
            rango_sueldos = [(r[1] / 12) * mes for r in ALICUOTAS]

            # Sumamos las deducciones a ser aplicadas este mes
            deducciones = sum((d.cantidad for d in sueldo.deducciones))
            deducciones = (deducciones / 12) * mes

            # Calculamos todos los aportes del mes
            aportes = sum((monto for aporte, monto in sueldo.aportes))

            neto_acumulado += sueldo.bruto - aportes
            gravado = max(neto_acumulado - deducciones, 0)

            # Acá vemos en que lugar de la tabla de alicuotas cae el neto 
            # acumulado menos las deducciones. El numero que devuelve 
            # corresponde al índice de la lista.
            idx = max(bisect_left(rango_sueldos, gravado) - 1, 0)

            porc, excede, fijo = ALICUOTAS[idx]
            fijo = (fijo / 12) * mes
            excede = (excede / 12) * mes

            # Calculamos el impuesto
            impuesto = (fijo + (gravado - excede) * porc) - impuesto_acumulado

            # Lo guardamos en el sueldo del mes
            sueldo.impuesto_ganancias = max(impuesto, 0)
            impuesto_acumulado += impuesto

    bruto_anual = property(_bruto_anual)
    impuesto_anual = property(_impuesto_anual)


class Sueldo(object):
    """
    Clase que representa un sueldo, contiene las deducciones, aportes 
    y el impuesto a las ganancias una vez que esté calculado.
    """

    def __init__(self, sueldo_bruto):
        self.bruto = Decimal(str(sueldo_bruto))
        self.deducciones = []
        self._impuesto_ganancias = -1

    def _set_impuesto_ganancias(self, value):
        # Guardamos el cálculo del impuesto
        self._impuesto_ganancias = value

    def _impuesto_ganancias(self):
        # Se usan properties acá para poder advertir cuando el impuesto
        # no ha sido calculado.
        if self._impuesto_ganancias == -1:
            raise ValueError("El impuesto a las ganancias no está calculado")

        return self._impuesto_ganancias

    def _sueldo_neto(self):
        # El sueldo neto corresponde al bruto sin los aportes e impuestos
        contrib_suma = sum((a[1] for a in self.aportes))
        return self.bruto - contrib_suma - self.impuesto_ganancias

    def eliminar_deduccion(self, deduccion):
        """
        Eliminar una deducción. Las deducciones se encuentran en el módulo
        'deduccion'.
        """

        if deduccion < 0 or deduccion > len(POSIBLES_DEDUCCIONES):
            raise ValueError(u"Tipo de deducción inválida")

        self.deducciones.remove(POSIBLES_DEDUCCIONES[deduccion])

    def agregar_deduccion(self, deduccion, cantidad=None):
        """
        Agregar una deducción al sueldo. Las deducciones se encuentran en el 
        módulo 'deduccion'.
        """
        if deduccion < 0 or deduccion > len(POSIBLES_DEDUCCIONES):
            raise ValueError(u"Tipo de deducción inválida")

        deduccion = POSIBLES_DEDUCCIONES[deduccion]
        if cantidad:
            deduccion.cantidad = cantidad

        self.deducciones.append(deduccion)

    def clonar(self):
        """
        Devuelve una nueva instancia de Sueldo con todas los miembros
        del actual.
        """
        nuevo_sueldo = Sueldo(self.bruto)
        nuevo_sueldo.deducciones = self.deducciones
        nuevo_sueldo._impuesto_ganancias = self._impuesto_ganancias
        return nuevo_sueldo

    def _aportes(self):
        # Devuelve los aportes con sus nombres de acuerdo a la 
        # tabla de aportes
        return [(a[0], self.bruto * a[1]) for a in APORTES]

    # ---- Operaciones -----
    def __div__(self, num):
        if isinstance(num, Sueldo):
            num = num.bruto

        nuevo_sueldo = self.clonar()
        nuevo_sueldo.bruto /= num
        return nuevo_sueldo

    def __radd__(self, num):
        if isinstance(num, Sueldo):
            num = num.bruto

        nuevo_sueldo = self.clonar()
        nuevo_sueldo.bruto += num
        return nuevo_sueldo

    __add__ = __radd__

    def __mul__(self, num):
        if isinstance(num, Sueldo):
            num = num.bruto

        nuevo_sueldo = self.clonar()
        nuevo_sueldo.bruto *= num
        return nuevo_sueldo

    def __str__(self):
        return "<Sueldo: $%.2f>" % self.bruto

    aportes = property(_aportes)
    neto = property(_sueldo_neto)
    impuesto_ganancias = property(_impuesto_ganancias, _set_impuesto_ganancias)

