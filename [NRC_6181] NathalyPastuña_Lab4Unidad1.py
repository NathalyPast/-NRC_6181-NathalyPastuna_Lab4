import datetime
import requests
import os
import argparse
import re
import json
from dateutil.easter import easter
from dateutil.relativedelta import relativedelta as rd, FR
from holidays.constants import JAN, MAY, AUG, OCT, NOV, DEC
from holidays.holiday_base import HolidayBase


class HolidayEcu(HolidayBase):
    """
    Una clase para representar un feriado en Ecuador por provincia (HolidayEcu)
     Su objetivo es determinar si un
     fecha especifica es unas vacaciones lo mas rapido y flexible posible.
     https://www.turismo.gob.ec/wp-content/uploads/2020/03/CALENDARIO-DE-FERIADOS.pdf
     ...
     Atributos (Hereda la clase HolidayBase)
     ----------
     prueba: calle
         codigo de provincia segun ISO3166-2
     Metodos
     -------
     __init__(self, plate, date, time, online=False):
         Construye todos los atributos necesarios para el objeto HolidayEcu.
     _poblar(uno mismo, año):
         Devoluciones si una fecha es feriado o no
    """     
    # ISO 3166-2 codes for the principal subdivisions, 
    # called provinces
    # https://es.wikipedia.org/wiki/ISO_3166-2:EC
    PROVINCES = ["EC-P"]  # TODO add more provinces

    def __init__(self, **kwargs):
        """
       Contructor con metodos necesario para los dias festivos de Ecuador.
        """       
        self.country = "Ecuador"
        self.prov = kwargs.pop("prov", "ON")
        HolidayBase.__init__(self, **kwargs)

    def _populate(self, year):
        """
        Comprueba si una fecha es feriado o no
        
         Parametros
         ----------
         año: calle
             año de una fecha
         Devoluciones
         -------
         Devuelve verdadero si una fecha es un dia festivo, de lo contrario, se muestra como verdadero.
        """                              
        # día de Año Nuevo
        self[datetime.date(year, JAN, 1)] = "Año Nuevo "
        
        # Navidad
        self[datetime.date(year, DEC, 25)] = "Navidad "
        
        # Semana santa 
        self[easter(year) + rd(weekday=FR(-1))] = "Semana Santa (Viernes Santo) [Good Friday)]"
        self[easter(year)] = "Día de Pascuas "
        
        # Carnaval
        total_lent_days = 46
        self[easter(year) - datetime.timedelta(days=total_lent_days+2)] = "Lunes de carnaval "
        self[easter(year) - datetime.timedelta(days=total_lent_days+1)] = "Martes de carnaval "
        
        # Dia trabajador
        name = "Día Nacional del Trabajo "
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016 /R.O # 906)) Si el feriado cae en sábado o martes
        # el descanso obligatorio irá al viernes o lunes inmediato anterior
        # respectivamente
        if year > 2015 and datetime.date(year, MAY, 1).weekday() in (5,1):
            self[datetime.date(year, MAY, 1) - datetime.timedelta(days=1)] = name
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016/R.O # 906)) si el feriado cae en domingo
        # el descanso obligatorio sera para el lunes siguiente
        elif year > 2015 and datetime.date(year, MAY, 1).weekday() == 6:
            self[datetime.date(year, MAY, 1) + datetime.timedelta(days=1)] = name
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016 /R.O # 906)) Feriados que sean en miércoles o jueves
        # se moverá al viernes de esa semana
        elif year > 2015 and  datetime.date(year, MAY, 1).weekday() in (2,3):
            self[datetime.date(year, MAY, 1) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, MAY, 1)] = name
        
        #Batalla de Pichincha, las reglas son las mismas que el día del trabajo
        name = "Batalla del Pichincha [Pichincha Battle]"
        if year > 2015 and datetime.date(year, MAY, 24).weekday() in (5,1):
            self[datetime.date(year, MAY, 24).weekday() - datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, MAY, 24).weekday() == 6:
            self[datetime.date(year, MAY, 24) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, MAY, 24).weekday() in (2,3):
            self[datetime.date(year, MAY, 24) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, MAY, 24)] = name        
        
        # First Cry of Independence, the rules are the same as the labor day
        name = "Primer Grito de la Independencia "
        if year > 2015 and datetime.date(year, AUG, 10).weekday() in (5,1):
            self[datetime.date(year, AUG, 10)- datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, AUG, 10).weekday() == 6:
            self[datetime.date(year, AUG, 10) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, AUG, 10).weekday() in (2,3):
            self[datetime.date(year, AUG, 10) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, AUG, 10)] = name       
        
        # Independencia de Guayaquil, las reglas son las mismas que el día del trabajo
        name = "Independencia de Guayaquil "
        if year > 2015 and datetime.date(year, OCT, 9).weekday() in (5,1):
            self[datetime.date(year, OCT, 9) - datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, OCT, 9).weekday() == 6:
            self[datetime.date(year, OCT, 9) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, MAY, 1).weekday() in (2,3):
            self[datetime.date(year, OCT, 9) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, OCT, 9)] = name        
        
        # Day of the Dead and
        namedd = "Día de los difuntos " 
        # Independence of Cuenca
        nameic = "Independencia de Cuenca "
        #(Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016/R.O # 906))
        #Para festivos nacionales y/o locales que coincidan en días corridos,
        #se aplicarán las siguientes reglas:
        if (datetime.date(year, NOV, 2).weekday() == 5 and  datetime.date(year, NOV, 3).weekday() == 6):
            self[datetime.date(year, NOV, 2) - datetime.timedelta(days=1)] = namedd
            self[datetime.date(year, NOV, 3) + datetime.timedelta(days=1)] = nameic     
        elif (datetime.date(year, NOV, 3).weekday() == 2):
            self[datetime.date(year, NOV, 2)] = namedd
            self[datetime.date(year, NOV, 3) - datetime.timedelta(days=2)] = nameic
        elif (datetime.date(year, NOV, 3).weekday() == 3):
            self[datetime.date(year, NOV, 3)] = nameic
            self[datetime.date(year, NOV, 2) + datetime.timedelta(days=2)] = namedd
        elif (datetime.date(year, NOV, 3).weekday() == 5):
            self[datetime.date(year, NOV, 2)] =  namedd
            self[datetime.date(year, NOV, 3) - datetime.timedelta(days=2)] = nameic
        elif (datetime.date(year, NOV, 3).weekday() == 0):
            self[datetime.date(year, NOV, 3)] = nameic
            self[datetime.date(year, NOV, 2) + datetime.timedelta(days=2)] = namedd
        else:
            self[datetime.date(year, NOV, 2)] = namedd
            self[datetime.date(year, NOV, 3)] = nameic  
            
       # Fundación de Quito, aplica solo para la provincia de Pichincha,
        # las reglas son las mismas que el día del trabajo
        name = "Fundación de Quito "        
        if self.prov in ("EC-P"):
            if year > 2015 and datetime.date(year, DEC, 6).weekday() in (5,1):
                self[datetime.date(year, DEC, 6) - datetime.timedelta(days=1)] = name
            elif year > 2015 and datetime.date(year, DEC, 6).weekday() == 6:
                self[(datetime.date(year, DEC, 6).weekday()) + datetime.timedelta(days=1)] =name
            elif year > 2015 and  datetime.date(year, DEC, 6).weekday() in (2,3):
                self[datetime.date(year, DEC, 6) + rd(weekday=FR)] = name
            else:
                self[datetime.date(year, DEC, 6)] = name

class PicoPlaca:
    """
    Una clase para representar un vehículo.
    medida de restricción (Pico y Placa)
    - ORDENANZA METROPOLITANA N° 0305
    http://www7.quito.gob.ec/mdmq_ordenanzas/Ordenanzas/ORDENANZAS%20A%C3%91OS%20ANTERIORES/ORDM-305-%20%20CIRCULACION%20VEHICULAR%20PICO%20Y%20PLACA.pdf
    ...
    Atributos
    ----------
    placa : calle
        El registro o patente de un vehículo es una combinación de caracteres alfabéticos o numéricos
        caracteres que identifican e individualizan el vehículo respecto de los demás;
        
        El formato utilizado es
        XX-YYYY o XXX-YYYY,
        donde X es una letra mayúscula e Y es un dígito.
    fecha: calle
        Fecha en la que el vehículo pretende transitar
        esta siguiendo el
        Formato ISO 8601 AAAA-MM-DD: por ejemplo, 2020-04-22.
    tiempo: calle
        tiempo en que el vehículo pretende transitar
        esta siguiendo el formato
        HH:MM: por ejemplo, 08:35, 19:30
    en línea: booleano, opcional
        si en línea == Verdadero, se utilizará la API de días festivos abstractos
    Métodos
    -------
    __init__(self, plate, date, time, online=False):
        Construye todos los atributos necesarios.
        para el objeto PicoPlaca.
    plato (uno mismo):
        Obtiene el valor del atributo de placa
    placa (auto, valor):
        Establece el valor del atributo de la placa
    fecha (uno mismo):
        Obtiene el valor del atributo de fecha
    fecha (auto, valor):
        Establece el valor del atributo de fecha
    tiempo (uno mismo):
        Obtiene el valor del atributo de tiempo
    tiempo (uno mismo, valor):
        Establece el valor del atributo de tiempo
    __find_day(yo, fecha):
        Devuelve el día a partir de la fecha: por ejemplo, miércoles
    __is_forbidden_time(self, check_time):
        Devuelve True si el tiempo proporcionado está dentro de las horas pico prohibidas, de lo contrario, False
    __es_vacaciones:
        Devuelve True si la fecha marcada (en formato ISO 8601 AAAA-MM-DD) es un día festivo en Ecuador, de lo contrario, False
    predecir (auto):
        Devuelve True si el vehículo con la placa especificada puede estar en la carretera en la fecha y hora especificadas, de lo contrario, False
    """
    
    #Días de la semana
    __days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"]

    # Diccionario que contiene las restricciones en la forma {día: último dígito prohibido}
    __restrictions = {
            "Monday": [1, 2],
            "Tuesday": [3, 4],
            "Wednesday": [5, 6],
            "Thursday": [7, 8],
            "Friday": [9, 0],
            "Saturday": [],
            "Sunday": []}

    def __init__(self, plate, date, time, online=False):
        """
        Construye todos los atributos necesarios para el objeto PicoPlaca.
        
         Parametros
         ----------
             placa : calle
                 El registro o patente de un vehiculo es una combinacion de caracteres alfabeticos o numericos
                 caracteres que identifican e individualizan el vehiculo respecto de los demas;
                 El formato utilizado es AA-YYYY o XXX-YYYY, donde X es una letra mayuscula e Y es un digito.
             fecha: calle
                 Fecha en la que el vehiculo pretende transitar
                 Sigue el formato ISO 8601 AAAA-MM-DD: por ejemplo, 2020-04-22.
             tiempo: calle
                 tiempo en que el vehiculo pretende transitar
                 Sigue el formato HH:MM: por ejemplo, 08:35, 19:30
             en linea: booleano, opcional
                 si en linea == Verdadero, se usar la API de dias festivos abstractos (el valor predeterminado es Falso)               
        """                  
        self.plate = plate
        self.date = date
        self.time = time
        self.online = online


    @property
    def plate(self):
        """Obtiene el valor del atributo de placa"""
        return self._plate


    @plate.setter
    def plate(self, value):
        """
        Sets(Establece) evalúa el atributo placa
         Par metros
         ----------
         valor: cadena
        
         aumenta
         ------
         ValorError
             Si la cadena de valor no tiene el formato
             XX-AAAA o XXX-AAAA,
             donde X es una letra may scula e Y es un d gito
        """
        if not re.match('^[A-Z]{2,3}-[0-9]{4}$', value):
            raise ValueError(
                'La placa debe tener el siguiente formato: XX-YYYY o XXX-YYYY, donde X es una letra mayúscula e Y es un dígito')
        self._plate = value


    @property
    def date(self):
        """Obtiene el valor del atributo de fecha"""
        return self._date


    @date.setter
    def date(self, value):
        """
        Establece el valor del atributo de fecha
        Parámetros
        ----------
        valor: cadena
        
        aumenta
        ------
        ValorError
            Si la cadena de valor no tiene el formato AAAA-MM-DD (por ejemplo, 2021-04-02)
        """
        try:
            if len(value) != 10:
                raise ValueError
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                'La fecha debe tener el siguiente formato: AAAA-MM-DD (por ejemplo: 2021-04-02)') from None
        self._date = value
        

    @property
    def time(self):
        """Obtiene el valor del atributo de tiempo"""
        return self._time


    @time.setter
    def time(self, value):
        """
        Establece el valor del atributo de tiempo
        Parámetros
        ----------
        valor: cadena
        
        aumenta
        ------
        ValorError
            Si la cadena de valor no tiene el formato HH:MM (por ejemplo, 08:31, 14:22, 00:01)
        """
        if not re.match('^([01][0-9]|2[0-3]):([0-5][0-9]|)$', value):
            raise ValueError(
               'La hora debe tener el siguiente formato: HH:MM (por ejemplo, 08:31, 14:22, 00:01)')
        self._time = value


    def __find_day(self, date):
        """
        Encuentra el día a partir de la fecha: por ejemplo, miércoles
        Parámetros
        ----------
        fecha: calle
            Está siguiendo el formato ISO 8601 AAAA-MM-DD: por ejemplo, 2020-04-22
        Devoluciones
        -------
        Devuelve el día a partir de la fecha como una cadena
        """
        d = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
        return self.__days[d]


    def __is_forbidden_time(self, check_time):
        """
        Comprueba si el tiempo proporcionado está dentro de las horas pico prohibidas,
        donde las horas pico son: 07:00 - 09:30 y 16:00 - 19:30
        Parámetros
        ----------
        check_time : str
            Tiempo que se comprobará. Está en formato HH:MM: por ejemplo, 08:35, 19:15
        Devoluciones
        -------
        Devuelve True si el tiempo proporcionado está dentro de las horas pico prohibidas, de lo contrario, False
        """
        t = datetime.datetime.strptime(check_time, '%H:%M').time()
        return ((t >= datetime.time(7, 0) and t <= datetime.time(9, 30)) or
                (t >= datetime.time(16, 0) and t <= datetime.time(19, 30)))


    def __is_holiday(self, date, online):
        """
        Comprueba si la fecha (en formato ISO 8601 AAAA-MM-DD) es un día festivo en Ecuador
        si en línea == Verdadero, utilizará una API REST, de lo contrario, generará los días festivos del año examinado
        
        Parámetros
        ----------
        fecha: calle
            Está siguiendo el formato ISO 8601 AAAA-MM-DD: por ejemplo, 2020-04-22
        en línea: booleano, opcional
            si en línea == Verdadero, se utilizará la API de días festivos abstractos
        Devoluciones
        -------
        Devuelve True si la fecha marcada (en formato ISO 8601 AAAA-MM-DD) es un día festivo en Ecuador, de lo contrario, False
        """
        y, m, d = date.split('-')

        if online:
            # abstractapi Holidays API, free version: 1000 requests per month
            # 1 request per second
            # retrieve API key from enviroment variable
            key = os.environ.get('HOLIDAYS_API_KEY')
            response = requests.get(
                "https://holidays.abstractapi.com/v1/?api_key={}&country=EC&year={}&month={}&day={}".format(key, y, m, d))
            if (response.status_code == 401):
                # This means there is a missing API key
                raise requests.HTTPError(
                    'Falta la clave API. Guarde su clave en la variable de entorno HOLIDAYS_API_KEY')
            if response.content == b'[]':  # if there is no holiday we get an empty array
                return False
            # Fix Maundy Thursday incorrectly denoted as holiday
            if json.loads(response.text[1:-1])['name'] == 'Maundy Thursday':
                return False
            return True
        else:
            ecu_holidays = HolidayEcu(prov='EC-P')
            return date in ecu_holidays


    def predecir(self):
        """
        Comprueba si el vehículo con la placa especificada puede estar en la carretera en la fecha y hora proporcionada según las reglas de Pico y Placa:
        http://www7.quito.gob.ec/mdmq_ordenanzas/Ordenanzas/ORDENANZAS%20A%C3%91OS%20ANTERIORES/ORDM-305-%20%20CIRCULACION%20VEHICULAR%20PICO%20Y%20PLACA.pdf
        Devoluciones
        -------
        Devoluciones
        Verdadero si el vehículo con
        la placa especificada puede estar en el camino
        en la fecha y hora especificadas, de lo contrario Falso
        """
        # Check if date is a holiday
        if self.__is_holiday(self.date, self.online):
            return True

        # Check for restriction-excluded vehicles according to the second letter of the plate or if using only two letters
        # https://es.wikipedia.org/wiki/Matr%C3%ADculas_automovil%C3%ADsticas_de_Ecuador
        if self.plate[1] in 'AUZEXM' or len(self.plate.split('-')[0]) == 2:
            return True

        # Check if provided time is not in the forbidden peak hours
        if not self.__is_forbidden_time(self.time):
            return True

        day = self.__find_day(self.date)  # Find day of the week from date
        # Check if last digit of the plate is not restricted in this particular day
        if int(self.plate[-1]) not in self.__restrictions[day]:
            return True

        return False


if __name__ == '__main__':
    enlinea=False
    #Ingreso de datos lo que es la placa, fecha y hora... respectando los devidos formatos
    print (" ----------------------------------------")
    print ("NOTA: X es una letra mayuscula e Y es un digito")
    placa=input("Ingrese la placa por favor: ")
    print (" ----------------------------------------")
    fecha=input("Ingrese la fecha por favor, AAAA-MM-DD: ")
    print (" ----------------------------------------")
    hora=input("Ingrese la hora por favor, HH:MM:  ")
    print (" ----------------------------------------")

    pyp = PicoPlaca(placa, fecha, hora, enlinea)
  #En esta parte se muestra el vehiculo y su placa respectiva la cual puede o no 
  #estar en carretera con fecha y de que hora a que hora 
    if pyp.predecir():
        print(
            'EL VEHICULO CON LA SIGUIENTE PLACA: {} PUEDE CIRCULAR EL {} A LAS {}.'.format(
                placa,
                fecha,
                hora))
    else:
        print(
            'ESTE VEHICULO {} NO PUEDE CIRCULAR EL {} A LAS {}.'.format(
                placa,
                fecha,
                hora))