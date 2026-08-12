import re
from enum import Enum

from . import __version__ as protocol_version


class ToolAccess(Enum):
    PRIVATE = 0
    PROTECTED = 2
    HIDDEN = 5
    PUBLIC = 7


PROTOCOL_VERSION = protocol_version


ERROR_UNKNOWN = -999
ERROR_IMAGE_NOT_BUILDABLE = -890
ERROR_IMAGE_NOT_RUNNABLE = -850
ERROR_PACKAGE_NOT_INSTALLABLE = -500
ERROR_COMMAND_NOT_RUNNABLE = -350
ERROR_COMMAND_INTERRUPTED = -300
ERROR_TOOL_NOT_LOADABLE = -200
ERROR_CONFIGURATION_NOT_FOUND = -100


CONFIGURATION_NAME = 'automate.yaml'
TOOL_NAME = 'Tool X'
KIT_NAME = 'Kit X'
TOOL_VERSION = '0.0.0'


STEP_NAMES = 'input', 'log', 'output', 'print', 'debug'


VARIABLE_ID_PATTERN = re.compile(r'[a-zA-Z0-9_]+$')
VARIABLE_ID_TEMPLATE_PATTERN = re.compile(r'{ *([a-zA-Z0-9_| ]+?) *}')


DOMAIN_PATTERN = re.compile(r'[^a-z0-9.-]')


RAW_DATA_BYTE_COUNT = 16 * 1024
RAW_DATA_CACHE_LENGTH = 256


SCRIPT_LANGUAGE = 'python'
ENGINE_NAME = 'podman'
IMAGE_NAME = 'python:slim'


PRINTER_NAMES = ('pdf',)


SUPPORT_EMAIL = 'support@crosscompute.com'


STEP_INPUT = 'i'
STEP_OUTPUT = 'o'
STEP_LOG = 'l'
STEP_DEBUG = 'd'
STEP_PRINT = 'p'


DATA_VALUE = 'v'
DATA_PATH = 'p'
DATA_URI = 'u'
DATA_CONFIGURATION = 'c'
