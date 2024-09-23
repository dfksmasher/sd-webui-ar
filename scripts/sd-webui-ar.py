import contextlib
from pathlib import Path

import gradio as gr

import modules.scripts as scripts
from modules.ui_components import ToolButton

from math import gcd

aspect_ratios_dir = scripts.basedir()

calculator_symbol = "\U0001F5A9"
switch_values_symbol = "\U000021C5"
get_dimensions_symbol = "\u2B07\ufe0f"
get_image_dimensions_symbol = "\U0001F5BC"


class ResButton(ToolButton):
    def __init__(self, res=(512, 512), **kwargs):
        super().__init__(**kwargs)

        self.w, self.h = res

    def reset(self):
        return [self.w, self.h]


class ARButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)

        self.ar = ar

    def apply(self, w, h):
        if self.ar > 1.0:  # fix height, change width
            w = self.ar * h
        elif self.ar < 1.0:  # fix width, change height
            h = w / self.ar
        else:  # set minimum dimension to both
            min_dim = min([w, h])
            w, h = min_dim, min_dim

        return list(map(round, [w, h]))

    def reset(self, w, h):
        return [self.res, self.res]


def parse_aspect_ratios_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)

    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        if ',' not in line:
            continue

        try:
            label, value = line.strip().split(",")
            comment = ""
            if "#" in value:
                value, comment = value.split("#")
        except ValueError:
            print(f"skipping badly formatted line in aspect ratios file: {line}")
            continue

        labels.append(label)
        values.append(eval(value))
        comments.append(comment)

    return labels, values, comments


def parse_resolutions_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)

    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        if ',' not in line:
            continue

        try:
            label, width, height = line.strip().split(",")
            comment = ""
            if "#" in height:
                height, comment = height.split("#")
        except ValueError:
            print(f"skipping badly formatted line in resolutions file: {line}")
            continue

        resolution = (width, height)

        labels.append(label)
        values.append(resolution)
        comments.append(comment)

    return labels, values, comments


# TODO: write a generic function handling both cases
def write_aspect_ratios_file(filename):
    aspect_ratios = [
        "1:1, 1.0 # 1:1 ratio based on minimum dimension\n",
        "3:2, 3/2 # Set width based on 3:2 ratio to height\n",
        "4:3, 4/3 # Set width based on 4:3 ratio to height\n",
        "16:9, 16/9 # Set width based on 16:9 ratio to height",
    ]
    with open(filename, "w", encoding="utf-
