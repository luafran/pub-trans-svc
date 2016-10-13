## Functional Endpoints

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

### Get all routes not running at {02:00}
```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes?not_running_at=02:00' | python -m json.tool
{
    "routes": [
        {
            "tag": "1",
            "title": "1-California"
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

### Get schedule for route {E} from agency {sf-muni}

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes/E/schedule' | python -m json.tool
{
    "scheduleClass": "2016T_FALL",
    "scheduleItems": {
        "wkd:inbound": {
            "serviceClass": "wkd",
            "direction": "Inbound",
            "stops": {
                "4513": {
                    "tag": "4513",
                    "title": "The Embarcadero & Ferry Term",
                    "scheduledArrivals": [
                        {
                            "epochTime": "32220000",
                            "timeData": "08:57:00"
                        },
                        ...
                        {
                            "epochTime": "65460000",
                            "timeData": "18:11:00"
                        }
                    ]
                },
                "4530": {},
                "5237": {},
                "5240": {},
                "7795": {},
                "33095": {},
                "35184": {}
            },
            "scheduleStartTime": "08:52:00",
            "scheduleStopTime": "18:29:00"
        }
    },
    "wkd:outbound": {},
    "sat:inbound": {},
    "sat:outbound": {},
    "sun:inbound": {},
    "sun:outbound": {}
}
```

### Get messages for route {E} from agency {sf-muni}
```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes/E/messages' | python -m json.tool
{
    "allMessages": [
        {
            "id": "18419",
            "sendToBuses": "false",
            "priority": "Low",
            "text": "We're on Twitter: @sfmta_muni"
        },
        ...
        {
            "id": "21868",
            "sendToBuses": "false",
            "priority": "Low",
            "text": "Seeing \"registering\"? The system is being upgraded to 3G."
        }
    ],
    "routeMessages": [
        {
            "id": "22003",
            "sendToBuses": "false",
            "priority": "Normal",
            "text": "Board E at other \nend of station",
            "stops": [
                {
                    "tag": "5234",
                    "title": "King St & 2nd St"
                },
                {
                    "tag": "5237",
                    "title": "King St & 2nd St"
                }
            ],
            "intervals": [
                {
                    "startDay": "0",
                    "startTime": "32400",
                    "endDay": "0",
                    "endTime": "68340"
                },
                ...
                {
                    "startDay": "6",
                    "startTime": "32400",
                    "endDay": "6",
                    "endTime": "68340"
                }
            ]
        },
        ...
    ]
}
```

### Get vehicles for route {E} from agency {sf-muni} since last time {1476380899035}
```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/sf-muni/routes/E/vehicles?lastTime=1476380899035' | python -m json.tool
{
    "vehicles": [
        {
            "id": "1009",
            "dirTag": "E____O_F00",
            "lat": "37.80753",
            "lon": "-122.41732",
            "secsSinceReport": "62",
            "predictable": "true",
            "heading": "218",
            "SpeedKmHr": "0"
        },
        {
            "id": "1007",
            "dirTag": "E____I_F00",
            "lat": "37.77587",
            "lon": "-122.39455",
            "secsSinceReport": "27",
            "predictable": "true",
            "heading": "45",
            "SpeedKmHr": "20"
        }
    ],
    "lastTime": "1476380934095"
}
```

## Operations and Support Endpoints

### Send a request to service health

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/health' | python -m json.tool
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

### Get the total number of queries made to each endpoint

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/stats/uri_count' | python -m json.tool
{
    "uriCount": {
        "/v1/stats": 32,
        "/v1/stats/slow_requests": 9,
        "/v1/agencies": 8,
        "/v1/stats/uri_count": 6,
        "/v1/sf-muni/routes": 6,
        "/v1/sf-muni/routes/6/schedule": 1
    }
}
```

### Get a list of requests that latest response time was greater than {500} ms.

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/stats/slow_requests?slow_limit=500' | python -m json.tool
{
    "slowRequests": {
        "/v1/sf-muni/routes/6/schedule": 1425,
        "/v1/sf-muni/routes": 872
    }
}
```

### Get all stats

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/stats | python -m json.tool
{
    "uriCount": {
        "/v1/stats": 32,
        "/v1/stats/slow_requests": 9,
        "/v1/agencies": 8,
        "/v1/stats/uri_count": 7,
        "/v1/sf-muni/routes": 6,
        "/v1/sf-muni/routes/6/schedule": 1
    },
    "slowRequests": {
        "/v1/sf-muni/routes/6/schedule": 1425,
        "/v1/sf-muni/routes": 872,
        "/v1/stats": 5,
        "/v1/agencies": 4,
        "/v1/stats/slow_requests": 3,
        "/v1/stats/uri_count": 2
    }
}
```
