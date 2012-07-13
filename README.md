Módulo para calcular el impuesto a las ganancias de una manera pythonica y prolija.

¿Estás cansado de no saber de donde cuernos sale tu sueldo? Acá está tu solución.

Se tiene en cuenta aportes, y las deducciones correspondientes al art. 23.

Valores actualizados a Enero de 2010.

Ejemplo:

```python
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
```
