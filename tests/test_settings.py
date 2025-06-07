from pymapgis.settings import settings


def test_defaults():
    assert settings.default_crs == "EPSG:4326"
