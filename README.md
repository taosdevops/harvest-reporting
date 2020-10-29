# harvest-reporting

Harvest Time tracking and reporting API implementation

## Usage

### Notification Configuration

There is an [example yaml](./examples/config.yaml) that shows how to
set up every kind of integration.

## Contributing

### Local Development

Create virtual env

`pipenv shell`

Install Testing + Doc dependencies

`pipenv install -e .[tests,docs] --dev --skip-lock`

#### Generate Docs

`cd docsrc && make github`

#### Hosting the docs

`cd PROJECT_ROOT && python -m http.server`

This will host the docs [locally on 8000](http://localhost:8000)

#### Local Testing

To test, you will need the following environment variables set:

  "BEARER_TOKEN"          ##google harvest api token and get a developer token

  "CONFIG_PATH"           ##configuration file to use, see ./examples/config.yml

  "HARVEST_ACCOUNT_ID"    ##matches with the bearer token

  "LOG_LEVEL": "debug"    ##logging level

  "SENDGRID_API_KEY"      ##google sendgrid api token

  "ORIGIN_EMAIL_ADDRESS"  ##must be valid email address should be self

  "GCP_PROJECT"           ##doesn't have to be a real bucket name, could be FAKE


#### End-to-end Testing

To test, you will need the following environment variables set:

  "BEARER_TOKEN_SECRET"          ##google harvest api token and get a developer token

  "BUCKET"                       ##this is where the config files are pulled from

  "HARVEST_ACCOUNT_ID"           ##matches with the bearer token

  "LOG_LEVEL": "debug"           ##logging level

  "SENDGRID_API_KEY_SECRET"      ##google sendgrid api token

  "ORIGIN_EMAIL_ADDRESS"         ##must be valid email address should be self

  "GCP_PROJECT"                  ##must be the GCP project where the application is running
