"""This module is used to create a Traffic Ops session 
and to store prerequisite data for endpoints"""
import json
import logging
import sys
from random import randint
from urllib.parse import urlparse
import pytest
from trafficops.tosession import TOSession
from trafficops.restapi import OperationError


# Create and configure logger
logger = logging.getLogger()


def pytest_addoption(parser):
    """Passing in Traffic Ops Arguments [Username, Password, Url and Hostname] from Command Line"""
    parser.addoption(
        '--to_user', action='store', default='admin', help='User name for Traffic Ops Session'
    )
    parser.addoption(
        '--to_password', action='store', default='twelve12', help='Password for Traffic Ops Session'
    )
    parser.addoption(
        '--to_url', action='store', default='https://localhost/api', help='Traffic Ops URL'
    )
    parser.addoption(
        '--hostname', action='store', default='localhost', help='Traffic Ops hostname'
    )


@pytest.fixture(name="to_args")
def to_data(pytestconfig):
    """PyTest fixture to store Traffic ops Arguments passed from command line"""
    args = {}
    args['user'] = pytestconfig.getoption('--to_user')
    args['password'] = pytestconfig.getoption('--to_password')
    args['url'] = pytestconfig.getoption('--to_url')
    args['hostname'] = pytestconfig.getoption('--hostname')
    return args


@pytest.fixture(name="to_session")
def to_login(to_args):
    """PyTest Fixture to create a Traffic Ops session from Traffic Ops Arguments 
    passed as command line arguments in to_args fixture in conftest
    :param to_args: Fixture to get Traffic ops session arguments
    :type to_args: dict
    """
    # Create a Traffic Ops V4 session and login
    with open('to_data.json', encoding="utf-8", mode='r') as session_file:
        data = json.load(session_file)
    session_data = data["test"]
    api_version = session_data["api_version"]
    port = session_data["port"]
    if to_args["user"] is None:
        logger.info(
            "Traffic Ops session data were not passed from Command line Args")
    else:
        logger.info("Parsed Traffic ops session data from args %s", to_args)
        session_data = to_args
    to_url = urlparse(session_data["url"])
    to_host = to_url.hostname
    try:
        to_session = TOSession(host_ip=to_host, host_port=port,
                               api_version=api_version, ssl=True, verify_cert=False)
        logger.info("Established Traffic Ops Session")
    except OperationError:
        sys.exit(-1)

    # Login To TO_API
    to_session.login(session_data["user"], session_data["password"])
    logger.info("Successfully logged into Traffic Ops")
    return to_session


@pytest.fixture()
def cdn_prereq(to_session, get_cdn_data):
    """PyTest Fixture to create POST data for cdns endpoint
    :param to_session: Fixture to get Traffic ops session 
    :type to_session: TOsession
    :param get_cdn_data: Fixture to get cdn data from a prereq file
    :type get_cdn_data: dict
    """

    # Return new post data and post response from cdns POST request
    get_cdn_data["name"] = get_cdn_data["name"][:4]+str(randint(0, 1000))
    get_cdn_data["domainName"] = get_cdn_data["domainName"][:5] + \
        str(randint(0, 1000))
    logger.info("New cdn data to hit POST method %s", get_cdn_data)
    # Hitting cdns POST methed
    response = to_session.create_cdn(data=get_cdn_data)
    prerequisite_data = None
    try:
        cdn_response = response[0]
        prerequisite_data = [get_cdn_data, cdn_response]
    except IndexError:
        logger.error("No CDN response data from cdns POST request")
    return prerequisite_data
