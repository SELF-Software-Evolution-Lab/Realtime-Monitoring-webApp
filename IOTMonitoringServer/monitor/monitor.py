from argparse import ArgumentError
from django.db.models import Avg
from datetime import timedelta, datetime
from processor.models import Data, Measurement


def analyze_data():
    # Consulta todos los datos de la última hora, los agrupa por estación y variable
    # Compara el promedio con los valores límite que están en la base de datos para esa variable.
    # Si el promedio es mayor que el límite, se envia un mensaje de alerta.
    data = Data.objects.all()
    # .filter(
    #   base_time__gte=datetime.now() - timedelta(hours=10))
    aggregation = data.annotate(check_value=Avg('avg_value')) \
        .select_related('station', 'measurement') \
        .select_related('station__user', 'station__location') \
        .select_related('station__location__city', 'station__location__state',
                        'station__location__country') \
        .values('check_value', 'station__user__username',
                'measurement__name',
                'measurement__max_value',
                'measurement__min_value',
                'station__location__city__name',
                'station__location__state__name',
                'station__location__country__name')

    for item in aggregation:
        if item["check_value"] > (item["measurement__max_value"] or 0):
            print(
                "Alerta: El valor promedio de la variable {} en la estación {} es mayor que el límite máximo de {}".format(
                    item["measurement__name"], item["station__user__username"],
                    item["measurement__max_value"]))
        elif item["check_value"] < (item["measurement__min_value"] or 0):
            print(
                "Alerta: El valor promedio de la variable {} en la estación {} es menor que el límite mínimo de {}".format(
                    item["measurement__name"], item["station__user__username"],
                    item["measurement__min_value"]))
        topic = '{}/{}/{}/{}/message'.format(item['station__location__country__name'],
                                             item['station__location__state__name'],
                                             item['station__location__city__name'],
                                             item['station__user__username'])
        print('Tópico: {}'.format(topic))

    print("Results: ", len(aggregation), " records")
    # print(aggregation)
