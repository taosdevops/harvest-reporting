# harvest-reporting

Harvest Time tracking and reporting API implementation

Docs: [Harvest Reporting Docs](https://taosdevops.github.io/harvest-reporting/)

## Configration of Notifications

### YAML Settings

There is an [example yaml](./examples/config.yaml) that shows how to
set up every kind of integration.

### Global Hooks

There are two types of global hooks. Emails and WebHooks.

Emails are in the block labeled `globalEmails`. All emails in this block receive *all*
notifications. This includes client names and usage information. This should only be
used for internal notification for project owners or business management.

```.yaml
globalEmails:
  - firstEmailAddress@example.com
  - secnodEmailAddress@example.com
```

Hooks are listed in the `globalHooks`. All hooks in this block will receive *all*
notifications. This includes client names and usage information. This should only be
used for internal notification for project owners or business management.

```.yaml
globalHooks:
  - https://hooks.slack.com/services/GlobalHooksForAllClients
  - https://hooks.slack.com/services/GlobalHookForProjects
```

### Client Specific Hooks

Each client listed in the configuration has its own section.
This section has two types of hooks that can be enabled.

All webhooks are to be listed under `hooks:` for the client. This
list is provider agnostic and will auto-switch the formatting based on
if MS Teams or Slack is detected. This hook will only send specific client data.

```.yaml
clients:
  - name: LotsOfHours
    hours: 160
    hooks:
      - https://hooks.slack.com/services/dude/what!
      - https://outlook.office.com/webhook/lotsOfhashes
```

All destination email addresses are to be listed under `emails:`

```.yaml
clients:
  - name: Email Only
    hours: 160
    emails:
      - primary@emailonly.com
      - secondary@emailonly.com
```

## CLI

### Installing as CLI

you can install this package off of pypi

`pip install harvestcli`

or you can clone the project install the project from that directory.

`pip install .`

### Environment Variables

When using the cli Environment Variables can be used as an alternative to
providing the input via command line flags.

| Variable | Option |
| -------- | ------ |
| BEARER_TOKEN | -b, --bearer-token |
| HARVEST_ACCOUNT_ID | --account-id |
| HARVEST_CONFIG | --config-path |
| SENDGRID_API_KEY| -s, --send-grid |

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
  "SLACK_API_KEY"         ##slack api key
  "ORIGIN_EMAIL_ADDRESS"  ##must be valid email address should be self
  "GCP_PROJECT"           ##doesn't have to be a real bucket name, could be FAKE


#### End-to-end Testing

To test, you will need the following environment variables set:
  "BEARER_TOKEN_SECRET"          ##google harvest api token and get a developer token
  "BUCKET"                       ##this is where the config files are pulled from
  "HARVEST_ACCOUNT_ID"           ##matches with the bearer token
  "LOG_LEVEL": "debug"           ##logging level
  "SENDGRID_API_KEY_SECRET"      ##google sendgrid api token
  "SLACK_API_KEY_SECRET"         ##slack api key
  "ORIGIN_EMAIL_ADDRESS"         ##must be valid email address should be self
  "GCP_PROJECT"                  ##doesn't have to be a real bucket name, could be FAKE