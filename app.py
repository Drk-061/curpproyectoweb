from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc
import os
import random
from datetime import datetime

app = Flask(__name__)

class CURPGenerator:
    ESTADOS = {
        'AGUASCALIENTES': 'AS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BS',
        'CAMPECHE': 'CC', 'CHIAPAS': 'CS', 'CHIHUAHUA': 'CH', 'COAHUILA': 'CL',
        'COLIMA': 'CM', 'CIUDAD DE MEXICO': 'DF', 'DURANGO': 'DG', 'GUANAJUATO': 'GT',
        'GUERRERO': 'GR', 'HIDALGO': 'HG', 'JALISCO': 'JC', 'MEXICO': 'MC',
        'MICHOACAN': 'MN', 'MORELOS': 'MS', 'NAYARIT': 'NT', 'NUEVO LEON': 'NL',
        'OAXACA': 'OC', 'PUEBLA': 'PL', 'QUERETARO': 'QT', 'QUINTANA ROO': 'QR',
        'SAN LUIS POTOSI': 'SP', 'SINALOA': 'SL', 'SONORA': 'SR', 'TABASCO': 'TC',
        'TAMAULIPAS': 'TS', 'TLAXCALA': 'TL', 'VERACRUZ': 'VZ', 'YUCATAN': 'YN',
        'ZACATECAS': 'ZS', 'NACIDO EXTRANJERO': 'NE'
    }
    
    APELLIDOS_VALIDOS = {
        'GARCIA', 'RODRIGUEZ', 'MARTINEZ', 'HERNANDEZ', 'LOPEZ', 'GONZALEZ', 'PEREZ',
        'SANCHEZ', 'RAMIREZ', 'TORRES', 'FLORES', 'RIVERA', 'GOMEZ', 'DIAZ', 'CRUZ',
        'MORALES', 'REYES', 'GUTIERREZ', 'ORTIZ', 'CHAVEZ', 'RUIZ', 'JIMENEZ',
        'MENDOZA', 'CASTILLO', 'VAZQUEZ', 'MORENO', 'ROMERO', 'HERRERA', 'MEDINA',
        'AGUILAR', 'GUERRERO', 'RAMOS', 'SILVA', 'CASTRO', 'VARGAS', 'GUZMAN',
        'VELAZQUEZ', 'MENDEZ', 'SALAZAR', 'ROJAS', 'CONTRERAS', 'SOTO', 'LUNA',
        'JUAREZ', 'MEJIA', 'RIOS', 'CAMPOS', 'ESCOBAR', 'CERVANTES', 'LARA',
        'DOMINGUEZ', 'CARRILLO', 'VEGA', 'LEON', 'CANO', 'BLANCO', 'PENA',
        'NAVARRO', 'CORTES', 'SANTIAGO', 'ESTRADA', 'BAUTISTA', 'CABRERA',
        'TREJO', 'MOLINA', 'ALVARADO', 'SANDOVAL', 'IBARRA', 'MARQUEZ',
        'DELGADO', 'SOLIS', 'CARDENAS', 'NUNEZ', 'ESPINOZA', 'VALDEZ'
    }
    
    NOMBRES_VALIDOS = {
        'JUAN', 'JOSE', 'LUIS', 'MIGUEL', 'CARLOS', 'JESUS', 'FRANCISCO', 'ANTONIO',
        'ALEJANDRO', 'PEDRO', 'FERNANDO', 'JORGE', 'RICARDO', 'DANIEL', 'DAVID',
        'MARIA', 'GUADALUPE', 'ROSA', 'ANA', 'MARTHA', 'PATRICIA', 'LAURA',
        'ELIZABETH', 'LETICIA', 'CARMEN', 'GABRIELA', 'ANGELICA', 'TERESA',
        'JUANA', 'ELENA', 'SANDRA', 'MONICA', 'VERONICA', 'DIANA', 'SILVIA',
        'ROBERTO', 'EDUARDO', 'JAVIER', 'RAFAEL', 'OSCAR', 'SERGIO', 'MANUEL',
        'ARTURO, ALBERTO', 'MARIO', 'RAUL', 'ENRIQUE', 'RAMON', 'VICTOR',
        'ADRIANA, BEATRIZ', 'CLAUDIA', 'CECILIA', 'CRISTINA', 'IRMA', 'LIDIA',
        'MARGARITA', 'MIRIAM', 'NORMA', 'GLORIA', 'JOSEFINA', 'YOLANDA',
        'PABLO', 'GERARDO', 'HECTOR', 'ALFREDO', 'RUBEN', 'MARCELO', 'DIEGO',
        'ANDRES', 'GUILLERMO', 'SALVADOR', 'HUGO', 'FELIPE', 'ANGEL', 'ISRAEL',
        'ALICIA', 'CAROLINA', 'JULIA', 'KAREN', 'LUISA', 'NANCY', 'PAOLA',
        'ROCIO', 'SOFIA', 'SUSANA', 'ALMA', 'BERENICE', 'DULCE', 'ESTHER'
    }
    
    PALABRAS_PROHIBIDAS = {
        'BACA', 'BAKA', 'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'CAKO',
        'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO', 'FALO', 'FETO',
        'GETA', 'GUEI', 'GUEY', 'JOTO', 'KACA', 'KACO', 'KAGA', 'KAGO', 'KAKA', 'KAKO',
        'KOGE', 'KOGI', 'KOJA', 'KOJE', 'KOJI', 'KOJO', 'KOLA', 'KULO', 'LILO', 'LOCA',
        'LOCO', 'LOKA', 'LOKO', 'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR', 'MION',
        'MOCO', 'MOKO', 'MULA', 'MULO', 'NACA', 'NACO', 'PEDA', 'PEDO', 'PENE', 'PIPI',
        'PITO', 'POPO', 'PUTA', 'PUTO', 'QULO', 'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN',
        'SENO', 'TETA', 'VACA', 'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY'
    }
    
    def __init__(self):
        self.errores = []
    
    def validar_nombre_apellido(self, texto, tipo):
        texto_limpio = self.limpiar_texto(texto)
        
        if tipo == 'nombre':
            if texto_limpio not in self.NOMBRES_VALIDOS:
                return False, f"Error Sintáctico: No se encontró el nombre '{texto}'"
        else:  
            if texto_limpio not in self.APELLIDOS_VALIDOS:
                return False, f"Error Sintáctico: No se encontró el apellido '{texto}'"
        
        return True, None
    
    def limpiar_texto(self, texto):
        texto = texto.upper().strip()
        reemplazos = {
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'Ñ': 'X', ' ': ''
        }
        for original, reemplazo in reemplazos.items():
            texto = texto.replace(original, reemplazo)
        return texto
    
    def obtener_primera_vocal(self, texto):
        vocales = 'AEIOU'
        for i in range(1, len(texto)):
            if texto[i] in vocales:
                return texto[i]
        return 'X'
    
    def obtener_primera_consonante_interna(self, texto):
        consonantes = 'BCDFGHJKLMNPQRSTVWXYZ'
        for i in range(1, len(texto)):
            if texto[i] in consonantes:
                return texto[i]
        return 'X'
    
    def procesar_nombre(self, nombre):
        nombres = nombre.strip().split()
        if len(nombres) > 1:
            primer_nombre = nombres[0].upper()
            if primer_nombre in ['MARIA', 'JOSE', 'MA', 'MA.', 'J', 'J.']:
                return ' '.join(nombres[1:])
        return nombre
    
    def generar_curp(self, apellido_paterno, apellido_materno, nombre, dia, mes, anio, sexo, estado):
        self.errores = []
        
        if not all([apellido_paterno, apellido_materno, nombre, dia, mes, anio, sexo, estado]):
            self.errores.append("Todos los campos son obligatorios")
            return None
        
        es_valido, error = self.validar_nombre_apellido(apellido_paterno, 'apellido')
        if not es_valido:
            self.errores.append(error)
            return None
        
        es_valido, error = self.validar_nombre_apellido(apellido_materno, 'apellido')
        if not es_valido:
            self.errores.append(error)
            return None
        
        nombre_procesado = self.procesar_nombre(nombre)
        primer_nombre = nombre_procesado.split()[0]
        
        es_valido, error = self.validar_nombre_apellido(primer_nombre, 'nombre')
        if not es_valido:
            self.errores.append(error)
            return None
        
        ap_paterno = self.limpiar_texto(apellido_paterno)
        ap_materno = self.limpiar_texto(apellido_materno)
        nombre_limpio = self.limpiar_texto(primer_nombre)
        
        curp = ""
        
        curp += ap_paterno[0]
        curp += self.obtener_primera_vocal(ap_paterno)
        
        curp += ap_materno[0]
        
        curp += nombre_limpio[0]
        
        if curp[:4] in self.PALABRAS_PROHIBIDAS:
            curp = curp[0] + 'X' + curp[2:]
        
        try:
            anio_str = str(anio)[-2:]  
            mes_str = str(mes).zfill(2)
            dia_str = str(dia).zfill(2)
            curp += anio_str + mes_str + dia_str
            
            fecha_completa = datetime(int(anio), int(mes), int(dia))
        except:
            self.errores.append("Fecha inválida")
            return None
        
        sexo_letra = sexo.upper()[0]
        if sexo_letra not in ['H', 'M']:
            self.errores.append("Sexo debe ser H (Hombre) o M (Mujer)")
            return None
        curp += sexo_letra
        
        estado_codigo = self.ESTADOS.get(estado.upper())
        if not estado_codigo:
            self.errores.append("Estado no válido")
            return None
        curp += estado_codigo
        
        curp += self.obtener_primera_consonante_interna(ap_paterno)
        curp += self.obtener_primera_consonante_interna(ap_materno)
        curp += self.obtener_primera_consonante_interna(nombre_limpio)
        
        if fecha_completa.year <= 1999:
            curp += str(random.randint(0, 9))
        else:
            curp += chr(random.randint(65, 90)) 
        digito_verificador = self.calcular_digito_verificador(curp)
        curp += str(digito_verificador)
        
        return curp
    
    def calcular_digito_verificador(self, curp_17):
        valores = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17,
            'I': 18, 'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'Ñ': 24, 'O': 25,
            'P': 26, 'Q': 27, 'R': 28, 'S': 29, 'T': 30, 'U': 31, 'V': 32, 'W': 33,
            'X': 34, 'Y': 35, 'Z': 36
        }
        
        suma = 0
        posicion = 18
        
        for caracter in curp_17:
            valor = valores.get(caracter, 0)
            suma += valor * posicion
            posicion -= 1
        
        residuo = suma % 10
        
        if residuo == 0:
            return 0
        else:
            return 10 - residuo

@app.route('/', methods=['GET', 'POST'])
def index():
    for archivo in ['parser.out', 'parsetab.py', '__pycache__']:
        try:
            if os.path.isfile(archivo):
                os.remove(archivo)
            elif os.path.isdir(archivo):
                import shutil
                shutil.rmtree(archivo)
        except:
            pass
    
    if request.method == 'GET':
        return render_template("index.html", 
                             estados=CURPGenerator.ESTADOS.keys(),
                             dias=range(1, 32),
                             meses=range(1, 13),
                             anios=range(1920, 2026))
    
    apellido_paterno = request.form.get('apellido_paterno', '')
    apellido_materno = request.form.get('apellido_materno', '')
    nombre = request.form.get('nombre', '')
    dia = request.form.get('dia', '')
    mes = request.form.get('mes', '')
    anio = request.form.get('anio', '')
    sexo = request.form.get('sexo', '')
    estado = request.form.get('estado', '')
    generador = CURPGenerator()
    curp = generador.generar_curp(
        apellido_paterno,
        apellido_materno,
        nombre,
        dia,
        mes,
        anio,
        sexo,
        estado
    )
    
    resultado = {
        'curp': curp,
        'errores': generador.errores,
        'datos': {
            'apellido_paterno': apellido_paterno,
            'apellido_materno': apellido_materno,
            'nombre': nombre,
            'dia': dia,
            'mes': mes,
            'anio': anio,
            'sexo': sexo,
            'estado': estado
        }
    }
    
    return render_template(
        "index.html",
        resultado=resultado,
        estados=CURPGenerator.ESTADOS.keys(),
        dias=range(1, 32),
        meses=range(1, 13),
        anios=range(1920, 2026)
    )

if __name__ == "__main__":
    import sys
    is_production = '--production' in sys.argv or os.environ.get('VERCEL')
    app.run(debug=not is_production, port=5001)