from rest_framework.throttling import UserRateThrottle


class ReceiveThrottle(UserRateThrottle):
    scope = "receive_virtual_content"
