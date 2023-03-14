"""Api Contract Test Case for cdns endpoint"""
import json
import logging
import pytest

# Create and configure logger
logger = logging.getLogger()


@pytest.fixture(name="get_cdn_data")
def get_cdn_prereq_data():
    """PyTest Fixture to store prereq data for cdns endpoint"""
    # Response keys for cdns endpoint
    with open('prerequisite_data.json', encoding="utf-8", mode='r') as prereq_file:
        data = json.load(prereq_file)
    cdn_data = data["cdns"]
    return cdn_data


def test_get_cdn(to_session, get_cdn_data, cdn_prereq):
    """Test step to validate keys from cdns endpoint response and POST method
    :param to_session: Fixture to get Traffic ops session 
    :type to_session: TOsession
    :param get_cdn_data: Fixture to get cdn data from a prereq file
    :type get_cdn_data: dict
    :param cdn_prereq: Fixture to get sample cdn data and actual cdn response
    :type cdn_prereq: list
    """
    # validate CDN keys from cdns get response
    logger.info("Accessing Cdn endpoint through Traffic ops session")
    cdn_name = cdn_prereq[0]["name"]
    cdn_get_response = to_session.get_cdns(query_params={"name": str(cdn_name)})
    try:
        cdn_data = cdn_get_response[0]
        cdn_keys = list(cdn_data[0].keys())
        logger.info(
            "CDN Keys from cdns endpoint response %s", cdn_keys)
        # validate cdn values from prereq data in cdns get response
        prereq_data = [cdn_prereq[0]['name'], cdn_prereq[0]
                       ['domainName'], cdn_prereq[0]['dnssecEnabled']]
        get_data = [cdn_data[0]['name'], cdn_data[0]
                    ['domainName'], cdn_data[0]['dnssecEnabled']]
        assert cdn_keys.sort() == list(get_cdn_data.keys()).sort()
        assert get_data == prereq_data
    except IndexError:
        logger.error("No CDN data from cdns get request")
        pytest.fail("Response from get request is empty, Failing test_get_cdn")


@pytest.fixture(autouse=True)
def pytest_sessionfinish(cdn_prereq, to_session):
    """Delete CDN after test execution to avoid redundancy
    :param to_session: Fixture to get Traffic ops session 
    :type to_session: TOsession
    :param cdn_prereq: Fixture to get sample cdn data and actual cdn response
    :type cdn_prereq: list
    """
    yield
    try:
        cdn_response = cdn_prereq[1]
        cdn_id = cdn_response["id"]
        to_session.delete_cdn_by_id(cdn_id=cdn_id)
    except IndexError:
        logger.error("CDN doesn't created")
