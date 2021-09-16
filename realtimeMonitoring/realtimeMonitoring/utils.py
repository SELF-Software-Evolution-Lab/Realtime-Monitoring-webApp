
from realtimeGraph.models import Role, User
from django.contrib.auth.models import User as AuthUser
from ldap3 import Server, Connection, ALL, SUBTREE, Tls, NTLM
import ssl
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
                     Error users: {error_count}, Total success: \
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
