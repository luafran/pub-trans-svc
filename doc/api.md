### Send a request to service health

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/health' | python -m json.tool
{
    "status": {
        "details": [],
        "health": [
            0,
            "OK"
        ],
        "service": "pubtrans",
        "version": "0.0.1"
    }
}
```

### Get agencies

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/agencies' | python -m json.tool
{
    "agencies": [
        {
            "regionTitle": "California-Northern",
            "tag": "actransit",
            "title": "AC Transit"
        },
        ...
        {
            "regionTitle": "Pennsylvania",
            "tag": "york-pa",
            "title": "York College"
        }
    ]
}
```

### Get all routes for agency {sf-muni}
```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes' | python -m json.tool
{
    "routes": [
        {
            "tag": "E",
            "title": "E-Embarcadero"
        },
        ... 
        {
            "tag": "61",
            "title": "California Cable Car"
        }
    ]
}
```

### Get route with tag {E} for agency {sf-muni}
```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes/E' | python -m json.tool
{
    "tag": "E",
    "title": "E-Embarcadero",
    "color": "667744",
    "oppositeColor": "ffffff",
    "latMin": "37.7762699",
    "latMax": "37.8085899",
    "lonMin": "-122.41732",
    "lonMax": "-122.38798",
    "stops": [
        {
            "tag": "5184",
            "title": "Jones St & Beach St",
            "lat": "37.8071299",
            "lon": "-122.41732",
            "stopId": "15184"
        },
        ...
    ],
    "directions": [
        {
            "tag": "E____O_F00",
            "title": "Outbound to Mission Bay",
            "name": "Outbound",
            "useForUI": "true",
            "stops": [
                {
                    "tag": "5184"
                },
                ...
            ]
        },
        ...
    ],
    "paths": [
        {
            "points": [
                {
                    "lat": "37.80835",
                    "lon": "-122.41029"
                },
                ...
            ]
        }
        ...
    ]
}
```

## Get schedule for route {E} from agency {sf-muni}

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes/E/schedule' | python -m json.tool
{
    "scheduleClass": "2016T_FALL",
    "scheduleItems": [
        {
            "serviceClass": "wkd",
            "direction": "Inbound",
            "headerStops": [
                {
                    "tag": "5237",
                    "stopTitle": "King St & 2nd St"
                },
                ...
                {
                    "tag": "35184",
                    "stopTitle": "Jones St & Beach St"
                }
            ],
            "trs": [
                {
                    "blockId": "9201",
                    "stops": [
                        {
                            "tag": "5237",
                            "epochTime": "-1",
                            "timeData": "--"
                        },
                        ...
                        {
                            "tag": "33095",
                            "epochTime": "33180000",
                            "timeData": "09:13:00"
                        },
                        {
                            "tag": "35184",
                            "epochTime": "-1",
                            "timeData": "--"
                        }
                    ]
                },
                ...
                {
                    "blockId": "9204",
                    "stops": [
                        {
                            "tag": "5237",
                            "epochTime": "-1",
                            "timeData": "--"
                        },
                        ...
                        {
                            "tag": "35184",
                            "epochTime": "66540000",
                            "timeData": "18:29:00"
                        }
                    ]
                }
            ]
        },
        ...
        {
            "serviceClass": "sun",
            "direction": "Outbound",
            "headerStops": [
                {
                    "tag": "5184",
                    "stopTitle": "Jones St & Beach St"
                },
                ...
                {
                    "tag": "5239",
                    "stopTitle": "King St & 4th St"
                }
            ],
            "trs": [
                {
                    "blockId": "9201",
                    "stops": [
                        {
                            "tag": "5184",
                            "epochTime": "-1",
                            "timeData": "--"
                        },
                        ...
                        {
                            "tag": "5239",
                            "epochTime": "35820000",
                            "timeData": "09:57:00"
                        }
                    ]
                },
                ...
            ]
        }
    ]
}
```