# Exotel IP Whitelist Middleware
EXOTEL_IP_RANGES = [
    '14.141.14.0/24',      # Exotel India
    '115.110.0.0/16',      # Exotel India
    '54.251.82.0/24',      # Exotel AWS
    '52.66.146.0/24',      # Exotel AWS Mumbai
    '3.7.16.0/24',         # Exotel AWS
]

import ipaddress

def is_exotel_ip(client_ip: str) -> bool:
    """Check if IP is from Exotel's network."""
    try:
        client = ipaddress.ip_address(client_ip)
        for range_str in EXOTEL_IP_RANGES:
            network = ipaddress.ip_network(range_str, strict=False)
            if client in network:
                return True
        return False
    except ValueError:
        return False
