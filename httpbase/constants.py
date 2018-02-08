from typing import NamedTuple


class _HTTPMethods(NamedTuple):
    GET: str = "get"
    PUT: str = "put"
    POST: str = "post"
    DELETE: str = "delete"
    PATCH: str = "patch"
    HEAD: str = "head"
    OPTIONS: str = "options"


class _HTTPResponseCodes(NamedTuple):
    # Informational.
    CONTINUE: int = 100
    SWITCHING_PROTOCOLS: int = 101
    PROCESSING: int = 102
    CHECKPOINT: int = 103
    URI_TOO_LONG: int = 122
    OK: int = 200
    CREATED: int = 201
    ACCEPTED: int = 202
    NON_AUTHORITATIVE_INFO: int = 203
    NO_CONTENT: int = 204
    RESET_CONTENT: int = 205
    PARTIAL_CONTENT: int = 206
    MULTI_STATUS: int = 207
    ALREADY_REPORTED: int = 208
    IM_USED: int = 226

    # Redirection.
    MULTIPLE_CHOICES: int = 300
    MOVED_PERMANENTLY: int = 301
    FOUND: int = 302
    SEE_OTHER: int = 303
    NOT_MODIFIED: int = 304
    USE_PROXY: int = 305
    SWITCH_PROXY: int = 306
    TEMPORARY_REDIRECT: int = 307
    PERMANENT_REDIRECT: int = 308

    # Client Error.
    BAD_REQUEST: int = 400
    UNAUTHORIZED: int = 401
    PAYMENT_REQUIRED: int = 402
    FORBIDDEN: int = 403
    NOT_FOUND: int = 404
    METHOD_NOT_ALLOWED: int = 405
    NOT_ACCEPTABLE: int = 406
    PROXY_AUTHENTICATION_REQUIRED: int = 407
    REQUEST_TIMEOUT: int = 408
    CONFLICT: int = 409
    GONE: int = 410
    LENGTH_REQUIRED: int = 411
    PRECONDITION_FAILED: int = 412
    REQUEST_ENTITY_TOO_LARGE: int = 413
    REQUEST_URI_TOO_LARGE: int = 414
    UNSUPPORTED_MEDIA_TYPE: int = 415
    REQUESTED_RANGE_NOT_SATISFIABLE: int = 416
    EXPECTATION_FAILED: int = 417
    TEAPOT: int = 418
    ENHANCE_YOUR_CALM: int = 420
    MISDIRECTED_REQUEST: int = 421
    UNPROCESSABLE_ENTITY: int = 422
    LOCKED: int = 423
    FAILED_DEPENDENCY: int = 424
    UNORDERED_COLLECTION: int = 425
    UPGRADE_REQUIRED: int = 426
    PRECONDITION_REQUIRED: int = 428
    TOO_MANY_REQUESTS: int = 429
    HEADER_FIELDS_TOO_LARGE: int = 431
    NO_RESPONSE: int = 444
    RETRY_WITH: int = 449
    BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS: int = 450
    UNAVAILABLE_FOR_LEGAL_REASONS: int = 451
    CLIENT_CLOSED_REQUEST: int = 499

    # Server Error.
    INTERNAL_SERVER_ERROR: int = 500
    NOT_IMPLEMENTED: int = 501
    BAD_GATEWAY: int = 502
    SERVICE_UNAVAILABLE: int = 503
    GATEWAY_TIMEOUT: int = 504
    HTTP_VERSION_NOT_SUPPORTED: int = 505
    VARIANT_ALSO_NEGOTIATES: int = 506
    INSUFFICIENT_STORAGE: int = 507
    BANDWIDTH_LIMIT_EXCEEDED: int = 509
    NOT_EXTENDED: int = 510
    NETWORK_AUTHENTICATION_REQUIRED: int = 511


HTTPMethods = _HTTPMethods()
HTTPResponseCodes = _HTTPResponseCodes()
