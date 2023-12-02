import json
import pytest
from main import is_valid_relative_file_path, check_new_json, get_json_diff


class TestRelativeFilePath:

    @pytest.mark.asyncio
    async def test_valid_file_path(self, tmp_path):
        test_file = tmp_path / "existing_file.txt"
        test_file.write_text("test")

        assert await is_valid_relative_file_path(test_file) is None

    @pytest.mark.asyncio
    async def test_invalid_file_path(self):
        invalid_path = "non_existing_file.txt"
        with pytest.raises(ValueError):
            await is_valid_relative_file_path(invalid_path)


class TestGetJsonDiff:

    @pytest.mark.asyncio
    async def test_get_json_diff_with_value(self):
        expected = {'key1': 'value1', 'key2': 'value2'}
        differences = {'key1': 'value3'}
        with pytest.raises(ValueError) as e:
            await get_json_diff(expected, differences)
        assert str(e.value) == "Expected: 'key1': value1, Actual: value3"

    @pytest.mark.asyncio
    async def test_get_json_diff_missing_value(self):
        expected = {'key1': 'value1', 'key2': 'value2'}
        differences = {'key3': None}
        with pytest.raises(ValueError) as e:
            await get_json_diff(expected, differences)
        assert str(e.value) == "Expected: 'key3': None, but the parameter is missing"


class TestCorrectNewJsonData:

    @pytest.mark.asyncio
    async def test_correct_axiswise_rot_new_json(self):
        with open('axiswise_rot/axiswise_rot.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        print(data)
        assert await check_new_json(data) is None

    @pytest.mark.asyncio
    async def test_correct_axiswise_swap_new_json(self):
        with open('axis_swap/axis_swap.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        print(data)
        assert await check_new_json(data) is None

    @pytest.mark.asyncio
    async def test_correct_conv_ply_xyz_new_json(self):
        with open('conv_ply_xyz/conv_ply_xyz.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        print(data)
        assert await check_new_json(data) is None

    @pytest.mark.asyncio
    async def test_correct_height_color_new_json(self):
        with open('height_color/height_color.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        assert await check_new_json(data) is None

    @pytest.mark.asyncio
    async def test_correct_unbag_new_json(self):
        with open('unbag/unbug.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        print(data)
        assert await check_new_json(data) is None


async def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


@pytest.mark.asyncio
@pytest.mark.parametrize('json_file', [
    'axiswise_rot/axiswise_rot_diff_id.json',
    'axiswise_rot/axiswise_rot_wrong_params.json'
])
async def test_incorrect_json_data(json_file):
    data = await load_json_data(json_file)
    with pytest.raises(ValueError):
        await check_new_json(data)


async def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


class TestIncorrectNewJson:

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_diff_id.json',
        'axiswise_rot/axiswise_rot_diff_id.json',
        'conv_ply_xyz/conv_ply_xyz_diff_id.json',
        'height_color/height_color_diff_id.json',
        'unbag/unbag_diff_id.json'
    ])
    async def test_incorrect_id(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_diff_oper_type.json',
        'axiswise_rot/axiswise_rot_diff_oper_type.json',
        'conv_ply_xyz/conv_ply_xyz_diff_oper_type.json',
        'height_color/height_color_diff_oper_type.json',
        'unbag/unbag_diff_oper_type.json'
    ])
    async def test_incorrect_oper_type(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_diff_output.json',
        'axiswise_rot/axiswise_rot_diff_output.json',
        'conv_ply_xyz/conv_ply_xyz_diff_output.json',
        'height_color/height_color_diff_output.json',
        'unbag/unbag_diff_output.json'
    ])
    async def test_incorrect_output(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_empty_directory.json',
        'axiswise_rot/axiswise_rot_empty_directory.json',
        'conv_ply_xyz/conv_ply_xyz_empty_directory.json',
        'height_color/height_color_empty_directory.json',
        'unbag/unbag_empty_directory.json'
    ])
    async def test_incorrect_empty_directory(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_empty_params.json',
        'axiswise_rot/axiswise_rot_empty_params.json',
        'height_color/height_color_empty_params.json'
    ])
    async def test_incorrect_empty_params(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_wrong_directory.json',
        'axiswise_rot/axiswise_rot_wrong_directory.json',
        'conv_ply_xyz/conv_ply_xyz_wrong_directory.json',
        'height_color/height_color_wrong_directory.json',
        'unbag/unbag_wrong_directory.json'
    ])
    async def test_incorrect_wrong_directory(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('json_file', [
        'axis_swap/axis_swap_wrong_params.json',
        'axiswise_rot/axiswise_rot_wrong_params.json',
        'height_color/height_color_wrong_params.json'
    ])
    async def test_incorrect_wrong_params(self, json_file):
        data = await load_json_data(json_file)
        with pytest.raises(ValueError):
            await check_new_json(data)
