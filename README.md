# harvest-reporting

Harvest Time tracking and reporting API implementation

## Usage

### Notification Configuration

There is an [example yaml](./examples/config.yaml) that shows how to
set up every kind of integration.

## Contributing

### Local Development

1. Create virtual env
  `pipenv shell`

2. Install Testing + Doc dependencies
  `pipenv install -e .[tests,docs] --dev --skip-lock`

#### Generate Docs

`cd docsrc && make github`

#### Hosting the docs
This will host the docs [locally on 8000](http://localhost:8000):
  `cd PROJECT_ROOT && python -m http.server`

#### Testing

To test, you will need the following environment variables set:
  "BEARER_TOKEN"          = <REQUIRED as env var or in GCP Secret Manager, Harvest API token>
  "SENDGRID_API_KEY"      = <REQUIRED as env var or in GCP Secret Manager, Sendgrid API key>
  
  "GCP_PROJECT"           = <REQUIRED, GCP project where the application is running>
  "HARVEST_ACCOUNT_ID"    = <REQUIRED, harvest account id>
  "ORIGIN_EMAIL_ADDRESS"  = <REQUIRED, Valid email address>
  
  "LOG_LEVEL"             = <OPTIONAL, Logging level, defaults to `info`>
  "CONFIG_PATH"           = <OPTIONAL, Configuration file to use, defaults to `config/clients.yaml`>
