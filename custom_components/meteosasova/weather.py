#!/usr/bin/python
# Do basic imports
import os.path
import sys
import requests  
import asyncio
import logging
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.weather import (WeatherEntity)
from homeassistant.const import (TEMP_CELSIUS, CONF_NAME, CONF_HOST, CONF_TIMEOUT)
from homeassistant.components.weather import (PLATFORM_SCHEMA)
from homeassistant.helpers.restore_state import RestoreEntity 

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Meteo sasova weather station"
DEFAULT_TIMEOUT = 10000

ATTR_METEOSASOVA_TEMPERATURE = 'zakladneTeplota'
ATTR_METEOSASOVA_HUMIDITY = 'zakladneVlhkost'
ATTR_METEOSASOVA_PRESSURE = 'zakladneTlak'
ATTR_METEOSASOVA_WIND_SPEED = 'zakladneVietor'
ATTR_METEOSASOVA_WIND_BEARING = 'zakladneVietorSmer'
ATTR_METEOSASOVA_CONDITION = 'zakladnePocasieImg'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int
})

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    _LOGGER.info('Setting up Meteo sasova weather platform')
    name = config.get(CONF_NAME)
    ip_addr = config.get(CONF_HOST)
    timeout = config.get(CONF_TIMEOUT)   

    _LOGGER.info('Adding Meteo sasova weather platform to hass')
    async_add_devices([
        MeteoSasovaWeather(hass, name, ip_addr, timeout)
    ])

class MeteoSasovaWeather(WeatherEntity, RestoreEntity):
    
    def __init__(self, hass, name, ip_addr, timeout):
        
        self.hass = hass
        self._name = name
        self._ip_addr = ip_addr
        self._timeout = timeout
        
        self._actual_json_values = None

    @asyncio.coroutine
    def async_added_to_hass(self):
        _LOGGER.info('Meteo sasova weather added to hass()')
        self.SyncState()
        
    def FetchResult(self, ip_addr, timeout):
        valuesUrl = "http://" + ip_addr + "/loadZakladne.php"
        valuesJson = requests.get(valuesUrl, allow_redirects=True, timeout=timeout)       
        return valuesJson.content.decode("utf-8")

    def GetValues(self):
        return self.FetchResult(self._ip_addr, self._timeout)

    def SyncState(self):    
        
        try:
            payload = json.loads(self.GetValues());
        except Exception:
            _LOGGER.warning("Could not process: %s", self.GetValues())
            return

        self._actual_json_values = payload;     
        self.schedule_update_ha_state()

    def update(self):
        _LOGGER.info('update()')
        # Update HA State from Device
        self.SyncState()
    
    @property
    def name(self):
        """Return the name"""
        return self._name

    @property
    def should_poll(self):
        """hass call entity update() in intervals"""
        return True

    @property
    def temperature(self):
        """Return the temperature."""
        return float(self._actual_json_values[ATTR_METEOSASOVA_TEMPERATURE].split(' ')[0].replace(',','.'))

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def humidity(self):
        """Return the humidity."""
        return float(self._actual_json_values[ATTR_METEOSASOVA_HUMIDITY].split(' ')[0].replace(',','.'))

    @property                                                              
    def pressure(self):
        """Return the pressure."""
        return float(self._actual_json_values[ATTR_METEOSASOVA_PRESSURE].split(' ')[0].replace(',','.'))

    @property
    def wind_speed(self):
        """Return the wind speed."""
        speed = None
        
        try:
            speed = float(self._actual_json_values[ATTR_METEOSASOVA_WIND_SPEED].split(' ')[0].replace(',','.'))
        except Exception:
            speed = 0.0
            
        return speed 

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        self._actual_json_values[ATTR_METEOSASOVA_WIND_BEARING]
        
    #@property
    #def attribution(self):
    #    """Return the attribution."""
    #    return 'Retrieved through ' + self._ip_addr 

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = super().state_attributes
        return attrs

    @property
    def condition(self):
        """Return condition."""
        condition = self._actual_json_values[ATTR_METEOSASOVA_CONDITION]
        
        if 'jasno' in condition:
            return 'sunny'
        elif 'polooblacno' in condition: 
            return 'partlycloudy'
        elif 'zamracene' in condition:
            return 'cloudy'
        elif 'dazd' in condition:
            return 'rainy'
        elif 'sneh' in condition:
            return 'snowy'
        elif 'burka' in condition:
            return 'lightning'
        elif 'hmla' in condition:
            return 'fog'
        elif 'noc' in condition:
            return 'clear-night'    
        
        return 'exceptional'