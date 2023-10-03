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

"""API Contract Test Case for service_categories endpoint."""
import logging
from random import randint
from typing import Union
import pytest
import requests
from jsonschema import validate

from trafficops.tosession import TOSession

# Create and configure logger
logger = logging.getLogger()

Primitive = Union[bool, int, float, str, None]


def test_service_categories_contract(to_session: TOSession,
	response_template_data: dict[str, Union[Primitive, list[Union[Primitive,
							dict[str, object], list[object]]], dict[object, object]]],
							pytestconfig: pytest.Config,
	service_category_post_data: dict[str, object]
) -> None:
	"""
	Test step to validate keys, values and data types from service_category endpoint
	response.
	:param to_session: Fixture to get Traffic Ops session.
	:param response_template_data: Fixture to get response template data from a prerequisites file.
	:param service_category_post_data: Fixture to get service categories data.
	"""
	# validate service_category keys from api get response
	logger.info("Accessing /service_category endpoint through Traffic ops session.")

	service_category_name = service_category_post_data["name"]
	if not isinstance(service_category_name, str):
		raise TypeError("malformed API response; 'service_category_name' property not a string")

	service_category_get_response: tuple[
		Union[dict[str, object], list[Union[dict[str, object], list[object], Primitive]], Primitive],
		requests.Response
	] = to_session.get_service_categories(query_params={"name":service_category_name})

	# Hitting service_category PUT method
	service_category_new_name = "test" + str(randint(0, 1000)) 
	pytestconfig.cache.set("service_category_name", service_category_new_name)
	put_response: tuple[
		Union[dict[str, object], list[Union[dict[str, object], list[object], Primitive]], Primitive], 
		requests.Response] = to_session.update_service_category(service_category_name=service_category_name, data={"name":service_category_new_name,})
    
	try:
		service_category = service_category_get_response[0]
		if not isinstance(service_category, list):
			raise TypeError(
				"malformed API response; first service_category in response is not an array")
		first_service_category = service_category[0]

		service_category_put_data = put_response[0]
		if not isinstance(service_category_put_data, list):
			raise TypeError("malformed API response; 'response' property not an array")
		service_category_put_response = service_category_put_data[0]
		if not isinstance(service_category_put_response, dict):
			raise TypeError("malformed API response; service_category in response is not an dict")
		logger.info("service_category Api put response %s", service_category_put_response)

		service_category_response_template = response_template_data.get(
			"service_category")
		if not isinstance(service_category_response_template, dict):
			raise TypeError(f"service_category response template data must be a dict, not'"
							f"{type(service_category_response_template)}'")

		assert validate(instance=first_service_category, schema=service_category_response_template) is None
		assert validate(instance=service_category_put_response, schema=service_category_response_template) is None
		
	except IndexError:
		logger.error("Either prerequisite data or API response was malformed")
		pytest.fail("API contract test failed for service_category endpoint: API response was malformed")
