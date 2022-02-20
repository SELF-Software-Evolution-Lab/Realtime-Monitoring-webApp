from datetime import datetime
import json
import time

from django.db.models.aggregates import Count
from realtimeMonitoring import utils
from typing import Dict
import requests
import uuid
import tempfile

from django.template.defaulttags import register
from django.contrib.auth import login, logout
from realtimeGraph.forms import LoginForm
from django.http import JsonResponse
from django.http.response import FileResponse, Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import render
from random import randint
from .models import City, Data, Measurement, Role, Station, User
from realtimeMonitoring import settings
import dateutil.relativedelta
from django.db.models import Avg, Max, Min, Sum


class DashboardView(TemplateView):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, 'index.html', self.get_context_data(**kwargs))
        #return render(request, 'no_data.html')

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        context = {}
        print("CONTEXT: getting context data")
        try:
            userParam = self.request.user.username
            cityParam = self.request.GET.get('city', None)
            print("CONTEXT: getting user and city: ", userParam, cityParam)
            if cityParam == None:
                user = User.objects.get(login=userParam)
                print("CONTEXT: getting user db: ", user)
                stations = Station.objects.filter(user=user)
                print("CONTEXT: getting stations db: ", stations)
                station = stations[0] if len(stations) > 0 else None
                print("CONTEXT: getting first station: ", station)
                if station != None:
                    cityParam = station.city.name
                else:
                    return context
            print("CONTEXT: getting last week data and measurements")
            context["data"], context["measurements"] = self.get_last_week_data(userParam, cityParam)
            print("CONTEXT: got last week data, now getting city: ", cityParam)
            context["selectedCity"] = City.objects.get(name=cityParam)
        except Exception as e:
            print("Error get_context_data. User: " + userParam, e)
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
        measurementsO = Measurement.objects.all()
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
            print("LAST_WEEK: Got user and city:", user, city)
            if userO == None or cityO == None:
                raise 'No existe el usuario o ciudad indicada'
            stationO = Station.objects.get(user=userO, city=cityO)
            print("LAST_WEEK: Got station:", user, city, stationO)
            if stationO == None:
                raise 'No hay datos para esa ubicación'
            print("LAST_WEEK: Filtering measures of ", stationO)
            datas = Data.objects.filter(station=stationO, created_at__gte=start).order_by('-created_at')[:100]
            print("LAST_WEEK: Filtered data: len ", len(datas))
            cnt = 0
            while len(datas) <= 0 and cnt < 3:
                start = start - \
                    dateutil.relativedelta.relativedelta(weeks=1)
                datas = Data.objects.filter(station=stationO, created_at__gte=start).order_by('-created_at')[:100]
                cnt += 1
            if len(datas) <= 0:
                start = datetime.fromtimestamp(0)
                datas = Data.objects.filter(station=stationO).order_by('-created_at')[:100]
            print("LAST_WEEK: Filtered data: len ", len(datas))
            measurementsO = set([data.measurement for data in datas])
            print("LAST_WEEK: Measurements got: ", measurementsO)
            for measure in measurementsO:
                print("LAST_WEEK: Filtering measure: ", measure)
                # created_at__gte=start.date() Filtro para último día
                raw_data = Data.objects.filter(station=stationO, created_at__gte=start, measurement=measure).order_by('-created_at')[:50]
                print("LAST_WEEK: Raw data: ", len(raw_data))
                data = [[(d.toDict()['created_at'].timestamp() *
                          1000) // 1, d.toDict()['value']] for d in raw_data]

                minVal = raw_data.aggregate(
                    Min('value'))['value__min']
                maxVal = raw_data.aggregate(
                    Max('value'))['value__max']
                avgVal = raw_data.aggregate(
                    Avg('value'))['value__avg']
                result[measure.name] = {
                    'min': minVal if minVal != None else 0,
                    'max': maxVal if maxVal != None else 0,
                    'avg': round(avgVal if avgVal != None else 0, 2),
                    'data': data
                }
        except Exception as error:
            print('Error en consulta de datos:', error)

        return result, measurementsO

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
                data['result'] = self.get_last_week_data(userParam, cityName)[0]
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


def get_or_create_role(name):
    try:
        role = Role.objects.get(name=name)
    except Role.DoesNotExist:
        role = Role(name=name)
        role.save()
    return(role)


def get_or_create_user(login):
    try:
        user = User.objects.get(login=login)
    except User.DoesNotExist:
        role = Role.objects.get(name="USER")
        user = User(login=login, role=role, )
        user.save()
    return(user)


def get_or_create_city(name):
    city, created = City.objects.get_or_create(name=name)
    if city.lat == None:
        lat, lon = utils.getCityCoordinates(name)
        city.lat = lat
        city.lon = lon
        city.save()
        
    return(city)


def get_or_create_station(user, city):
    station, created = Station.objects.get_or_create(user=user, city=city)
    return(station)


def get_station(user, city):
    station = Station.objects.get(user=user, city=city)
    return(station)


def get_or_create_measurement(name, unit):
    measurement, created = Measurement.objects.get_or_create(name=name, unit=unit)
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
            try:
                user = form.login(request)
                if user:
                    # print('User logged: ', user['email'])
                    login(request, user)
                    return HttpResponseRedirect("/")
            except Exception as e:
                print('Login error', e)
        errors = ''
        for e in form.errors.values():
            errors += str(e[0])

        return render(request, 'login.html', {'errors': errors, 'username': form.cleaned_data['username'], 'password': form.cleaned_data['password'], })


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class HistoricalView(TemplateView):
    template_name = 'historical.html'

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        userParam = self.request.user.username
        cityParam = self.kwargs['city'] if 'city' in self.kwargs else None

        # Add in a QuerySet of all the users
        # context['cities'] = City.objects.all()
        # context['measurements'] = Measurement.objects.all()
        context['selectedUser'] = User.objects.get(login=userParam)
        if context['selectedUser'] != None:
            stations = Station.objects.filter(
                user=context['selectedUser'])
            context['cities'] = [station.city for station in stations]
            if len(context['cities']) > 0 and cityParam == None:
                cityParam = context['cities'][0].name
            if cityParam != None:
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
                                weeks=1)
                        end = datetime.now()
                        end += dateutil.relativedelta.relativedelta(days=1)
                    elif end == None:
                        end = datetime.now()
                    elif start == None:
                        start = datetime.fromtimestamp(0)

                    context['data'] = {}

                    context['start'] = start.strftime(
                        "%d/%m/%Y") if start != None else " "
                    context['end'] = end.strftime(
                        "%d/%m/%Y") if end != None else " "

                    for measure in context['measurements']:
                        data = Data.objects.filter(
                            station=station, measurement=measure, created_at__gte=start.date(), created_at__lte=end.date())
                        contextData = [[(d.toDict()['created_at'].timestamp() * 1000) // 1, d.toDict()[
                            'value']] for d in data]
                        minVal = data.aggregate(
                            Min('value'))['value__min']
                        maxVal = data.aggregate(
                            Max('value'))['value__max']
                        avgVal = data.aggregate(
                            Avg('value'))['value__avg']
                        context['data'][measure.name] = {
                            'min': minVal if minVal != None else 0,
                            'max': maxVal if maxVal != None else 0,
                            'avg': round(avgVal if avgVal != None else 0, 2),
                            'data': contextData
                        }
                    context['data'] = json.dumps(context['data'])
        return context

class RemaView(TemplateView):
    template_name = 'rema.html'

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        measureParam = self.kwargs.get('measure', None)
        selectedMeasure = None
        measurements = Measurement.objects.all()

        if measureParam != None:
            selectedMeasure = Measurement.objects.filter(name=measureParam)[0]
        elif measurements.count() > 0:
            selectedMeasure = measurements[0]

        cities = City.objects.all()
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
                    weeks=1)
            end = datetime.now()
            end += dateutil.relativedelta.relativedelta(days=1)
        elif end == None:
            end = datetime.now()
        elif start == None:
            start = datetime.fromtimestamp(0)

        data = []

        for city in cities:
            stations = Station.objects.filter(city=city)
            cityData = Data.objects.filter(station__in=stations, measurement__name=selectedMeasure.name,  created_at__gte=start.date(), created_at__lte=end.date())
            if cityData.count() <= 0:
                continue
            minVal = cityData.aggregate(
                    Min('value'))['value__min']
            maxVal = cityData.aggregate(
                    Max('value'))['value__max']
            avgVal = cityData.aggregate(
                    Avg('value'))['value__avg']
            data.append({
                'name': city.name,
                'lat': city.lat,
                'lon': city.lon,
                'population': stations.count(),
                'min': minVal if minVal != None else 0,
                'max': maxVal if maxVal != None else 0,
                'avg': round(avgVal if avgVal != None else 0, 2),
            })

        startFormatted = start.strftime("%d/%m/%Y") if start != None else " "
        endFormatted = end.strftime("%d/%m/%Y") if end != None else " "

        context['measurements'] = measurements
        context['selectedMeasure'] = selectedMeasure
        context['cities'] = cities
        context['start'] = startFormatted
        context['end'] = endFormatted
        context['data'] = data

        return context

def download_csv_data(request):
    print("Getting time for csv req")
    startT = time.time()
    print('####### VIEW #######')
    print('Processing CSV')
    start, end = get_daterange(request)
    print("Start, end", start, end)
    data = Data.objects.filter(
        created_at__gte=start.date(), created_at__lte=end.date())
    print("Data ref got")
    tmpFile = tempfile.NamedTemporaryFile(delete=False)
    print("Creating file")
    filename = tmpFile.name

    with open(filename, 'w', encoding='utf-8') as data_file:
        print("Filename:", filename)
        headers = ['Usuario', 'Ciudad', 'Fecha', 'Variable', 'Medición']
        data_file.write(','.join(headers) + '\n')
        print("Head written")
        print("Len of data:", len(data))
        try:
            data_file.write(str(data))
        except Exception as e:
            print(e)
        # for measure in data:
        #     usuario, ciudad, fecha, variable, medicion = 'NA', 'NA', 'NA', 'NA', 'NA'
        #     try:
        #         usuario = measure.station.user.login
        #     except:
        #         pass
        #     try:
        #         ciudad = measure.station.city.name
        #     except:
        #         pass
        #     try:
        #         fecha = measure.created_at.strftime("%Y-%m-%d %H:%M:%S")
        #     except:
        #         pass
        #     try:
        #         variable = measure.measurement.name
        #     except:
        #         pass
        #     medicion = measure.value
        #     print("Writing: ", usuario, ciudad, fecha, variable, str(medicion))

        #     data_file.write(
        #         ','.join([usuario, ciudad, fecha, variable, str(medicion)]) + '\n')
    endT = time.time()
    print("##### VIEW ######")
    print("Processed. Time: ", endT - startT)

    return FileResponse(open(filename, 'rb'), filename='datos-historicos-iot.csv')


def get_daterange(request):
    try:
        start = datetime.fromtimestamp(
            float(request.GET.get('from', None))/1000)
    except:
        start = None
    try:
        end = datetime.fromtimestamp(
            float(request.GET.get('to', None))/1000)
    except:
        end = None
    if start == None and end == None:
        start = datetime.now()
        start = start - \
            dateutil.relativedelta.relativedelta(
                weeks=1)
        end = datetime.now()
        end += dateutil.relativedelta.relativedelta(days=1)
    elif end == None:
        end = datetime.now()
    elif start == None:
        start = datetime.fromtimestamp(0)

    return start, end


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