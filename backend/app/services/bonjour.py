import socket
from zeroconf import ServiceInfo

SERVICE_TYPE = "_wannawatch._tcp.local."
SERVICE_NAME = "WannaWatchServer._wannawatch._tcp.local."

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


def build_service_info(host_ip: str) -> ServiceInfo:
    # TXT records (bytes). Put anything the client needs here.
    props = {
        b"api": b"/api",          # base path for API
        b"version": b"1",
        b"directplay": b"1",      # you can add codec/container flags later
    }

    return ServiceInfo(
        type_=SERVICE_TYPE,
        name=SERVICE_NAME,
        addresses=[socket.inet_aton(host_ip)],
        port=4000,
        properties=props,
        server="wannawatch_server.local.",  # can be any stable hostname; not strictly required
    )