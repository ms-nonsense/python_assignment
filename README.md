# (Take-Home) Python Assignment

## Brief description:
This project does two things

1. Fetch IBM, Apple, Inc. stocks information for the most recent two weeks. 
These data will be processed before stored in a table.
2. Runs an API which returns stock data or its average for a specific time period, company, if given.

## Tech stack
- Database: MySQL 5.7
- PL: Python 3.10.10
- Libraries:
  - Flask
    - It is lightweight and well-documented enough to make things easier for any beginners. 
  - marshmallow
    - Makes serialization and deserialization easier. Not to mention, it has validation feature.
  - pymysql
    - It is said that this is faster than the usual library (mysql-connector-python) I use so I wanted to try it.
  - requests
    - It makes HTTP requests simpler and more human-friendly.
  - python-dateutil
    - It provides powerful extensions to Python's standard datetime module which I needed when dealing with dates
  - python-dotenv
    - It makes reading .env files and setting them as environment variables easier.
  
  The following libraries are not for production but for development.
  - flake8
    - I want to make sure my codes are up to coding standard.
  - mypy
    - I want to make sure I'm using variables and functions correctly.
  - yapf
    - I want to make sure my code format is correct

## Running locally

### Prerequisites
Following are already installed
- Python3.x 
- docker

and that you have created an API Key from [AlphaVantage](https://www.alphavantage.co/documentation/)
  
1. Go to project directory
```shell
cd python_assignment
```

2. (Optional) Create a virtual environment and activate it
```shell
python3 -m venv venv
source venv/bin/activate 
```

3. Set up all environmental variables. Copy .env.sample as .env and replace all values that start with `sample`.
Please make sure all values are the same in all env files.
```shell
# docker-compose db service
cp mysql-variables.env.sample mysql-variables.env

# get_raw_data env
cp .env.sample .env

# financial-api env
cp financial/.env.sample .env
```

4. Spin up DB and API containers
```shell
docker-compose up
```

6. To populate `financial_table` with records, execute
```shell
python3 get_raw_data.py
```

7. Query API for data

- ### financial_data

Request: `GET financial_data`
Parameters (optional):
- start_date: the minimum date of stock record to be fetched
- end_date: the maximum date of stock record to be fetched
- symbol: the stock symbol of the company
- page: offset page
- limit: the number of records to be displayed in a single page

```shell
curl -X GET 'http://127.0.0.1:5000/api/financial_data?start_date=2023-03-08&end_date=2023-03-18&symbol=IBM&page=2&limit=2'
```

Response
```json5
{
    "data":[
        {
            "symbol":"IBM",
            "date":"2023-03-10",
            "open_price":"126.1200",
            "close_price":"125.4500",
            "volume":5990867
        },
        {
            "symbol":"IBM",
            "date":"2023-03-13",
            "open_price":"125.1500",
            "close_price":"125.5800",
            "volume":8188369
        }
    ],
    "pagination":{
        "count":8,
        "page":2,
        "limit":2,
        "pages":4
    },
    "info":{
        "error":""
    }
}
```

- ### statistics

Request: `GET statistics`
Parameters (required):
- start_date: the minimum date of stock record to be fetched
- end_date: the maximum date of stock record to be fetched
- symbol: the stock symbol of the company

```shell
curl -X GET 'http://127.0.0.1:5000/api/statistics?start_date=2023-03-08&end_date=2023-03-18&symbol=IBM'
```

Response
```json5
{
    "data":[
        {
            "start_date":"2023-03-08",
            "end_date":"2023-03-18",
            "symbol":"IBM",
            "average_daily_open_price":"125.57125000",
            "average_daily_close_price":"125.19500000",
            "average_daily_volume":"10047584.0000"
        }
    ],
    "info":{
        "error":""
    }
}
```

## Maintaining API Key

For local development, I normally would go for git-crypt but only when the repository I'm going to push
to is private or is in self-hosted platform (e.g GitHub Enterprise Server).

In a production environment, using services like [AWS Secret Manager](https://aws.amazon.com/secrets-manager/) 
or [Infisical](https://github.com/Infisical/infisical) to manage secrets across all teams.

If none of the options above are feasible for some reasons, 
1. storing them in .env files and making sure those files are outside VCS
2. encrypt and store them in database.
are other options too.

Regardless of any environment, API Keys should be periodically replaced and their usage should be limited.