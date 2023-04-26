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

"""API Contract Test Case for servers endpoint."""
import logging
import pytest
import requests
from jsonschema import validate

from trafficops.tosession import TOSession

# Create and configure logger
logger = logging.getLogger()

primitive = bool | int | float | str | None


def test_server_contract(
	to_session: TOSession,
	response_template_data: dict[str, primitive | list[primitive | dict[str, object]
						    | list[object]] | dict[object, object]],
	server_post_data: dict[str, object]
) -> None:
	"""
	Test step to validate keys, values and data types from servers endpoint
	response.
	:param to_session: Fixture to get Traffic Ops session.
	:param response_template_data: Fixture to get response template data from a prerequisites file.
	:param server_post_data: Fixture to get sample server data and actual server response.
	"""
	# validate server keys from server get response
	logger.info("Accessing /servers endpoint through Traffic ops session.")

	server_id = server_post_data.get("id")
	if not isinstance(server_id, int):
		raise TypeError("malformed API response; 'id' property not a integer")

	server_get_response: tuple[
		dict[str, object] | list[dict[str, object] | list[object] | primitive] | primitive,
		requests.Response
	] = to_session.get_servers(query_params={"id": server_id})
	try:
		server_data = server_get_response[0]
		if not isinstance(server_data, list):
			raise TypeError("malformed API response; 'response' property not an array")

		first_server = server_data[0]
		if not isinstance(first_server, dict):
			raise TypeError("malformed API response; first Server in response is not an object")
		logger.info("Server Api get response %s", first_server)
		server_response_template = response_template_data.get("servers")
		if not isinstance(server_response_template, dict):
			raise TypeError(
				f"Server response template data must be a dict, not '{type(server_response_template)}'")

		keys = ["cachegroupId", "cdnId", "domainName", "physLocationId", "profileNames",
	            "statusId", "typeId"]
		prereq_values = [server_post_data[key] for key in keys]
		get_values = [first_server[key] for key in keys]

		assert validate(instance=first_server, schema=server_response_template) is None
		assert get_values == prereq_values
	except IndexError:
		logger.error("Either prerequisite data or API response was malformed")
		pytest.fail("API contract test failed for server endpoint: API response was malformed")
	finally:
		# Delete Server after test execution to avoid redundancy.
		try:
			server_id = server_post_data["id"]
			to_session.delete_server_by_id(server_id=server_id)
		except IndexError:
			logger.error("Profile returned by Traffic Ops is missing an 'id' property")
			pytest.fail("Response from delete request is empty, Failing test_server_contract")
