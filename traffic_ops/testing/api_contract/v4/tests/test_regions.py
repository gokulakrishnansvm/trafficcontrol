"""Api Contract Test Case for regions endpoint"""
import json
import logging
import pytest

# Create and configure logger
logger = logging.getLogger()


@pytest.fixture(name="get_region_data")
def get_region_prereq_data():
    """PyTest Fixture to store prereq data for regions endpoint"""
    # Response keys for regions endpoint
    with open('prerequisite_data.json', encoding="utf-8", mode='r') as prereq_file:
        data = json.load(prereq_file)
    region_data = data["regions"]
    return region_data


def test_get_region(to_session, get_region_data, api_fixture):
    """Test step to validate keys, values and data types from regions endpoint response
    :param to_session: Fixture to get Traffic ops session 
    :type to_session: TOsession
    :param get_profile_data: Fixture to get region data from a prereq file
    :type get_profile_data: dict
    :param api_fixture: Fixture to get sample region data and actual region response
    :type api_fixture: list
    """
    # validate Region keys from regions get response
    logger.info("Accessing regions endpoint through Traffic ops session")
    region_prereq = api_fixture("regions", get_region_data)
    region_name = region_prereq[0]["name"]
    region_get_response = to_session.get_regions(
        query_params={"name": str(region_name)})
    try:
        region_data = region_get_response[0]
        region_keys = list(region_data[0].keys())
        logger.info(
            "Region Keys from regions endpoint response %s", region_keys)
        # validate region values from prereq data in profiles get response
        prereq_values = [region_prereq[0]['name'], region_prereq[0]['divisionName'],
                         region_prereq[0]['division']]
        get_values = [region_data[0]['name'], region_data[0]['divisionName'],
                      region_data[0]['division']]
        # validate data types for values from region get json response
        for (prereq_value, get_value) in zip(prereq_values, get_values):
            assert isinstance(prereq_value, type(get_value))
        assert region_keys.sort() == list(get_region_data.keys()).sort()
        assert get_values == prereq_values
    except IndexError:
        logger.error("No Region data from regions get request")
        pytest.fail(
            "Response from get request is empty, Failing test_get_region")
    finally:
        try:
            region_response = region_prereq[1]
            region_id = region_response["id"]
            to_session.delete_region(query_params={"id": str(region_id)})
        except IndexError:
            logger.error("Profile doesn't created")
