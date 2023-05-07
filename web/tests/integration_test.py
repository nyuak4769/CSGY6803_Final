import requests
import pytest
from conftest import ValueStorage

ENDPOINT_URL = "http://127.0.0.1:5000/api/v1"


@pytest.fixture(scope='module')
def dummy_secret():
    keys = {}
    yield keys


def test_swagger_up():
    r = requests.get(ENDPOINT_URL)
    assert r.status_code == 200


def test_swagger_redirect():
    r = requests.get("http://127.0.0.1:5000", allow_redirects=False)
    assert r.status_code == 302


def test_secrets_endpoint():
    r = requests.get(ENDPOINT_URL+"/secret/")
    ValueStorage.num_of_secrets = len(r.json())


def test_events_endpoint():
    r = requests.get(ENDPOINT_URL+"/events/")
    ValueStorage.num_of_events = len(r.json())


def test_create_new_secret():
    r = requests.post(ENDPOINT_URL+"/secret/", json=ValueStorage.dummy_secret)
    assert r.status_code == 201
    assert r.json()['description'] == ValueStorage.dummy_secret['description']
    assert r.json()['rotationpolicy'] == ValueStorage.dummy_secret['policyname']
    assert 'nextrotationtime' in r.json()
    ValueStorage.dummy_secret_id = r.json()['id']


def test_get_new_secret():
    r = requests.get(ENDPOINT_URL+"/secret/"+ValueStorage.dummy_secret_id)
    assert r.status_code == 200
    assert r.json()[0]['description'] == ValueStorage.dummy_secret['description']
    assert r.json()[0]['rotationpolicy'] == ValueStorage.dummy_secret['policyname']
    assert 'nextrotationtime' in r.json()[0]


def test_get_new_secret_events():
    r = requests.get(ENDPOINT_URL+"/events/")
    assert len(r.json()) > 0
    assert r.status_code == 200


def test_delete_new_secret():
    r = requests.delete(ENDPOINT_URL+"/secret/"+ValueStorage.dummy_secret_id)
    assert r.status_code == 204


def test_num_secrets_matches_after_delete():
    r = requests.get(ENDPOINT_URL+"/secret/")
    assert len(r.json()) == ValueStorage.num_of_secrets


def test_num_events_matches_after_delete():
    r = requests.get(ENDPOINT_URL+"/events/")
    assert len(r.json()) == ValueStorage.num_of_events
