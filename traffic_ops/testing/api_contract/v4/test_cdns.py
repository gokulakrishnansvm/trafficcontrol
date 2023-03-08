import pytest
import json

"""
PyTest Fixture to store keys for cdns endpoint
"""
@pytest.fixture
def get_cdn_keys():
    # Response keys for cdns endpoint
    with open('endpoint_data.json', 'r') as f:
         data = json.load(f)     
    return data['cdn_keys']

"""
Test step to validate keys from cdns endpoint response in TO V4
"""
def test_get_cdn(to_login, get_cdn_keys, cdn_post_data):
    #validate CDN keys from cdns get response
    print("Accessing Cdn endpoint through Traffic ops session")
    cdn_name = cdn_post_data[0]["cdns"]["name"]
    cdn_get_response = to_login.get_cdns(query_params={"name":str(cdn_name)})
    #add a check
    cdn_data = cdn_get_response[0] 
    cdn_keys = list(cdn_data[0].keys())
    print("CDN Keys from cdns endpoint response {}".format(cdn_keys))
    #validate cdn values from post data in cdns get response
    post_data = [cdn_post_data[0]["cdns"]['name'], cdn_post_data[0]["cdns"]['domainName'], cdn_post_data[0]["cdns"]['dnssecEnabled']]
    get_data = [cdn_data[0]['name'], cdn_data[0]['domainName'], cdn_data[0]['dnssecEnabled']]
    assert cdn_keys == get_cdn_keys
    assert get_data == post_data


"""
Test step to validate POST method for cdns endpoint
"""
def test_post_cdn(to_login, cdn_post_data):

    post_data=cdn_post_data[0]['cdns']
    cdn_data = [post_data['name'], post_data['domainName'], post_data['dnssecEnabled']]
    print("Print pre post data for cdn endpoint {}".format(post_data))
    #Accessing cdns POST method
    cdn_response = cdn_post_data[1]
    cdn_response_data = [cdn_response['name'], cdn_response['domainName'], cdn_response['dnssecEnabled']]
    assert cdn_response_data == cdn_data
    

