import socket
from zeroconf import ServiceInfo
import re

from app.config import GET_SERVER_NAME

def _local_ip() -> str:
    """
    Best-effort to get a LAN IP (not 127.0.0.1).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable; just used to select an outbound interface.
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


async def build_service_info() -> ServiceInfo:
    SERVICE_TYPE = "_wannawatch._tcp.local."
    SERVER_NAME = await GET_SERVER_NAME()

    SERVICE_NAME = f"{SERVER_NAME}.{SERVICE_TYPE}"
    SERVICE_ADDRESS = re.sub(r'\W+', '_', SERVER_NAME).lower()

    host_ip = _local_ip()
    # TXT records (bytes). Put anything the client needs here.
    props = {
        b"api": b"/api",          # base path for API
        b"version": b"1",
    }

    return ServiceInfo(
        type_=SERVICE_TYPE,
        name=SERVICE_NAME,
        addresses=[socket.inet_aton(host_ip)],
        port=4000,
        properties=props,
        server=f"{SERVICE_ADDRESS}.local."
    )