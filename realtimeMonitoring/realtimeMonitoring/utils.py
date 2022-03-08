from django.utils.timezone import activate
from realtimeGraph.models import (
    Measurement,
    Role,
    Station,
    User,
    Data,
    State,
    City,
    Country,
    Location,
)
from django.contrib.auth.models import User as AuthUser
from django.db.models import Max, Sum
from ldap3 import Server, Connection, ALL, SUBTREE, Tls, NTLM
from django_cron import CronJobBase, Schedule
from datetime import datetime, timedelta
import datetime as datetimelib
import ssl
import random
import time
import os
import requests

from . import settings

"""
Registra los usuarios que están en users.pwd (en la carpeta raíz del proyecto) en el sistema.
Por cada usuario, el sistema crea el objeto User, luego crea un usuario en el sistema de 
autenticación de Django con usuario login y la contraseña MQTT descrita en el archivo users.pwd.
"""


def register_users():
    registered_count = 0
    registering_count = 0
    error_count = 0

    print("Utils: Registering users...")

    with open(settings.BASE_DIR / "users.pwd", "r") as users_file:
        lines = users_file.readlines()
        for line in lines:
            [login, passwd] = line.split(":")
            login = login.strip()
            passwd = passwd.strip()
            try:
                role, created = Role.objects.get_or_create(
                    name="USER", active=True)
                userDB, userCreated = User.objects.get_or_create(
                    login=login,
                    defaults={
                        "email": login + "@uniandes.edu.co",
                        "password": passwd,
                        "role": role,
                    },
                )
                userAuth = AuthUser.objects.get(username=login)
                registered_count += 1
            except AuthUser.DoesNotExist:
                AuthUser.objects.create_user(
                    login, login + "@uniandes.edu.co", passwd)
                registering_count += 1
            except Exception as e:
                print(f"Error registering u: {login}. Error: {e}")
                error_count += 1
        print("Utils: Users registered.")
        print(
            f"Utils: Already users: {registered_count}, \
                 Registered users: {registering_count}, \
                     Error use rs: {error_count}, Total success: \
                         {registered_count+ registering_count}"
        )


"""
Presta el servicio de login al sistema ldap de la universidad.
Esta función sólo confirma que el usuario y la contraseña son correctos o no.
Sólo funciona si el códido es ejecutado dentro de la red de la universidad.
"""


def ldap_login(username, password):
    msg = ""
    try:
        user = "uniandes.edu.co\\" + username.strip()
        ldap_user_pwd = password.strip()
        tls_configuration = Tls(
            validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2
        )
        server = Server(
            "ldap://adua.uniandes.edu.co:389", use_ssl=True, tls=tls_configuration
        )
        conn = Connection(
            server,
            user=user,
            password=ldap_user_pwd,
            authentication=NTLM,
            auto_referrals=False,
        )
        data = conn.bind()
        if not data:
            print(f"LDAP: Login error: {conn.last_error} ")
            msg = str(conn.last_error) + " conn error"
        else:
            print("LDAP: Login successful")
            conn.unbind()
            return True, "Success"
    except Exception as e:
        print("LDAP: Error: ", e)
        msg = str(e) + " Exception"
    return False, msg


"""
Servicio para conseguir las coordenadas de un lugar (nombre) usando PositionStack.
"""


def getCityCoordinates(nameParam: str):
    lat = None
    lng = None
    name = " ".join(nameParam.split("_"))
    r = requests.get(
        "http://api.positionstack.com/v1/forward?access_key=0696170f684f55b08c5c4fca694fd70c&query="
        + str(name)
    )
    if r.status_code == 200:
        data = r.json().get("data", None)
        if data != None and len(data) > 0:
            lat = data[0]["latitude"]
            lng = data[0]["longitude"]
    return lat, lng


"""
Crea y escribe el archivo CSV para descarga.
Se escribe en el archivo todos los registros que están en la base de datos actualmente.
Para una gran cantidad de registros toma mucho tiempo.
Ejecutar sólo la primera vez, luego usar updateCSV.
"""


def writeDataCSVFile():
    print("Getting time for csv req")
    startT = time.time()
    print("####### VIEW #######")
    print("Processing CSV")
    data = Data.objects.all().order_by("time")
    filepath = (
        settings.BASE_DIR / "realtimeMonitoring/static/data/datos-historicos-iot.csv"
    )

    with open(filepath, "w", encoding="utf-8") as data_file:
        print("Filename:", filepath)
        headers = [
            "Usuario",
            "Ciudad",
            "Estado",
            "País",
            "Fecha",
            "Variable",
            "Medición",
        ]
        data_file.write(",".join(headers) + "\n")
        print("CSV: Head written")
        print("CSV: Len of data:", len(data))
        lines = ""
        for measure in data:
            usuario, ciudad, estado, pais, fecha, variable, medicion = (
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
            )
            try:
                usuario = measure.station.user.login
            except:
                pass
            try:
                ciudad = measure.station.location.city.name
                estado = measure.station.location.state.name
                pais = measure.station.location.country.name
            except:
                pass
            try:
                fecha = measure.time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            try:
                variable = measure.measurement.name
            except:
                pass
            medicion = measure.value
            lines += (
                ",".join(
                    [usuario, ciudad, estado, pais,
                        fecha, variable, str(medicion)]
                )
                + "\n"
            )
        data_file.write(lines)
    endT = time.time()
    print("Processed CSV file. Time: ", endT - startT)


"""
Actualiza el archivo CSV para descargar.
Lee el último registro y escribe los registros faltantes a la fecha.
"""


def updateCSVFile():
    filepath = (
        settings.BASE_DIR / "realtimeMonitoring/static/data/datos-historicos-iot.csv"
    )
    last_date = datetime.now()
    with open(filepath, "rb") as data_file:
        last_register = getLastLine(data_file).strip()
        strDate = last_register.split(",")[4]
        last_date = datetime.strptime(strDate, "%Y-%m-%d %H:%M:%S")
        last_date = last_date + datetimelib.timedelta(0, 1)
    new_data = Data.objects.filter(
        time__gt=last_date, time__lte=datetime.now())
    print("New data: ", len(new_data))
    with open(filepath, "a", encoding="utf-8") as data_file:
        lines = ""
        for measure in new_data:
            usuario, ciudad, estado, pais, fecha, variable, medicion = (
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
            )
            try:
                usuario = measure.station.user.login
            except:
                pass
            try:
                ciudad = measure.station.location.city.name
                estado = measure.station.location.state.name
                pais = measure.station.location.country.name
            except:
                pass
            try:
                fecha = measure.time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            try:
                variable = measure.measurement.name
            except:
                pass
            medicion = measure.value
            lines += (
                ",".join(
                    [usuario, ciudad, estado, pais,
                        fecha, variable, str(medicion)]
                )
                + "\n"
            )
        data_file.write(lines)


"""
Crea una medición en la base de datos.
Se usa para la importación de los datos desde CSV.
"""


def saveMeasure(user: str, city: str, date: datetime, variable: str, measure: float):
    from realtimeGraph.views import (
        create_data_with_date,
        get_or_create_location,
        get_or_create_location_only_city,
        get_or_create_measurement,
        get_or_create_user,
        get_or_create_station,
        create_data,
    )

    try:
        user_obj = get_or_create_user(user)
        location_obj = get_or_create_location_only_city(city)
        unit = "°C" if str(variable).lower() == "temperatura" else "%"
        variable_obj = get_or_create_measurement(variable, unit)
        sensor_obj = get_or_create_station(user_obj, location_obj)
        create_data_with_date(measure, sensor_obj, variable_obj, date)
    except Exception as e:
        print("ERROR saving measure: ", e)


"""
Función para importar los datos del archivo input.csv en la raíz del proyecto.
"""


def loadCSV():
    filepath = settings.BASE_DIR / "input.csv"
    with open(filepath, "r") as data_file:
        lines = data_file.readlines()
        lon = len(lines)
        count = 1
        print("CSV length: ", lon)
        for line in lines[1:]:
            print("Reg ", count, "of", lon)
            usuario, ciudad, fecha, variable, medicion = line.split(",")
            date = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
            saveMeasure(
                user=usuario,
                city=ciudad,
                date=date,
                variable=variable,
                measure=float(medicion),
            )


"""
Clase cron para actualizar el CSV cada cierto tiempo
"""


class UpdateCSVCron(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "realtimeMonitoring.updateCSVCronJob"

    def do(self):
        updateCSVFile()


"""
Función auxiliar para obtener la última linea de un archivo.
"""


def getLastLine(file):
    try:  # catch OSError in case of a one line file
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b"\n":
            file.seek(-2, os.SEEK_CUR)
    except OSError:
        file.seek(0)
    last_line = file.readline().decode()
    return last_line


"""
Función para generar datos ficticios para poblar el sistema.
Se usa para hacer pruebas de carga.
"""


def generateMockData(quantity: int = 500000):
    from realtimeGraph.views import create_data

    print("Starting generation of {} data...".format(quantity))

    query_len = Data.objects.aggregate(Sum("length"))
    print("Query len:", query_len)
    data_len = query_len["length__sum"] or 0

    print("Data in database:", data_len)

    if data_len > quantity:
        print("Mock data already generated.")
        return

    measure1, created = Measurement.objects.get_or_create(
        name="Temperatura", unit="°C")
    measure2, created = Measurement.objects.get_or_create(
        name="Humedad", unit="%")

    role, created = Role.objects.get_or_create(name="TEST")

    user1, created = User.objects.get_or_create(login="userMock1", role=role)
    user2, created = User.objects.get_or_create(login="userMock2", role=role)

    city1, created = City.objects.get_or_create(name="Ciudad1")
    city2, created = City.objects.get_or_create(name="Ciudad2")

    state1, created = State.objects.get_or_create(name="Estado1")
    state2, created = State.objects.get_or_create(name="Estado2")

    country1, created = Country.objects.get_or_create(name="Pais1")
    country2, created = Country.objects.get_or_create(name="Pais2")

    location1, created = Location.objects.get_or_create(
        city=city1, state=state1, country=country1, lat=4.7110, lng=74.0721
    )
    location2, created = Location.objects.get_or_create(
        city=city2, state=state2, country=country2, lat=19.4326, lng=99.1332
    )

    station1, created = Station.objects.get_or_create(
        user=user1, location=location1)
    station2, created = Station.objects.get_or_create(
        user=user2, location=location2)

    stations = []
    measures = []
    data_per_day = 20000
    initial_date = "20/06/2021"
    interval = ((24 * 60 * 60 * 1000) / data_per_day) // 1

    print("Init date: ", initial_date)
    print("Data per day: ", data_per_day)
    print("Interval (milliseconds):", interval)

    stations = Station.objects.all()
    measures = Measurement.objects.all()
    print("Total stations:", len(stations))
    print("Total measures:", len(measures))

    if data_len > 0:
        cd_query = Data.objects.aggregate(Max("base_time"))
        current_date = cd_query["base_time__max"]
        current_date = current_date + timedelta(hours=1)
    else:
        current_date = datetime.strptime(initial_date, "%d/%m/%Y")

    count = data_len if data_len != None else 0

    while count <= quantity:
        rand_station = random.randint(0, len(stations) - 1)
        rand_measure = random.randint(0, len(measures) - 1)
        station = stations[rand_station]
        measure = measures[rand_measure]
        data = random.random() * 40
        create_data(data, station, measure, current_date)
        print("Data created:", count, current_date.timestamp())
        count += 1
        current_date += timedelta(milliseconds=interval)

    print("Finished. Total data:", count, "Last date:", current_date)
