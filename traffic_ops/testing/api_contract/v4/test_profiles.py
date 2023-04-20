#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""API Contract Test Case for profiles endpoint."""
import logging
import pytest
import requests
from jsonschema import validate

from trafficops.tosession import TOSession

# Create and configure logger
logger = logging.getLogger()

primitive = bool | int | float | str | None

def test_profile_contract(
	to_session: TOSession,
	request_template_data: list[dict[str, object] | list[object] | primitive],
	response_template_data: dict[str, primitive | list[primitive | dict[str, object]
						    | list[object]] | dict[object, object]],
	profile_post_data: dict[str, object]
) -> None:
	"""
	Test step to validate keys, values and data types from profiles endpoint
	response.
	:param to_session: Fixture to get Traffic Ops session.
	:param request_template_data: Fixture to get request template data from a prerequisites file.
	:param response_template_data: Fixture to get response template data from a prerequisites file.
	:param profile_post_data: Fixture to get sample Profile data and actual Profile response.
	"""
	# validate Profile keys from profiles get response
	logger.info("Accessing /profiles endpoint through Traffic ops session.")

	profile = request_template_data["profiles"][0]
	if not isinstance(profile, dict):
		raise TypeError("malformed profile in prerequisite data; not an object")

	profile_name = profile.get("name")
	if not isinstance(profile_name, str):
		raise TypeError("malformed profile in prerequisite data; 'name' not a string")

	profile_get_response: tuple[
		dict[str, object] | list[dict[str, object] | list[object] | primitive] | primitive,
		requests.Response
	] = to_session.get_profiles(query_params={"name": profile_name})
	try:
		profile_data = profile_get_response[0]
		if not isinstance(profile_data, list):
			raise TypeError("malformed API response; 'response' property not an array")

		first_profile = profile_data[0]
		if not isinstance(first_profile, dict):
			raise TypeError("malformed API response; first Profile in response is not an object")
		profile_response_template = response_template_data.get("profiles")
		if not isinstance(profile_response_template, dict):
			raise TypeError(
				f"Profile response template data must be a dict, not '{type(profile_response_template)}'")

		# validate profile values from prereq data in profiles get response.
		prereq_values = [profile_post_data["name"], profile_post_data["cdn"]]
		get_values = [first_profile["name"], first_profile["cdn"]]

		assert validate(instance=first_profile, schema=profile_response_template) == None
		assert get_values == prereq_values
	except IndexError:
		logger.error("Either prerequisite data or API response was malformed")
		pytest.fail("API contract test failed for cdn endpoint: API response was malformed")
	finally:
		# Delete Profile after test execution to avoid redundancy.
		try:
			profile_id = profile_post_data["id"]
			to_session.delete_profile_by_id(profile_id=profile_id)
		except IndexError:
			logger.error("Profile returned by Traffic Ops is missing an 'id' property")
			pytest.fail("Response from delete request is empty, Failing test_profile_contract")
