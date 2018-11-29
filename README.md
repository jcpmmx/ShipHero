# ShipHeroTest
ShipHero take-home test project.

### System requirements
- Python (v3.6.5)
- PostgreSQL (v10.5)

### Built and tested with
- Python (v3.6.5)
- Flask (v1.0.2)
- Flask-RESTful (v0.3.6)
- requests (v2.20)
- PostgreSQL (v10.5) + psycopg2 (v2.7.6.1)
- SQLAlchemy (v1.2.14) + Flask-SQLAlchemy (v2.3.2)
- gunicorn (v19.9) (Heroku only)

### How to run this locally
1. Clone this repo
2. Install all Python libraries (ideally inside a `virtualenv`): `pip install -r requirements.txt` 
3. Create 2 new PostgreSQL databases: `createdb shiphero` and `createdb shiphero_test`
4. Run `python manage.py db init` and `python manage.py db upgrade` to set your DB instance
5. Run `python run.py` to run Flask's development server and go to `http://localhost:5000`
6. Run `python tests.py` to run test cases

### About this solution

This Flask application contains one SQLAlchemy model, `Carrier`, that represents a shipping carrier and its basic data:  
- Name
- API credentials
- Shipment options

The app also provides 2 API endpoints to interact with.  
These endpoints are RESTful and work with JSON by default.

1. `/api/shipping/carrier`: returns a list of all carriers supported.  
e.g.
```
Request: HTTP POST

Response: HTTP/1.0 200 OK
[
    {
        "code": "fedex",
        "enabled": true,
        "name": "Fedex",
        "shipment_methods": {
            "cheap": "fdxchp",
            "express": "fdxexp",
            "regular": "fdxreg"
        }
    },
    {
        "code": "ups",
        "enabled": true,
        "name": "UPS",
        "shipment_methods": {
            "cheap": "upschp",
            "express": "upsexp",
            "regular": "upsreg"
        }
    }
]
```
> For testing purposes, the DB comes with 2 preloaded carriers: Fedex and UPS

2. `/api/shipping/cost`: returns the cost of a given shipment done by each of the enabled carriers.  
All params are required and have type checking (i.e. `weight` must be a valid int, `box_type` must be only the valid values).

e.g.  
```
Request: HTTP POST
{
    "address": "123 Fake St, Springfield",
    "weight": 33,
    "priority": 1,
    "box_type": "medium"
}

HTTP/1.0 200 OK
[
    {
        "carrier": "fedex",
        "cost": 647,
        "error": ""
    },
    {
        "carrier": "ups",
        "cost": 679,
        "error": ""
    }
]
```

Internally, this endpoint takes all the data, verifies it (it randomly generates HTTP 400 to simulate bad user input) and checks all enabled carriers. For each enabled carrier, we take the original data and hit the carrier's API endpoint. In this case, this endpoint is mocked locally at `/mock/<carrier>/shippingcost`. This mocking endpoint does hit an external API, `fakeJSON`, and handles an expected, consistent structure. Similarly, interactions against `fakeJSON` also randomly fail by design to cope with unexpected responses from external APIs.

e.g. Response for an empty POST request
```
HTTP/1.0 200 OK
{
    "message": {
        "address": "Destination to calculate shipment costs for",
        "box_type": "Valid values: small, medium, big",
        "priority": "Valid values: 1 (top) to 5 (least)",
        "weight": "Weight of the package in lb"
    }
}
```

e.g. Responses when we hit HTTP 400 randomly, or when the 'external API' fails
```
HTTP/1.0 400 BAD REQUEST
{
    "message": "Shame! http://weknowmemes.com/wp-content/uploads/2013/09/boo-bitch-aaron-paul-gif.png"
}

HTTP/1.0 200 OK
[
    {
        "carrier": "fedex",
        "cost": -1,
        "error": "Blame Fedex! https://memegenerator.net/img/instances/44786501.jpg"
    },
    {
        "carrier": "ups",
        "cost": -1,
        "error": "Blame UPS! https://memegenerator.net/img/instances/44786501.jpg"
    }
]
```

### Limitations
- `fakeJSON` daily credits (this is the case when `cost` is always 123)

### Nices to have
- Add Flask-API support so our API is browsable
- Return more realistic costs, one per shipment method
- Connect to real APIs from carriers
