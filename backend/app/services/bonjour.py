import socket
from zeroconf import ServiceInfo

SERVICE_TYPE = "_wannawatch._tcp.local."
SERVICE_NAME = "WannaWatch Server 6969._wannawatch._tcp.local." #WannaWatchServer is the name shown. TODO: Set this to the server name, when it's stored in the DB

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


def build_service_info() -> ServiceInfo:
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
        server="wannawatch_server_6969.local.",  # can be any stable hostname; not strictly required TODO: Set this to something individual so people can have more than one server connected. 
    )