
from realtimeGraph.models import Role, User, Data
from django.contrib.auth.models import User as AuthUser
from ldap3 import Server, Connection, ALL, SUBTREE, Tls, NTLM
from django_cron import CronJobBase, Schedule
from datetime import datetime
import ssl
import time
import os
import requests
from . import settings


def register_users():
    registered_count = 0
    registering_count = 0
    error_count = 0

    print('Utils: Registering users...')

    with open(settings.BASE_DIR / "users.pwd", "r") as users_file:
        lines = users_file.readlines()
        for line in lines:
            [login, passwd] = line.split(':')
            login = login.strip()
            passwd = passwd.strip()
            try:
                role = Role.objects.get(name="USER")
                userDB, userCreated = User.objects.get_or_create(login=login, defaults={
                    'email': login + '@uniandes.edu.co',
                    'password': passwd,
                    'role': role,
                })
                userAuth = AuthUser.objects.get(username=login)
                registered_count += 1
            except AuthUser.DoesNotExist:
                AuthUser.objects.create_user(
                    login, login + '@uniandes.edu.co', passwd)
                registering_count += 1
            except Exception as e:
                print(f'Error registering u: {login}. Error: {e}')
                error_count += 1
        print('Utils: Users registered.')
        print(
            f'Utils: Already users: {registered_count}, \
                 Registered users: {registering_count}, \
                     Error use rs: {error_count}, Total success: \
                         {registered_count+ registering_count}'
        )


def ldap_login(username, password):
    msg = ""
    try:
        user = 'uniandes.edu.co\\' + username.strip()
        ldap_user_pwd = password.strip()
        tls_configuration = Tls(validate=ssl.CERT_REQUIRED,
                                version=ssl.PROTOCOL_TLSv1_2)
        server = Server('ldap://adua.uniandes.edu.co:389',
                        use_ssl=True, tls=tls_configuration)
        conn = Connection(server, user=user, password=ldap_user_pwd, authentication=NTLM,
                          auto_referrals=False)
        data = conn.bind()
        if not data:
            print(f"LDAP: Login error: {conn.last_error} ")
            msg = str(conn.last_error) + " conn error"
        else:
            print('LDAP: Login successful')
            conn.unbind()
            return True, "Success"
    except Exception as e:
        print('LDAP: Error: ', e)
        msg = str(e) + " Exception"
    return False, msg


def getCityCoordinates(nameParam: str):
    lat = None
    lon = None
    name = ' '.join(nameParam.split('_'))
    r = requests.get(
        "http://api.positionstack.com/v1/forward?access_key=0696170f684f55b08c5c4fca694fd70c&query=" + str(name))
    if r.status_code == 200:
        data = r.json().get('data', None)
        if data != None and len(data) > 0:
            lat = data[0]['latitude']
            lon = data[0]['longitude']
    return lat, lon


def writeDataCSVFile():
    print("Getting time for csv req")
    startT = time.time()
    print('####### VIEW #######')
    print('Processing CSV')
    data = Data.objects.all().order_by("created_at")
    filepath = settings.BASE_DIR / \
        "realtimeMonitoring/static/data/datos-historicos-iot.csv"

    with open(filepath, 'w', encoding='utf-8') as data_file:
        print("Filename:", filepath)
        headers = ['Usuario', 'Ciudad', 'Fecha', 'Variable', 'Medición']
        data_file.write(','.join(headers) + '\n')
        print("CSV: Head written")
        print("CSV: Len of data:", len(data))
        lines = ""
        for measure in data:
            usuario, ciudad, fecha, variable, medicion = 'NA', 'NA', 'NA', 'NA', 'NA'
            try:
                usuario = measure.station.user.login
            except:
                pass
            try:
                ciudad = measure.station.city.name
            except:
                pass
            try:
                fecha = measure.created_at.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            try:
                variable = measure.measurement.name
            except:
                pass
            medicion = measure.value
            lines += ','.join([usuario, ciudad, fecha,
                              variable, str(medicion)]) + '\n'
        data_file.write(lines)
    endT = time.time()
    print("Processed CSV file. Time: ", endT - startT)


def updateCSVFile():
    filepath = settings.BASE_DIR / \
        "realtimeMonitoring/static/data/datos-historicos-iot.csv"
    last_date = datetime.now()
    with open(filepath, 'rb') as data_file:
        last_register = getLastLine(data_file).strip()
        strDate = last_register.split(",")[2]
        last_date = datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')
    new_data = Data.objects.filter(
        created_at__gt=last_date, created_at__lte=datetime.now())
    print("New data: ", len(new_data))
    with open(filepath, 'a', encoding='utf-8') as data_file:
        lines = ""
        for measure in new_data:
            usuario, ciudad, fecha, variable, medicion = 'NA', 'NA', 'NA', 'NA', 'NA'
            try:
                usuario = measure.station.user.login
            except:
                pass
            try:
                ciudad = measure.station.city.name
            except:
                pass
            try:
                fecha = measure.created_at.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            try:
                variable = measure.measurement.name
            except:
                pass
            medicion = measure.value
            lines += ','.join([usuario, ciudad, fecha,
                              variable, str(medicion)]) + '\n'
        data_file.write(lines)


class UpdateCSVCron(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'realtimeMonitoring.updateCSVCronJob'

    def do(self):
        updateCSVFile()


def getLastLine(file):
    try:  # catch OSError in case of a one line file
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR)
    except OSError:
        file.seek(0)
    last_line = file.readline().decode()
    return last_line
