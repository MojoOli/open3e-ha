"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any, Callable

import aiohttp
import async_timeout
from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant

from .const import MQTT_CONFIG_TOPIC


class IntegrationBlueprintApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationBlueprintApiClientCommunicationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate a communication error."""


class IntegrationBlueprintApiClientAuthenticationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationBlueprintApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class IntegrationBlueprintApiClient:
    """Sample API Client."""

    def __init__(
            self,
            username: str,
            password: str,
            session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
            self,
            method: str,
            url: str,
            data: dict | None = None,
            headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise IntegrationBlueprintApiClientError(
                msg,
            ) from exception


class Open3eMqttClient:
    """Open3e Mqtt Client."""

    _mqtt_cmd: str

    def __init__(
            self,
            mqtt_cmd: str
    ) -> None:
        """Sample API Client."""
        self._mqtt_cmd = mqtt_cmd

    async def async_request_config(self, hass: HomeAssistant, config_callback: Callable):
        # mqtt.subscribe(hass=hass, topic=MQTT_CONFIG_TOPIC, msg_callback=config_callback)
        """Get data from the API."""
        return await mqtt.async_publish(hass=hass, topic=self._mqtt_cmd, payload='{"mode":"config"}')

    # async def async_set_title(self, value: str) -> Any:
    #     """Get data from the API."""
    #     return await self._api_wrapper(
    #         method="patch",
    #         url="https://jsonplaceholder.typicode.com/posts/1",
    #         data={"title": value},
    #         headers={"Content-type": "application/json; charset=UTF-8"},
    #     )
    #
    # async def _api_wrapper(
    #         self,
    #         method: str,
    #         url: str,
    #         data: dict | None = None,
    #         headers: dict | None = None,
    # ) -> Any:
    #     """Get information from the API."""
    #     try:
    #         async with async_timeout.timeout(10):
    #             response = await self._session.request(
    #                 method=method,
    #                 url=url,
    #                 headers=headers,
    #                 json=data,
    #             )
    #             _verify_response_or_raise(response)
    #             return await response.json()
    #
    #     except TimeoutError as exception:
    #         msg = f"Timeout error fetching information - {exception}"
    #         raise IntegrationBlueprintApiClientCommunicationError(
    #             msg,
    #         ) from exception
    #     except (aiohttp.ClientError, socket.gaierror) as exception:
    #         msg = f"Error fetching information - {exception}"
    #         raise IntegrationBlueprintApiClientCommunicationError(
    #             msg,
    #         ) from exception
    #     except Exception as exception:  # pylint: disable=broad-except
    #         msg = f"Something really wrong happened! - {exception}"
    #         raise IntegrationBlueprintApiClientError(
    #             msg,
    #         ) from exception
