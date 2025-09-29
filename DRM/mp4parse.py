# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2025/9/29 17:26
# @Version     : Python 3.13.2
import base64
import json
import os
import platform
from pathlib import Path


def mp4dump(file: str):
    binaries_dir = Path(__file__).resolve().parent / 'binaries'
    dump_programs = {
        'Windows': (binaries_dir / 'mp4dump.exe').as_posix(),
        'Linux': (binaries_dir / 'mp4dump_linux').as_posix(),
        'Darwin': (binaries_dir / 'mp4dump_mac').as_posix(),
    }
    return json.loads(os.popen(f'{dump_programs[platform.system()]} {file} --format json').read())


# def to_dict(mp4struct: list, data: dict = None):
#     """
#     将mp4dump返回的列表数据字典化,但会导致相同字段只保留一个,如pssh
#     """
#     if data is None:
#         data = {}
#     for children in mp4struct:
#         name = children['name']
#         if 'children' in children and isinstance(children['children'], list):
#             children_data = to_dict(children.pop('children'))
#             children.update(children_data)
#         data[name] = children
#
#     return data


def get_kids(mp4struct: dict) -> list:
    """值为空表示不存在 kid """
    kids = []
    kids_path = ['moov', 'trak', 'mdia', 'minf', 'stbl', 'stsd', ['encv', 'enca'], 'sinf', 'schi', 'tenc']
    if f"'{kids_path[-1]}'" not in str(mp4struct):
        return kids
    while kids_path[:-1]:
        p = kids_path.pop(0)
        children = mp4struct['children'] if 'children' in mp4struct else mp4struct
        for child in children:
            if (
                    (isinstance(p, str) and child['name'] == p)
                    or (isinstance(p, list) and child['name'] in p)
            ):
                mp4struct = child
                break
    for child in mp4struct['children']:
        if child['name'] == kids_path[-1]:
            kids.append(child['default_KID'][1:-1].replace(' ', ''))
    if not kids:
        raise ValueError('有但是未解析到KID')
    return kids


def get_pssh(mp4struct: dict, file: str) -> str:
    """
    pssh 可能存在于 moov/moof 中
    值为空表示不存在 pssh
    """
    tag = 'pssh'
    if f"'{tag}'" not in str(mp4struct):
        return ''
    start = 0
    for child in mp4struct:
        if child['name'] in ['moov', 'moof']:
            start += child['header_size']
            for sub_child in child['children']:
                if sub_child['name'] == tag:
                    system_id = sub_child['system_id'][1:-1].replace(' ', '')
                    if system_id == 'edef8ba979d64acea3c827dcd51d21ed':
                        size = sub_child['size']
                        with open(file, mode='rb') as f:
                            return base64.b64encode(f.read(start + size)[-size:]).decode('utf-8')
                start += sub_child['size']
        else:
            start += child['size']
    raise ValueError('有但是未解析到PSSH')
