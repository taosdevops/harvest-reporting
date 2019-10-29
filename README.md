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

## Install sphinx

 `pipenv install --dev Sphinx --skip-lock`

### Configure Sphinx

  From the root of your project, initialise the docs/ directory with sphinx-quickstart:

   `cd docs/`

   `sphinx-quickstart`

    *  Project name: 
    *  Author name(s):
    *  Project release []:
    *  Project language [en]:

  Generate Module API docs:

  `sphinx-apidoc -o source/ ../hreporting/`

  Add Module extensions:

   ```
    extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    ]

   ```
 Add correct path to module extensions:

  `sys.path.insert(0, os.path.abspath('../..'))`


 Include the README:
  
  path:
  docs/index.rst


   `.. include:: ../../README.md`

 Added html theme:
  
  `html_theme = sphinx_rtd_theme`


  Reference documentaion:
  https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/

Generate html

  `make html`





