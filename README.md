# harvest-reporting
Harvest Time tracking and reporting API implementation

## CLI

### Installing as CLI

you can install this package off of pypi

` pip install harvestcli `

or you can clone the project install the project from that directory.

` pip install .`

### Environment Variables

When using the cli Environment Variables can be used as an alternative to
providing the input via command line flags.

| Variable | Option |
| -------- | ------ |
| BEARER_TOKEN | -b, --bearer-token |
| HARVEST_ACCOUNT_ID | --account-id |
| HARVEST_CONFIG | --config-path |

### Local Development

Create virtual env

 `pipenv shell`

Install Dev dependencies

 `pipenv install --dev --skip-lock`

#### Generate Docs

Install the devrequirements to install sphinx and its dependencies then run

`sphinx-build .docs docs`

#### Hosting the docs

`cd docs && python -m http.server`

This will host the docs locally at http://localhost:8000
