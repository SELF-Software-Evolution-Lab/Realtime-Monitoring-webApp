from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("realtimeGraph", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL('SELECT create_hypertable(\'"realtimeGraph_data"\', \'time\');'),
        migrations.RunSQL(
            "ALTER TABLE \"realtimeGraph_data\" SET (timescaledb.compress, timescaledb.compress_segmentby = 'station_id');"
        ),
        migrations.RunSQL(
            'SELECT add_compression_policy(\'"realtimeGraph_data"\', INTERVAL \'7 days\');'
        ),
    ]