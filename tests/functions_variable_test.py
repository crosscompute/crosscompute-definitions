import json

import aiofiles
import pytest

from crosscompute_macros.abstract import (
    Clay)
from crosscompute_views.base import (
    initialize_view_by_name)

from crosscompute_definitions.constant import (
    DATA_CONFIGURATION,
    DATA_VALUE)
from crosscompute_definitions.function.variable import (
    get_variable_configuration_path,
    load_variable_data)


@pytest.mark.asyncio
async def test_load_variable_data(tmp_path):
    folder = tmp_path
    path_name = 'v.dictionary'
    path = folder / path_name
    initialize_view_by_name()
    variable = Clay(
        id='a',
        view_name='number',
        path_name=path_name,
        configuration={})
    configuration_path = get_variable_configuration_path(variable, tmp_path)

    async with aiofiles.open(path, mode='w') as f:
        await f.write(json.dumps({'a': 'a'}))
    variable_data = await load_variable_data(folder, variable)
    assert DATA_VALUE not in variable_data[DATA_VALUE]

    async with aiofiles.open(path, mode='w') as f:
        await f.write(json.dumps({'a': 1}))
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert DATA_CONFIGURATION not in variable_data

    async with aiofiles.open(configuration_path, mode='w') as f:
        await f.write('a')
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert DATA_CONFIGURATION not in variable_data

    async with aiofiles.open(configuration_path, mode='w') as f:
        await f.write('"a"')
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert DATA_CONFIGURATION not in variable_data

    variable = Clay(
        id='a',
        view_name='string',
        path_name=path_name,
        configuration={})

    async with aiofiles.open(configuration_path, mode='w') as f:
        await f.write(json.dumps({'suggestions': []}))
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert DATA_CONFIGURATION not in variable_data

    async with aiofiles.open(configuration_path, mode='w') as f:
        await f.write(json.dumps({'suggestions': [{}]}))
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert DATA_CONFIGURATION not in variable_data

    async with aiofiles.open(configuration_path, mode='w') as f:
        await f.write(json.dumps({'suggestions': [{'value': 1}]}))
    variable_data = await load_variable_data(folder, variable)
    assert variable_data[DATA_VALUE] == 1
    assert variable_data[DATA_CONFIGURATION] == {
        'suggestions': [{'value': "1"}]}


# ruff: noqa: S101
