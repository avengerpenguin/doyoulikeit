import pytest
import hyperspace
from laconia import ThingFactory


@pytest.fixture
def client():
    return hyperspace.jump('http://localhost:5100')

@pytest.fixture
def kevin_bacon():
    return hyperspace.jump('http://localhost:5100/things/1')

def test_should_have_a_title_or_name(kevin_bacon):
    print(kevin_bacon.data.serialize(format='turtle').decode('utf-8'))
    kb = ThingFactory(kevin_bacon.data)(kevin_bacon.url)
    assert set(kb.schema_name) == {'Kevin Bacon'}
