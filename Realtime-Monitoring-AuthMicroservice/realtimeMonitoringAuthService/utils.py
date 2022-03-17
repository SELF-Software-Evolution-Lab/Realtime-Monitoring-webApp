from django.utils.timezone import activate
from realtimeMonitoringAuthService.models import (
    Role,
    User,
    Data,
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
