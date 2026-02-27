from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstAnonRateThrottle(AnonRateThrottle):
    scope = "burst_anon"


class SustainedAnonRateThrottle(AnonRateThrottle):
    scope = "sustained_anon"


class BurstUserRateThrottle(UserRateThrottle):
    scope = "burst_user"


class SustainedUserRateThrottle(UserRateThrottle):
    scope = "sustained_user"
