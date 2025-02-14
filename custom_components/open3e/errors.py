from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.open3e.const import DOMAIN


class Open3eServerTimeoutError(
    HomeAssistantError
):
    """Exception to indicate a timeout error."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="timeout"
        )


class Open3eServerUnavailableError(
    HomeAssistantError
):
    """Exception to indicate that the server is unavailable."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="unavailable"
        )


class Open3eError(
    HomeAssistantError
):
    """Exception to indicate a MQTT error."""

    def __init__(self, exception: Exception) -> None:
        """Initialize the error."""
        super().__init__(
            exception,
            translation_domain=DOMAIN,
            translation_key="mqtt"
        )


class Open3eCoordinatorUpdateFailed(
    UpdateFailed
):
    """Exception to indicate an Update error."""
