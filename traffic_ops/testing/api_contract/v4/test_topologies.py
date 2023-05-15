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

"""API Contract Test Case for topologies endpoint."""
import logging
import pytest
import requests
from jsonschema import validate

from trafficops.tosession import TOSession

# Create and configure logger
logger = logging.getLogger()

primitive = bool | int | float | str | None


def test_topologies_contract(
	to_session: TOSession,
	response_template_data: dict[str, primitive | list[primitive | dict[str, object]
						    | list[object]] | dict[object, object]],
	topologies_post_data: dict[str, object]
) -> None:
	"""
	Test step to validate keys, values and data types from topologies endpoint
	response.
	:param to_session: Fixture to get Traffic Ops session.
	:param response_template_data: Fixture to get response template data from a prerequisites file.
	:param topologies_post_data: Fixture to get sample topologies data and actual topologies response.
	"""
	# validate topologies keys from topologies get response
	logger.info("Accessing /topologies endpoint through Traffic ops session.")

	topologies_id = topologies_post_data.get("id")
	if not isinstance(topologies_id, int):
		raise TypeError("malformed API response; 'id' property not a integer")

	topologies_get_response: tuple[
		dict[str, object] | list[dict[str, object] | list[object] | primitive] | primitive,
		requests.Response
	] = to_session.get_topologies(query_params={"id": topologies_id})
	try:
		topologies_data = topologies_get_response[0]
		if not isinstance(topologies_data, list):
			raise TypeError("malformed API response; 'response' property not an array")

		first_topologies = topologies_data[0]
		if not isinstance(first_topologies, dict):
			raise TypeError("malformed API response; first topologies in response is not an object")
		logger.info("topologies Api get response %s", first_topologies)
		topologies_response_template = response_template_data.get("topologies")
		if not isinstance(topologies_response_template, dict):
			raise TypeError(
				f"topologies response template data must be a dict, not '{type(topologies_response_template)}'")

		keys = ["cachegroupId", "cdnId", "domainName", "physLocationId", "profileNames",
	            "statusId", "typeId"]
		prereq_values = [topologies_post_data[key] for key in keys]
		get_values = [first_topologies[key] for key in keys]

		assert validate(instance=first_topologies, schema=topologies_response_template) is None
		assert get_values == prereq_values
	except IndexError:
		logger.error("Either prerequisite data or API response was malformed")
		pytest.fail("API contract test failed for topologies endpoint: API response was malformed")
	finally:
		# Delete topologies after test execution to avoid redundancy.
		try:
			topology_name = topologies_post_data["name"]
			to_session.delete_topology(name=topology_name)
		except IndexError:
			logger.error("Profile returned by Traffic Ops is missing an 'id' property")
			pytest.fail("Response from delete request is empty, Failing test_topologies_contract")
