import yaml
from dacite import from_dict
import reporting.config

def test_load():
    # Test open regular file
    f = from_dict(
        data_class=reporting.config.ReporterConfig, data=yaml.load(open('tests/harvestapi/testdata/test_config.yaml', 'r').read(), Loader=yaml.Loader)
    )

    assert reporting.config.load('tests/harvestapi/testdata/test_config.yaml') == f