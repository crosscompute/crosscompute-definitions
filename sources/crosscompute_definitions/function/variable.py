from logging import getLogger
from os.path import join, splitext

from crosscompute_macros.disk import (
    FileCache,
    get_byte_count,
    is_existing_path,
    load_raw_json,
    load_raw_text)
from crosscompute_macros.error import (
    DiskError,
    ParsingError)
from crosscompute_macros.log import (
    redact_path)

from ..constant import (
    DATA_CONFIGURATION,
    DATA_CONFIGURATION_CACHE_LENGTH,
    DATA_PATH,
    DATA_VALUE,
    RAW_DATA_BYTE_COUNT,
    RAW_DATA_CACHE_LENGTH)
from ..error import (
    CrossComputeConfigurationError,
    CrossComputeDataError)
from ..setting import (
    view_by_name)
from .disk import (
    get_matching_paths)


class LoadableVariableView:

    name = 'variable'

    @classmethod
    def get_from(Class, variable):
        view_name = variable.view_name
        try:
            View = view_by_name[view_name]
        except KeyError:
            L.error(
                'view "%s" is not installed and is needed by variable "%s"',
                view_name, variable.id)
            View = Class
        return View(variable)

    def __init__(self, variable):
        self.variable = variable

    async def parse_value_safely(self, v, w):
        try:
            return await self.parse_value(v)
        except CrossComputeDataError as e:
            L.error(f'variable value parse failed during {w}: {e}')

    async def parse_value(self, x):
        return x

    def parse_configuration_safely(self, c, w):
        if isinstance(c, dict):
            try:
                configuration = self.parse_configuration(c)
            except CrossComputeConfigurationError as e:
                L.error(f'variable configuration parse failed during {w}: {e}')
        else:
            L.error('variable configuration must be a dictionary')
            configuration = None
        return configuration

    def parse_configuration(self, c):
        return c


async def load_variable_data_by_id(folder, variables):
    data_by_id = {}
    for variable in variables:
        try:
            variable_data = await load_variable_data(folder, variable)
        except CrossComputeDataError as e:
            L.debug(e)
            continue
        data_by_id[variable.id] = variable_data
    return data_by_id


async def load_variable_data(
        folder, variable, *, with_configuration_path=True):
    path = join(folder, variable.path_name)  # noqa: PTH118
    variable_id = variable.id
    try:
        variable_data = await raw_data_cache.get(path)
    except CrossComputeDataError as e:
        e.variable_id = variable_id
        raise
    if path.endswith('.dictionary'):
        variable_data = load_variable_data_from(
            variable_data[DATA_VALUE], variable_id)
    configuration = {}
    configuration_path = get_variable_configuration_path(variable, folder)
    if with_configuration_path:
        configuration.update(await variable_configuration_cache.get(
            configuration_path))
    view = LoadableVariableView.get_from(variable)
    if DATA_VALUE in variable_data:
        value = await view.parse_value_safely(
            variable_data[DATA_VALUE], 'load')
        if value is not None:
            variable_data[DATA_VALUE] = value
    if configuration:
        configuration = view.parse_configuration_safely(
            configuration, 'load')
        if configuration:
            variable_data[DATA_CONFIGURATION] = configuration
    return variable_data


def get_variable_configuration_path(variable, folder):
    variable_id = variable.id
    return join(folder, f'{variable_id}.configuration')  # noqa: PTH118


def load_variable_data_from(variable_value_by_id, variable_id):
    try:
        variable_value = variable_value_by_id[variable_id]
    except KeyError as e:
        x = 'value was not found'
        raise CrossComputeDataError(
            x, variable_id=variable_id) from e
    return {DATA_VALUE: variable_value}


async def load_raw_data(path):
    try:
        matching_paths = await get_matching_paths(path)
    except OSError as e:
        x = 'path does not exist'
        raise CrossComputeDataError(x, path=path) from e
    match len(matching_paths):
        case 0:
            x = 'path does not exist'
            raise CrossComputeDataError(x, path=path)
        case 1:
            path = matching_paths[0]
        case _:
            return {DATA_PATH: path}
    suffix = splitext(path)[1]  # noqa: PTH122
    if suffix == '.dictionary':
        return await load_dictionary_data(path)
    if suffix in ['.md', '.txt']:
        return await load_file_data(path, load_raw_text)
    if suffix in ['.geojson', '.json']:
        return await load_file_data(path, load_raw_json)
    return {DATA_PATH: path}


async def load_dictionary_data(path):
    try:
        value = await load_raw_json(path)
    except (DiskError, ParsingError) as e:
        raise CrossComputeDataError(e) from e
    if not isinstance(value, dict):
        x = 'dictionary expected'
        raise CrossComputeDataError(x, path=path)
    return {DATA_VALUE: value}


async def load_file_data(path, load):
    try:
        byte_count = await get_byte_count(path)
        if byte_count > RAW_DATA_BYTE_COUNT:
            return {DATA_PATH: path}
        value = await load(path)
    except (DiskError, ParsingError) as e:
        raise CrossComputeDataError(e) from e
    return {DATA_VALUE: value}


async def load_variable_configuration(path):
    d = {}
    if await is_existing_path(path):
        try:
            d = await load_raw_json(path)
        except (DiskError, ParsingError) as e:
            L.error(e)
        else:
            if not isinstance(d, dict):
                L.error(
                    'variable configuration must be a dictionary; '
                    f'path="{redact_path(path)}"')
                d = {}
    return d


raw_data_cache = FileCache(
    load=load_raw_data,
    length=RAW_DATA_CACHE_LENGTH)
variable_configuration_cache = FileCache(
    load=load_variable_configuration,
    length=DATA_CONFIGURATION_CACHE_LENGTH)
L = getLogger(__name__)
