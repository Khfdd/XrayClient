import pathlib


WORK_DIR = pathlib.Path(__file__).resolve().parent
WORK_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = WORK_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Happ/3.18.1/Android/17764321936841767581',
    'X-Device-Locale': 'en',
    'X-Hwid': 'dcf74070417723f7',
    'X-Device-Os': 'Android',
    'X-Ver-Os': '13',
    'X-Device-Model': 'RMX3511',
    'Accept-Encoding': 'gzip'
}

XRAY_CONFIG_FILE = pathlib.Path("/usr/local/etc/xray/config.json")
XRAY_GEOIP_FILE = pathlib.Path("/usr/local/share/xray/geoip.dat")
XRAY_GEOSITE_FILE = pathlib.Path("/usr/local/share/xray/geosite.dat")
INBOUNDS = [
    {
        "protocol": "tun",
        "settings": {
            "name": "tun0",
            "mtu": 1400,
            "gateway": [
                    "10.0.0.1/16",
                    "fc00::1/64"
            ],
            "userLevel": 0
        },
        "tag": "tun0",
        "sniffing": {
            "enabled": True,
            "routeOnly": False,
            "destOverride": [
                "http",
                "tls",
                "quic"
            ]
        }
    },
    {
        "tag": "socks",
        "port": 10808,
        "listen": "127.0.0.1",
        "protocol": "socks",
        "settings": {
            "udp": True,
            "auth": "noauth"
        },
        "sniffing": {
            "enabled": True,
            "routeOnly": False,
            "destOverride": [
                "http",
                "tls",
                "quic"
            ]
        }
    },
    {
        "tag": "http",
        "port": 10809,
        "listen": "127.0.0.1",
        "protocol": "http",
        "settings": {
            "allowTransparent": False
        },
        "sniffing": {
            "enabled": True,
            "routeOnly": False,
            "destOverride": [
                "http",
                "tls",
                "quic"
            ]
        }
    }
]
