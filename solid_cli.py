from __future__ import annotations

import argparse
import copy
import os
import subprocess
import tempfile
from typing import List

from solid import OpenSCADObject, scad_render

POSSIBLE_ARGS = {
    "cmd",
    "cmd_name",
    "print",
    "preview",
    "model",
    "scad_file",
    "target_file",
}


class Args:
    @classmethod
    def from_argparse(cls, args: argparse.Namespace) -> Args:
        """
        This function builds this class from an argument namespace that
        was parsed from the associated model
        """
        args_dict = copy.deepcopy(vars(args))
        for possible_arg in POSSIBLE_ARGS:
            args_dict.pop(possible_arg, None)

        return cls(**args_dict)

    @classmethod
    def add_additional_args(cls, parser: argparse.ArgumentParser):
        """
        Hook for any args related to your model specifically
        """
        pass


class Model:

    # This field is used for controlling additional args
    # that your model needs.
    args_cls = None

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def build(self, args: Args) -> OpenSCADObject:
        """
        The main logic of your model. This should return something that
        can have be converted into scan code
        """
        raise NotImplementedError("This must be overwritten")


def _openscad_command():
    pass


def cmd_print(args, model):
    print(scad_render(model))
    return True


def cmd_write(args, model):
    code = scad_render(model)
    if args.print:
        print(code)
    with args.target_file as f:
        f.write(code)
        f.flush()

    if args.preview:
        subprocess.Popen(
            [
                "openscad",
                args.target_file.name,
            ],
            start_new_session=True,
        )

    return True


def cmd_build(args, model):
    def get_file_and_path():
        if args.scad_file:
            path = os.path.expandvars(os.path.expanduser(args.scad_file))
            return path, open(path, "w")
        else:
            f = tempfile.NamedTemporaryFile(mode="w")
            return f.name, f

    path, f = get_file_and_path()
    with f:
        f.write(scad_render(model))
        f.flush()
        subprocess.run(
            [
                "openscad",
                "-o",
                args.target_file,
                path,
            ],
            check=True,
        )
    return True


def _add_model_args(command_parser, models, multi=False):
    if multi:
        subparsers = command_parser.add_subparsers(
            help="Model", required=True, dest="_model_name"
        )
        for model in models:
            parser = subparsers.add_parser(model.name())
            model.args_cls.add_additional_args(parser)
            parser.set_defaults(model=model)
    elif len(models) == 1:
        model = models[0]
        model.args_cls.add_additional_args(command_parser)
        command_parser.set_defaults(model=model)
    else:
        raise RuntimeError(
            f"Expected one model because multi is false but found {len(models)}"
        )


def _add_commands(parser, models, multi=False):
    subparsers = parser.add_subparsers(help="Command", required=True, dest="cmd_name")

    print_parser = subparsers.add_parser(
        "print", help="Build the model and print the scad code to the screen"
    )
    print_parser.set_defaults(cmd=cmd_print)
    _add_model_args(print_parser, models, multi)

    write_parser = subparsers.add_parser(
        "write",
        help="Build the model and write the scad to a file",
    )
    write_parser.set_defaults(cmd=cmd_write)
    _add_model_args(write_parser, models, multi)
    write_parser.add_argument(
        "--print", action="store_true", help="Print the code in addition to writing it"
    )
    write_parser.add_argument(
        "--preview",
        action="store_true",
        help=(
            "Preview the result in OpenSCAD. This is useful once off but you should run "
            "write regularly and without it and use autorefresh in OpenSCAD for easiest "
            "workflow"
        ),
    )
    write_parser.add_argument(
        "target_file",
        type=argparse.FileType("w", encoding="UTF-8"),
    )

    build_parser = subparsers.add_parser(
        "build",
        help="Build the model and then compile it to an stl file with openscad",
    )
    build_parser.set_defaults(cmd=cmd_build)
    _add_model_args(build_parser, models, multi)
    build_parser.add_argument(
        "--scad-file",
        help="Write scad to this file (useful for seeing intermediate steps)",
    )
    build_parser.add_argument(
        "target_file",
        help="The STL path to output to",
    )


def run_model(parser):
    cli_args = parser.parse_args()
    model = cli_args.model()
    model_args = model.args_cls.from_argparse(cli_args)
    built_model = model.build(model_args)
    return cli_args.cmd(cli_args, built_model)


def main_single(model):
    assert issubclass(model, Model)
    parser = argparse.ArgumentParser(
        description=f"CLI for working with {model.name()} models"
    )
    _add_commands(parser, [model], multi=False)

    return run_model(parser)


def main_multi(models: List[Model]):
    if len(models) == 0:
        raise ValueError("You must provide at least one model for main_multi")
    parser = argparse.ArgumentParser(description="CLI for working with models")
    _add_commands(parser, models, multi=True)

    return run_model(parser)
