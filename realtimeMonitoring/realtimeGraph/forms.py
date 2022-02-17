from realtimeMonitoring import utils
from ldap3.utils.log import log
from realtimeGraph.models import User
from django import forms
from django.contrib.auth import authenticate, login


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    '''
    Process login intenta iniciar sesión al servidor ldap de la universidad.
    Sólo funciona si se está corriendo dentro de la red de la universidad.
    Para pruebas existe el usuario pruebasIOT con contraseña pruebas2021!
    Arroja excepciones si el usuario existe en la universidad pero no está registrado en el sistema de monitoreo o
    si existe algún otro error en el proceso
    '''

    def process_login(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        utils.ldap_login(username, password)
        # Username and password for testing
        if username == "pruebasIOT" and password == "pruebas2021!":
            username = "usertest1"
            logged_in = True
        user = None
        if logged_in:
            try:
                userDB = User.objects.get(login=username)
                user = authenticate(username=username,
                                    password=userDB.password)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "No estás registrado en el sistema de monitoreo. Comunícate con el profesor encargado.")
        if not user or not user.is_active:
            raise forms.ValidationError(
                "Los datos no son correctos. Revisa y vuelve a intentar.")
        return user

    def clean(self):
        self.process_login()
        return self.cleaned_data

    def login(self, request):
        user = self.process_login()
        return user
