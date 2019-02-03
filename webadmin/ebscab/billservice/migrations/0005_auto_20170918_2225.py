# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billservice', '0004_auto_20170915_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_rx',
            field=models.IntegerField(default=0, verbose_name='Burst Rx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_time_rx',
            field=models.IntegerField(default=0, verbose_name='Burst time Rx (s)'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_time_tx',
            field=models.IntegerField(default=0, verbose_name='Burst time Tx (s)'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_treshold_rx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Rx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_treshold_tx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Tx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='burst_tx',
            field=models.IntegerField(default=0, verbose_name='Burst Tx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='max_rx',
            field=models.IntegerField(default=0, verbose_name='Max Rx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='max_tx',
            field=models.IntegerField(default=0, verbose_name='Max Tx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='min_rx',
            field=models.IntegerField(default=0, verbose_name='Min Rx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='min_tx',
            field=models.IntegerField(default=0, verbose_name='Min Tx'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='priority',
            field=models.IntegerField(default=8, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442'),
        ),
        migrations.AlterField(
            model_name='accessparameters',
            name='speed_units',
            field=models.CharField(blank=True, choices=[(b'Kbps', b'Kbps'), (b'Mbps', b'Mbps')], default=b'Kbps', max_length=32, null=True, verbose_name='\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u0438'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_rx',
            field=models.IntegerField(default=0, verbose_name='Burst Rx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_time_rx',
            field=models.IntegerField(default=0, verbose_name='Burst time Rx (s)'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_time_tx',
            field=models.IntegerField(default=0, verbose_name='Burst time Tx (s)'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_treshold_rx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Rx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_treshold_tx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Tx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='burst_tx',
            field=models.IntegerField(default=0, verbose_name='Burst Tx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='max_rx',
            field=models.IntegerField(default=0, verbose_name='Max Rx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='max_tx',
            field=models.IntegerField(default=0, verbose_name='Max Tx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='min_rx',
            field=models.IntegerField(default=0, verbose_name='Min Rx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='min_tx',
            field=models.IntegerField(default=0, verbose_name='Min Tx'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='priority',
            field=models.IntegerField(default=0, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442'),
        ),
        migrations.AlterField(
            model_name='addonservice',
            name='speed_units',
            field=models.CharField(blank=True, choices=[(b'Kbps', b'Kbps'), (b'Mbps', b'Mbps')], default=b'Kbps', max_length=32, null=True, verbose_name='\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u0438'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_rx',
            field=models.IntegerField(default=0, verbose_name='Burst Rx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_time_rx',
            field=models.IntegerField(default=0, verbose_name='Burst time Rx (s)'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_time_tx',
            field=models.IntegerField(default=0, verbose_name='Burst time Tx (s)'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_treshold_rx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Rx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_treshold_tx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Tx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='burst_tx',
            field=models.IntegerField(default=0, verbose_name='Burst Tx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='max_rx',
            field=models.IntegerField(default=0, verbose_name='Max Rx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='max_tx',
            field=models.IntegerField(default=0, verbose_name='Max Tx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='min_rx',
            field=models.IntegerField(default=0, verbose_name='Min Rx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='min_tx',
            field=models.IntegerField(default=0, verbose_name='Min Tx'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='priority',
            field=models.IntegerField(default=0, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442'),
        ),
        migrations.AlterField(
            model_name='speedlimit',
            name='speed_units',
            field=models.CharField(blank=True, choices=[(b'Kbps', b'Kbps'), (b'Mbps', b'Mbps')], default=b'Kbps', max_length=32, null=True, verbose_name='\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u0438'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_rx_int',
            field=models.IntegerField(default=0, verbose_name='Burst Rx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_time_rx_int',
            field=models.IntegerField(default=0, verbose_name='Burst time Rx (s)'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_time_tx_int',
            field=models.IntegerField(default=0, verbose_name='Burst time Tx (s)'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_treshold_rx_int',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Rx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_treshold_tx_int',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Tx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='burst_tx_int',
            field=models.IntegerField(default=0, verbose_name='Burst Tx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='max_rx_int',
            field=models.IntegerField(default=0, verbose_name='Max Rx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='max_tx_int',
            field=models.IntegerField(default=0, verbose_name='Max Tx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='min_rx_int',
            field=models.IntegerField(default=0, verbose_name='Min Rx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='min_tx_int',
            field=models.IntegerField(default=0, verbose_name='Min Tx'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='priority',
            field=models.IntegerField(default=8, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='speed_units',
            field=models.CharField(blank=True, choices=[(b'Kbps', b'Kbps'), (b'Mbps', b'Mbps')], default=b'Kbps', max_length=32, null=True, verbose_name='\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u0438'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_rx',
            field=models.IntegerField(default=0, verbose_name='Burst Rx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_time_rx',
            field=models.IntegerField(default=0, verbose_name='Burst time Rx (s)'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_time_tx',
            field=models.IntegerField(default=0, verbose_name='Burst time Tx (s)'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_treshold_rx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Rx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_treshold_tx',
            field=models.IntegerField(default=0, verbose_name='Burst treshold Tx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='burst_tx',
            field=models.IntegerField(default=0, verbose_name='Burst Tx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='max_rx',
            field=models.IntegerField(default=0, verbose_name='Max Rx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='max_tx',
            field=models.IntegerField(default=0, verbose_name='Max Tx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='min_rx',
            field=models.IntegerField(default=0, verbose_name='Min Rx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='min_tx',
            field=models.IntegerField(default=0, verbose_name='Min Tx'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='priority',
            field=models.IntegerField(default=8, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442'),
        ),
        migrations.AlterField(
            model_name='timespeed',
            name='speed_units',
            field=models.CharField(blank=True, choices=[(b'Kbps', b'Kbps'), (b'Mbps', b'Mbps')], default=b'Kbps', max_length=32, null=True, verbose_name='\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u0438'),
        ),
    ]
