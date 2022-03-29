import logging
import re
from typing import Dict, List

from meross_iot.controller.device import BaseDevice

from . import version
from .version import MEROSS_IOT_VERSION

_LOGGER = logging.getLogger(__name__)

# Constants
DOMAIN = "meross_cloud"
ATTR_CONFIG = "config"
MANAGER = "manager"
DEVICE_LIST_COORDINATOR = "device_list_coordinator"
LIMITER = "limiter"
CLOUD_HANDLER = "cloud_handler"
MEROSS_MANAGER = "%s.%s" % (DOMAIN, MANAGER)
SENSORS = "sensors"
HA_SWITCH = "switch"
HA_LIGHT = "light"
HA_SENSOR = "sensor"
HA_COVER = "cover"
HA_CLIMATE = "climate"
HA_FAN = "fan"
MEROSS_PLATFORMS = (HA_SWITCH, HA_LIGHT, HA_COVER, HA_FAN, HA_SENSOR, HA_CLIMATE)
CONNECTION_TIMEOUT_THRESHOLD = 5

CONF_STORED_CREDS = "stored_credentials"
CONF_MQTT_SKIP_CERT_VALIDATION = "skip_mqtt_cert_validation"
CONF_HTTP_ENDPOINT = "http_api_endpoint"

CONF_OPT_CUSTOM_USER_AGENT = "custom_user_agent"

HA_SENSOR_POLL_INTERVAL_SECONDS = 30     # HA sensor polling interval
HTTP_UPDATE_INTERVAL = 120               # Meross Cloud "discovery" interval
UNIT_PERCENTAGE = "%"

ATTR_API_CALLS_PER_SECOND = "api_calls_per_second"
ATTR_DELAYED_API_CALLS_PER_SECOND = "delayed_api_calls_per_second"
ATTR_DROPPED_API_CALLS_PER_SECOND = "dropped_api_calls_per_second"

HTTP_API_RE = re.compile("(http:\/\/|https:\/\/)?([^:]+)(:([0-9]+))?")

DEFAULT_USER_AGENT = f"MerossHA/{version.MEROSS_INTEGRATION_VERSION}"


def calculate_id(platform: str, uuid: str, channel: int, supplementary_classifiers: List[str] = None) -> str:
    base = "%s:%s:%d" % (platform, uuid, channel)
    if supplementary_classifiers is not None:
        extrastr = ":".join(supplementary_classifiers)
        if extrastr != "":
            extrastr = ":" + extrastr
        return base + extrastr
    return base


def dismiss_notification(hass, notification_id):
    hass.async_create_task(
        hass.services.async_call(
            domain="persistent_notification",
            service="dismiss",
            service_data={"notification_id": "%s.%s" % (DOMAIN, notification_id)},
        )
    )


def notify_error(hass, notification_id, title, message):
    hass.async_create_task(
        hass.services.async_call(
            domain="persistent_notification",
            service="create",
            service_data={
                "title": title,
                "message": message,
                "notification_id": "%s.%s" % (DOMAIN, notification_id),
            },
        )
    )


def log_exception(
        message: str = None, logger: logging = None, device: BaseDevice = None
):
    if logger is None:
        logger = logging.getLogger(__name__)

    if message is None:
        message = "An exception occurred"

    device_info = "<Unavailable>"
    if device is not None:
        device_info = (
            f"\tName: {device.name}\n"
            f"\tUUID: {device.uuid}\n"
            f"\tType: {device.type}\n\t"
            f"HW Version: {device.hardware_version}\n"
            f"\tFW Version: {device.firmware_version}"
        )

    formatted_message = (
        f"Error occurred.\n"
        f"-------------------------------------\n"
        f"Component version: {MEROSS_IOT_VERSION}\n"
        f"Device info: \n"
        f"{device_info}\n"
        f'Error Message: "{message}"'
    )
    logger.exception(formatted_message)


def invoke_method_or_property(obj, method_or_property):
    # We only call the explicit method if the sampled value is older than 10 seconds.
    attr = getattr(obj, method_or_property)
    if callable(attr):
        return attr()
    else:
        return attr


def extract_subdevice_notification_data(
        data: dict, filter_accessor: str, subdevice_id: str
) -> Dict:
    # Operate only on relative accessor
    context = data.get(filter_accessor)

    for notification in context:
        if notification.get("id") != subdevice_id:
            continue
        return notification
