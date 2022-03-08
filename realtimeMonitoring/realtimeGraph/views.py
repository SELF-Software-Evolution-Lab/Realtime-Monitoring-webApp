from datetime import datetime, tzinfo
import json
from os import name
import time

import tempfile
from realtimeMonitoring.utils import getCityCoordinates

from django.template.defaulttags import register
from django.contrib.auth import login, logout
from realtimeGraph.forms import LoginForm
from django.http import JsonResponse
from django.http.response import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils import timezone
from random import randint
from .models import (
    City,
    Country,
    Data,
    Location,
    Measurement,
    Role,
    State,
    Station,
    User,
)
from realtimeMonitoring import settings
import dateutil.relativedelta
from django.db.models import Avg, Max, Min, Sum


class DashboardView(TemplateView):
    template_name = "index.html"

    """
    Get de Index. Si el usuario no está logueado se redirige a la página de login.
    Envía la página de template de Index con los datos de contexto procesados en get_context_data.
    """

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, "index.html", self.get_context_data(**kwargs))

    """
    Se procesan los datos para cargar el contexto del template.
    El template espera un contexto de este tipo:
    {
        "data": {
            "temperatura": {
                "min": float,
                "max": float,
                "avg": float,
                "data": [
                    (timestamp1, medición1),
                    (timestamp2, medición2),
                    (timestamp3, medición3),
                    ...
                ]
            },
            "variable2" : {min,max,avg,data},
            ...
        },
        "measurements": [Measurement0, Measurement1, ...],
        "selectedCity": City,
        "selectedState": State,
        "selectedCountry": Country,
        "selectedLocation": Location
    }
    """

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        context = {}
        print("CONTEXT: getting context data")
        try:
            userParam = self.request.user.username
            cityParam = self.request.GET.get("city", None)
            stateParam = self.request.GET.get("state", None)
            countryParam = self.request.GET.get("country", None)
            print(
                "CONTEXT: getting user, city, state, country: ",
                userParam,
                cityParam,
                stateParam,
                countryParam,
            )
            if not cityParam and not stateParam and not countryParam:
                user = User.objects.get(login=userParam)
                print("CONTEXT: getting user db: ", user)
                stations = Station.objects.filter(user=user)
                print("CONTEXT: getting stations db: ", stations)
                station = stations[0] if len(stations) > 0 else None
                print("CONTEXT: getting first station: ", station)
                if station != None:
                    cityParam = station.location.city.name
                    stateParam = station.location.state.name
                    countryParam = station.location.country.name
                else:
                    return context
            print("CONTEXT: getting last week data and measurements")
            context["data"], context["measurements"] = self.get_last_week_data(
                userParam, cityParam, stateParam, countryParam
            )
            print(
                "CONTEXT: got last week data, now getting city, state, country: ",
                cityParam,
                stateParam,
                countryParam,
            )
            context["selectedCity"] = City.objects.get(name=cityParam)
            context["selectedState"] = State.objects.get(name=stateParam)
            context["selectedCountry"] = Country.objects.get(name=countryParam)
            context["selectedLocation"] = Location.objects.get(
                city=context["selectedCity"],
                state=context["selectedState"],
                country=context["selectedCountry"],
            )
        except Exception as e:
            print("Error get_context_data. User: " + userParam, e)
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_measurements(self):
        measurements = Measurement.objects.all()
        return measurements

    def get_last_week_data(self, user, city, state, country):
        result = {}
        start = datetime.now()
        start = start - dateutil.relativedelta.relativedelta(days=1)
        try:
            userO = User.objects.get(login=user)
            location = None
            try:
                cityO = City.objects.get(name=city)
                stateO = State.objects.get(name=state)
                countryO = Country.objects.get(name=country)
                location = Location.objects.get(
                    city=cityO, state=stateO, country=countryO
                )
            except:
                print("Specified location does not exist")
            print("LAST_WEEK: Got user and lcoation:",
                  user, city, state, country)
            if userO == None or location == None:
                raise "No existe el usuario o ubicación indicada"
            stationO = Station.objects.get(user=userO, location=location)
            print("LAST_WEEK: Got station:", user, location, stationO)
            if stationO == None:
                raise "No hay datos para esa ubicación"
            measurementsO = self.get_measurements()
            print("LAST_WEEK: Measurements got: ", measurementsO)
            for measure in measurementsO:
                print("LAST_WEEK: Filtering measure: ", measure)
                # time__gte=start.date() Filtro para último día
                start_ts = int(start.timestamp() * 1000000)
                raw_data = Data.objects.filter(
                    station=stationO, time__gte=start_ts, measurement=measure
                ).order_by("-base_time")[:2]
                print("LAST_WEEK: Raw data: ", len(raw_data))
                data = []
                for reg in raw_data:
                    values = reg.values
                    times = reg.times
                    for i in range(len(values)):
                        data.append(
                            (
                                ((reg.base_time.timestamp() +
                                 times[i]) * 1000 // 1),
                                values[i],
                            )
                        )

                # data = [[(d.toDict()['base_time'].timestamp() *
                #           1000) // 1, d.toDict()['value']] for d in raw_data]

                minVal = raw_data.aggregate(Min("min_value"))["min_value__min"]
                maxVal = raw_data.aggregate(Max("max_value"))["max_value__max"]
                avgVal = sum(reg.avg_value * reg.length for reg in raw_data) / sum(
                    reg.length for reg in raw_data
                )
                result[measure.name] = {
                    "min": minVal if minVal != None else 0,
                    "max": maxVal if maxVal != None else 0,
                    "avg": round(avgVal if avgVal != None else 0, 2),
                    "data": data,
                }
        except Exception as error:
            print("Error en consulta de datos:", error)

        return result, measurementsO

    """
    Post en /index. Se usa para actualizar las gráficas de medidas en tiempo real del usuario.
    """

    def post(self, request, *args, **kwargs):
        data = {}
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        try:
            body = json.loads(request.body.decode("utf-8"))
            action = body["action"]
            print("action:", action)
            userParam = self.request.user.username
            if action == "get_data":
                cityName = body["city"]
                stateName = body["state"]
                countryName = body["country"]
                data["result"] = self.get_last_week_data(
                    userParam, cityName, stateName, countryName
                )
            else:
                data["error"] = "Ha ocurrido un error"
        except Exception as e:
            data["error"] = str(e)
        return JsonResponse(data)


"""
Intenta traer el rol con nombre {name}. Si no existe lo crea y lo retorna.
"""


def get_or_create_role(name):
    try:
        role = Role.objects.get(name=name)
    except Role.DoesNotExist:
        role = Role(name=name)
        role.save()
    return role


"""
Intenta traer el usuario con login {login}. Si no existe lo crea y lo retorna.
"""


def get_or_create_user(login):
    try:
        user = User.objects.get(login=login)
    except User.DoesNotExist:
        role = Role.objects.get(name="USER")
        user = User(
            login=login,
            role=role,
        )
        user.save()
    return user


"""
Intenta traer la locación con nombre de ciudad, estado y país {city, state, country}.
Si no existe, calcula las coordenadas de esa ubicación, lo crea y lo retorna.
"""


def get_or_create_location(city, state, country):
    cityO, created = City.objects.get_or_create(name=city)
    stateO, created = State.objects.get_or_create(name=state)
    countryO, created = Country.objects.get_or_create(name=country)
    loc, created = Location.objects.get_or_create(
        city=cityO, state=stateO, country=countryO
    )
    if loc.lat == None:
        lat, lng = getCityCoordinates(f"{city}, {state}, {country}")
        loc.lat = lat
        loc.lng = lng
        loc.save()

    return loc


"""
Intenta traer la locación con sólo nombre de ciudad {city}.
Si no existe, calcula las coordenadas de esa ubicación, lo crea y lo retorna.
"""


def get_or_create_location_only_city(city):
    cityO, created = City.objects.get_or_create(name=city)
    stateO, created = State.objects.get_or_create(name="")
    countryO, created = Country.objects.get_or_create(name="Colombia")
    loc, created = Location.objects.get_or_create(
        city=cityO, state=stateO, country=countryO
    )
    if loc.lat == None:
        lat, lng = getCityCoordinates(f"{city}, Colombia")
        loc.lat = lat
        loc.lng = lng
        loc.save()

    return loc


"""
Intenta traer la estación con usuario y locación {user, location}. Si no existe la crea y la retorna.
"""


def get_or_create_station(user, location):
    station, created = Station.objects.get_or_create(
        user=user, location=location)
    return station


"""
Traer la estación con usuario y locación {user, location}.
"""


def get_station(user, location):
    station = Station.objects.get(user=user, location=location)
    return station


"""
Intenta traer la variable con nombre y unidad {name, unit}. Si no existe la crea y la retorna.
"""


def get_or_create_measurement(name, unit):
    measurement, created = Measurement.objects.get_or_create(
        name=name, unit=unit)
    return measurement


"""
Crea una nueva medición con valor, estación y variable {value, station, measure}
Actualiza también el tiempo de última actividad de la estación.
"""


def create_data(
    value: float,
    station: Station,
    measure: Measurement,
    time: datetime = timezone.now(),
):
    base_time = datetime(time.year, time.month, time.day,
                         time.hour, tzinfo=time.tzinfo)
    ts = int(base_time.timestamp() * 1000000)
    secs = int(time.timestamp() % 3600)

    data, created = Data.objects.get_or_create(
        base_time=base_time, station=station, measurement=measure, defaults={
            "time": ts,
        }
    )

    if created:
        values = []
        times = []
    else:
        values = data.values
        times = data.times

    values.append(value)
    times.append(secs)

    length = len(times)

    # Pueden quedar threads abiertos y bloquean memoria/cpu. Probar consultas sin estos valores
    data.max_value = max(values) if length > 0 else 0
    data.min_value = min(values) if length > 0 else 0
    data.avg_value = sum(values) / length if length > 0 else 0
    data.length = length

    data.values = values

    data.save()
    station.last_activity = time
    station.save()
    return data


"""
Crea una nueva medición con valor, estación y variable {value, station, measure}
Adicional a la función anterior, esta crea la medición con una fecha específica.
Se usa para la importación de datos.
"""

# TODO No está ajustada para el modelo de datos de Data con values = json.
# def create_data_with_date(value: float, station: Station, measure: Measurement, date: datetime):
#     data = Data(value=value, station=station, measurement=measure, time=date)
#     data.save()
#     return(data)


"""
Trae la última medición de una estación y variable en específico {station, measurement}.
"""


def get_last_measure(station, measurement):
    last_measure = Data.objects.filter(station=station, measurement=measurement).latest(
        "base_time"
    )
    return last_measure.values[-1]


class LoginView(TemplateView):
    template_name = "login.html"
    http_method_names = ["get", "post"]

    def post(self, request):
        form = LoginForm(request.POST or None)
        if request.POST and form.is_valid():
            try:
                user = form.login(request)
                if user:
                    login(request, user)
                    return HttpResponseRedirect("/")
            except Exception as e:
                print("Login error", e)
        errors = ""
        for e in form.errors.values():
            errors += str(e[0])

        return render(
            request,
            "login.html",
            {
                "errors": errors,
                "username": form.cleaned_data["username"],
                "password": form.cleaned_data["password"],
            },
        )


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


class HistoricalView(TemplateView):
    template_name = "historical.html"

    """
    Get de /historical. Si el usuario no está logueado se redirige a la página de login.
    Envía la página de template de historical.
    El archivo se descarga directamente del csv actualizado. No hay procesamiento ni filtros.
    """

    def get(self, request, **kwargs):
        if request.user == None or not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        return render(request, self.template_name)


"""
Se procesan los datos para enviar en JSON
La respuesta tiene esta estructura:
{
    "data": [
        {
            "name": "ciudad, estado, país",
            "lat": float,
            "lng": float,
            "population": int,
            "min": float,
            "max": float,
            "avg": float
        },
        {name, lat, lng, pop, min, max, avg},
        {name, lat, lng, pop, min, max, avg},
        ...
    ],
    "measurements": [Measurement0, Measurement1, ...],
    "selectedMeasure": Measurement,
    "locations": [Location0, Location1, ...],
    "start": startTime,
    "end": endTime
}
"""


def get_map_json(request, **kwargs):
    data_result = {}

    measureParam = kwargs.get("measure", None)
    selectedMeasure = None
    measurements = Measurement.objects.all()

    if measureParam != None:
        selectedMeasure = Measurement.objects.filter(name=measureParam)[0]
    elif measurements.count() > 0:
        selectedMeasure = measurements[0]

    locations = Location.objects.all()
    try:
        start = datetime.fromtimestamp(
            float(request.GET.get("from", None)) / 1000
        )
    except:
        start = None
    try:
        end = datetime.fromtimestamp(
            float(request.GET.get("to", None)) / 1000)
    except:
        end = None
    if start == None and end == None:
        start = datetime.now()
        start = start - dateutil.relativedelta.relativedelta(weeks=1)
        end = datetime.now()
        end += dateutil.relativedelta.relativedelta(days=1)
    elif end == None:
        end = datetime.now()
    elif start == None:
        start = datetime.fromtimestamp(0)

    data = []

    start_ts = int(start.timestamp() * 1000000)
    end_ts = int(end.timestamp() * 1000000)

    for location in locations:
        stations = Station.objects.filter(location=location)
        locationData = Data.objects.filter(
            station__in=stations, measurement__name=selectedMeasure.name, time__gte=start_ts, time__lte=end_ts,
        )
        if locationData.count() <= 0:
            continue
        minVal = locationData.aggregate(Min("min_value"))["min_value__min"]
        maxVal = locationData.aggregate(Max("max_value"))["max_value__max"]
        avgVal = locationData.aggregate(Avg("avg_value"))["avg_value__avg"]
        data.append(
            {
                "name": f"{location.city.name}, {location.state.name}, {location.country.name}",
                "lat": location.lat,
                "lng": location.lng,
                "population": stations.count(),
                "min": minVal if minVal != None else 0,
                "max": maxVal if maxVal != None else 0,
                "avg": round(avgVal if avgVal != None else 0, 2),
            }
        )

    startFormatted = start.strftime("%d/%m/%Y") if start != None else " "
    endFormatted = end.strftime("%d/%m/%Y") if end != None else " "

    data_result["locations"] = [loc.str() for loc in locations]
    data_result["start"] = startFormatted
    data_result["end"] = endFormatted
    data_result["data"] = data

    return JsonResponse(data_result)


class RemaView(TemplateView):
    template_name = "rema.html"

    """
    Get de /rema. Si el usuario no está logueado se redirige a la página de login.
    Envía la página de template de historical.
    El archivo se descarga directamente del csv actualizado. No hay procesamiento ni filtros.
    """

    def get(self, request, **kwargs):
        # if request.user == None or not request.user.is_authenticated:
        #     return HttpResponseRedirect("/login/")
        return render(request, self.template_name, self.get_context_data(**kwargs))

    """
    Se procesan los datos para cargar el contexto del template.
    El template espera un contexto de este tipo:
    {
        "data": [
            {
                "name": "ciudad, estado, país",
                "lat": float,
                "lng": float,
                "population": int,
                "min": float,
                "max": float,
                "avg": float
            },
            {name, lat, lng, pop, min, max, avg},
            {name, lat, lng, pop, min, max, avg},
            ...
        ],
        "measurements": [Measurement0, Measurement1, ...],
        "selectedMeasure": Measurement,
        "locations": [Location0, Location1, ...],
        "start": startTime,
        "end": endTime
    }
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        measureParam = self.kwargs.get("measure", None)
        selectedMeasure = None
        measurements = Measurement.objects.all()

        if measureParam != None:
            selectedMeasure = Measurement.objects.filter(name=measureParam)[0]
        elif measurements.count() > 0:
            selectedMeasure = measurements[0]

        locations = Location.objects.all()
        try:
            start = datetime.fromtimestamp(
                float(self.request.GET.get("from", None)) / 1000
            )
        except:
            start = None
        try:
            end = datetime.fromtimestamp(
                float(self.request.GET.get("to", None)) / 1000)
        except:
            end = None
        if start == None and end == None:
            start = datetime.now()
            start = start - dateutil.relativedelta.relativedelta(weeks=1)
            end = datetime.now()
            end += dateutil.relativedelta.relativedelta(days=1)
        elif end == None:
            end = datetime.now()
        elif start == None:
            start = datetime.fromtimestamp(0)

        data = []

        start_ts = int(start.timestamp() * 1000000)
        end_ts = int(end.timestamp() * 1000000)

        for location in locations:
            stations = Station.objects.filter(location=location)
            locationData = Data.objects.filter(
                station__in=stations, measurement__name=selectedMeasure.name, time__gte=start_ts, time__lte=end_ts,
            )
            if locationData.count() <= 0:
                continue
            minVal = locationData.aggregate(Min("min_value"))["min_value__min"]
            maxVal = locationData.aggregate(Max("max_value"))["max_value__max"]
            avgVal = locationData.aggregate(Avg("avg_value"))["avg_value__avg"]
            data.append(
                {
                    "name": f"{location.city.name}, {location.state.name}, {location.country.name}",
                    "lat": location.lat,
                    "lng": location.lng,
                    "population": stations.count(),
                    "min": minVal if minVal != None else 0,
                    "max": maxVal if maxVal != None else 0,
                    "avg": round(avgVal if avgVal != None else 0, 2),
                }
            )

        startFormatted = start.strftime("%d/%m/%Y") if start != None else " "
        endFormatted = end.strftime("%d/%m/%Y") if end != None else " "

        context["measurements"] = measurements
        context["selectedMeasure"] = selectedMeasure
        context["locations"] = locations
        context["start"] = startFormatted
        context["end"] = endFormatted
        context["data"] = data

        return context


def download_csv_data(request):
    print("Getting time for csv req")
    startT = time.time()
    print("####### VIEW #######")
    print("Processing CSV")
    start, end = get_daterange(request)
    print("Start, end", start, end)
    start_ts = int(start.timestamp() * 1000000)
    end_ts = int(end.timestamp() * 1000000)
    data = Data.objects.filter(time__gte=start_ts, time__lte=end_ts)
    print("Data ref got")
    tmpFile = tempfile.NamedTemporaryFile(delete=False)
    print("Creating file")
    filename = tmpFile.name

    with open(filename, "w", encoding="utf-8") as data_file:
        print("Filename:", filename)
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
        print("Head written")
        print("Len of data:", len(data))
        try:
            data_file.write(str(data))
        except Exception as e:
            print(e)
    endT = time.time()
    print("##### VIEW ######")
    print("Processed. Time: ", endT - startT)

    return FileResponse(open(filename, "rb"), filename="datos-historicos-iot.csv")


"""
Extrae los rangos de fecha de la url.
Ej: /index?from=1600000&to=1600000 => start=datetime.fromtimestamp(1600000), end=datetime.fromtimestamp(1600000)
"""


def get_daterange(request):
    try:
        start = datetime.fromtimestamp(
            float(request.GET.get("from", None)) / 1000)
    except:
        start = None
    try:
        end = datetime.fromtimestamp(float(request.GET.get("to", None)) / 1000)
    except:
        end = None
    if start == None and end == None:
        start = datetime.now()
        start = start - dateutil.relativedelta.relativedelta(weeks=1)
        end = datetime.now()
        end += dateutil.relativedelta.relativedelta(days=1)
    elif end == None:
        end = datetime.now()
    elif start == None:
        start = datetime.fromtimestamp(0)

    return start, end


"""
Filtro para formatear datos en el template de index
"""


@register.filter
def get_statistic(dictionary, key):
    if type(dictionary) == str:
        dictionary = json.loads(dictionary)
    if key is None:
        return None
    keys = [k.strip() for k in key.split(",")]
    return dictionary.get(keys[0]).get(keys[1])


"""
Filtro para formatear datos en los templates
"""


@register.filter
def add_str(str1, str2):
    return str1 + str2
