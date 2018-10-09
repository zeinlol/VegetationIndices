from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import QgsRasterLayer


class VITool:
    def __init__(
        self, index_name, red_band, nir_band,
        output, blue_band, L, a,
    ):
        self.index = index_name
        self.red = red_band
        self.nir = nir_band
        self.blue = blue_band
        self.L = L
        self.a = a
        self.output = output

    def calc_ndvi(self):
        r = QgsRasterCalculatorEntry()
        r.ref = self.red.name() + '@1'
        r.raster = self.red
        r.bandNumber = 1

        ir = QgsRasterCalculatorEntry()
        ir.ref = self.nir.name() + '@2'
        ir.raster = self.nir
        ir.bandNumber = 1

        entries = list()
        entries.append(r)
        entries.append(ir)

        expression = '({0} - {1}) / ({0} + {1})'.format(ir.ref, r.ref)

        calc = QgsRasterCalculator(
            expression,
            self.output, "GTiff",
            self.red.extent(), self.red.width(), self.red.height(),
            entries
        )
        calc.processCalculation()

    def calc_rvi(self):
        r = QgsRasterCalculatorEntry()
        r.ref = self.red.name() + '@1'
        r.raster = self.red
        r.bandNumber = 1

        ir = QgsRasterCalculatorEntry()
        ir.ref = self.nir.name() + '@2'
        ir.raster = self.nir
        ir.bandNumber = 1

        entries = list()
        entries.append(r)
        entries.append(ir)

        expression =  '{0} / {1}'.format(r.ref, ir.ref)

        calc = QgsRasterCalculator(
            expression,
            self.output, "GTiff",
            self.red.extent(), self.red.width(), self.red.height(),
            entries
        )
        calc.processCalculation()

    def calc_savi(self):
        r = QgsRasterCalculatorEntry()
        r.ref = self.red.name() + '@1'
        r.raster = self.red
        r.bandNumber = 1

        ir = QgsRasterCalculatorEntry()
        ir.ref = self.nir.name() + '@2'
        ir.raster = self.nir
        ir.bandNumber = 1

        entries = list()
        entries.append(r)
        entries.append(ir)

        expression =  '(({0} - {1}) / ({0} + {1} + {2})) * (1 + {2})'.format(
            ir.ref, r.ref, self.L
        )

        calc = QgsRasterCalculator(
            expression,
            self.output, "GTiff",
            self.red.extent(), self.red.width(), self.red.height(),
            entries
        )
        calc.processCalculation()

    def calc_arvi(self):
        r = QgsRasterCalculatorEntry()
        r.ref = self.red.name() + '@1'
        r.raster = self.red
        r.bandNumber = 1

        ir = QgsRasterCalculatorEntry()
        ir.ref = self.nir.name() + '@2'
        ir.raster = self.nir
        ir.bandNumber = 1

        b = QgsRasterCalculatorEntry()
        b.ref = self.blue.name() + '@3'
        b.raster = self.blue
        b.bandNumber = 1

        entries = list()
        entries.append(r)
        entries.append(ir)
        entries.append(b)

        expression =  '({0} - ({1} - {3} * ({1} - {2}))) / ({0} + ({1} - {3} * ({1} - {2})))'.format(
            ir.ref, r.ref, b.ref, str(self.a)
        )

        calc = QgsRasterCalculator(
            expression,
            self.output, "GTiff",
            self.red.extent(), self.red.width(), self.red.height(),
            entries
        )
        calc.processCalculation()
