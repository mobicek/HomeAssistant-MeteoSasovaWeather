### HomeAssistant-MeteoSasovaWeather

Custom component for MeteoSasova weather station

![Image of Preview1](https://github.com/mobicek/HomeAssistant-MeteoSasovaWeather/blob/main/images/preview1.png)
![Image of Preview2](https://github.com/mobicek/HomeAssistant-MeteoSasovaWeather/blob/main/images/preview2.png)

Installation:

1. In your **configuration.yaml** add the following:

```
weather:
  - platform: meteosasova
    name: Meteo sasova weather station
    host: meteosasova.sk
```    

2. Copy meteosasova component to **config_dir/custom_components**   

3. Restart your Home Assistant server
