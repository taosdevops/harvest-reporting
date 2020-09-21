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

Install Dev dependencies

`pipenv install --dev --skip-lock`

#### Generate Docs

Install the devrequirements to install sphinx and its dependencies then run

`cd docsrc && make github`

#### Hosting the docs

`cd PROJECT_ROOT && python -m http.server`

This will host the docs [locally on 8000](http://localhost:8000)

#### Testing

To test, you will need the following environment variables set:


