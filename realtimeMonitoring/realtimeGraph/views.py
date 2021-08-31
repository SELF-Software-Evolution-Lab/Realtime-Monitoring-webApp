from datetime import datetime
import json
from typing import Dict

from django.template.defaulttags import register
from django.contrib.auth import login, logout
from realtimeGraph.forms import LoginForm
from django.http import JsonResponse
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import render
from random import randint
from .models import City, Data, Measurement, Rol, Station, User
import dateutil.relativedelta
from django.db.models import Avg, Max, Min, Sum


class DashboardView(TemplateView):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, 'index.html', self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        context = {}

        userParam = self.request.user.username
        cityParam = self.request.GET.get('city', None)

        if cityParam == None:
            user = User.objects.get(login=userParam)
            station = Station.objects.get(user=user)
            if station != None:
                cityParam = station.city.name

        context["data"] = self.get_last_week_data(userParam, cityParam)
        context["selectedCity"] = City.objects.get(name=cityParam)
        context["measurements"] = self.get_measurements(userParam, cityParam)
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_measurements(sself, user, city):
        userO = User.objects.get(login=user)
        cityO = City.objects.get(name=city)
        if userO == None or cityO == None:
            raise 'No existe el usuario o ciudad indicada'
        stationO = Station.objects.get(user=userO, city=cityO)
        if stationO == None:
            raise 'No hay datos para esa ubicación'
        datas = Data.objects.filter(station=stationO)
        measurementsO = set([data.measurement for data in datas])
        return measurementsO

    def get_last_week_data(self, user, city):
        result = {}
        start = datetime.now()
        start = start - \
            dateutil.relativedelta.relativedelta(
                days=1)
        try:
            userO = User.objects.get(login=user)
            cityO = City.objects.get(name=city)
            if userO == None or cityO == None:
                raise 'No existe el usuario o ciudad indicada'
            stationO = Station.objects.get(user=userO, city=cityO)
            if stationO == None:
                raise 'No hay datos para esa ubicación'
            datas = Data.objects.filter(station=stationO)
            measurementsO = set([data.measurement for data in datas])
            for measure in measurementsO:
                raw_data = Data.objects.filter(
                    station=stationO, measurement=measure, created_at__gte=start.date()).order_by('-created_at')[:50]
                data = [[(d.toDict()['created_at'].timestamp() *
                          1000) // 1, d.toDict()['value']] for d in raw_data]
                result[measure.name] = {
                    'data': data,
                    'min': raw_data.aggregate(
                        Min('value'))['value__min'],
                    'max': raw_data.aggregate(
                        Max('value'))['value__max'],
                    'avg': round(raw_data.aggregate(
                        Avg('value'))['value__avg'], 2),
                }
        except Exception as error:
            print('Error en consulta de datos:', error)

        return result

    def post(self, request, *args, **kwargs):
        data = {}
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        try:
            body = json.loads(request.body.decode("utf-8"))
            action = body['action']
            print('action:', action)
            userParam = self.request.user.username
            if action == 'get_data':
                cityName = body['city']
                data['result'] = self.get_last_week_data(userParam, cityName)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


def get_or_create_rol(name):
    try:
        rol = Rol.objects.get(name=name)
    except Rol.DoesNotExist:
        rol = Rol(name=name)
        rol.save()
    return(rol)


def get_or_create_user(login):
    try:
        user = User.objects.get(login=login)
    except User.DoesNotExist:
        rol = Rol.objects.get(name="USER")
        user = User(login=login, rol=rol, )
        user.save()
    return(user)


def get_or_create_city(name):
    try:
        city = City.objects.get(name=name)
    except City.DoesNotExist:
        city = City(name=name)
        city.save()
    return(city)


def get_or_create_station(user, city):
    try:
        station = Station.objects.get(user=user, city=city)
    except Station.DoesNotExist:
        station = Station(user=user, city=city)
        station.save()
    return(station)


def get_station(user, city):
    station = Station.objects.get(user=user, city=city)
    return(station)


def get_or_create_measurement(name, unit):
    try:
        measurement = Measurement.objects.get(name=name, unit=unit)
    except Measurement.DoesNotExist:
        measurement = Measurement(
            name=name, unit=unit)
        measurement.save()
    return(measurement)


def create_data(value, measurement, station):
    data = Data(value=value, measurement=measurement, station=station)
    data.save()
    return(data)


def get_last_measure(station, measurement):
    last_measure = Data.objects.filter(
        station=station, measurement=measurement).latest('created_at')
    print(last_measure.created_at)
    print(datetime.now())
    return(last_measure.value)


class LoginView(TemplateView):
    template_name = 'login.html'
    http_method_names = ['get', 'post']

    def post(self, request):
        form = LoginForm(request.POST or None)
        if request.POST and form.is_valid():
            user = form.login(request)
            if user:
                # print('User logged: ', user['email'])
                login(request, user)
                return HttpResponseRedirect("/")
        errors = ''
        for e in form.errors.values():
            errors += e[0]

        return render(request, 'login.html', {'errors': errors, 'username': form.cleaned_data['username'], 'password': form.cleaned_data['password'], })
        # print('User:', username)
        # print('Pass:', password)
        # return HttpResponse(, status=200)


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class HistoricalView(TemplateView):
    template_name = 'historical.html'

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        userParam = self.request.user.username
        cityParam = self.kwargs['city'] if 'city' in self.kwargs else None

        # Add in a QuerySet of all the users
        context['cities'] = City.objects.all()
        context['measurements'] = Measurement.objects.all()
        context['selectedUser'] = User.objects.get(login=userParam)
        if context['selectedUser'] != None:
            print('found user')
            stations = Station.objects.filter(
                user=context['selectedUser'])
            context['cities'] = [station.city for station in stations]
            if cityParam != None:
                print('found city param')
                context['selectedCity'] = City.objects.get(name=cityParam)
                if context['selectedCity'] != None:
                    print('found city')
                    datas = Data.objects.filter(station__in=stations)
                    station = Station.objects.get(
                        user=context['selectedUser'],
                        city=context['selectedCity']
                    )
                    context['measurements'] = set([
                        data.measurement for data in datas])
                    try:
                        start = datetime.fromtimestamp(
                            float(self.request.GET.get('from', None))/1000)
                    except:
                        start = None
                    try:
                        end = datetime.fromtimestamp(
                            float(self.request.GET.get('to', None))/1000)
                    except:
                        end = None
                    if start == None and end == None:
                        start = datetime.now()
                        start = start - \
                            dateutil.relativedelta.relativedelta(
                                months=1)
                        end = datetime.now()
                        end += dateutil.relativedelta.relativedelta(days=1)
                    elif end == None:
                        end = datetime.now()
                    elif start == None:
                        start = datetime.fromtimestamp(0)

                    context['data'] = {}

                    for measure in context['measurements']:
                        data = Data.objects.filter(
                            station=station, measurement=measure, created_at__gte=start.date(), created_at__lte=end.date())
                        contextData = [[(d.toDict()['created_at'].timestamp() * 1000) // 1, d.toDict()[
                            'value']] for d in data]
                        context['data'][measure.name] = {
                            'min': data.aggregate(
                                Min('value'))['value__min'],
                            'max': data.aggregate(
                                Max('value'))['value__max'],
                            'avg': round(data.aggregate(
                                Avg('value'))['value__avg'], 2),
                            'data': contextData
                        }
                    context['data'] = json.dumps(context['data'])

        return context


@ register.filter
def get_statistic(dictionary, key):
    if type(dictionary) == str:
        dictionary = json.loads(dictionary)
    if key is None:
        return None
    keys = [k.strip() for k in key.split(',')]
    return dictionary.get(keys[0]).get(keys[1])


@ register.filter
def add_str(str1, str2):
    return str1 + str2
