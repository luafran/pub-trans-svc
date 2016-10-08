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

### Get all routes for agency sf-muni
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

### Get route with tag E for agency sf-muni
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