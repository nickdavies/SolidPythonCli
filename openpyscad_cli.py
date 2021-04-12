import argparse
import os
import subprocess
import tempfile
from typing import List


class Model:
    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @classmethod
    def add_additional_args(cls, parser: argparse.ArgumentParser):
        """
        Hook for any args related to your model specifically
        """
        pass

    def build(self, args):
        """
        The main logic of your model. This should return something that
        can have .dump or be part of a union etc.
        """
        raise NotImplementedError("This must be overwritten")


def _openscad_command():
    pass


def cmd_print(args, model):
    print(model.dumps())
    return True


def cmd_write(args, model):
    if args.print:
        print(model.dumps())
    model.dump(args.target_file)

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
        model.dump(f)
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
            model.add_additional_args(parser)
            parser.set_defaults(model=model)
    elif len(models) == 1:
        model = models[0]
        model.add_additional_args(command_parser)
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


def main_single(model):
    assert issubclass(model, Model)
    parser = argparse.ArgumentParser(
        description=f"CLI for working with {model.name()} models"
    )
    _add_commands(parser, [model], multi=False)

    args = parser.parse_args()
    return args.cmd(args, args.model().build(args))


def main_multi(models: List[Model]):
    if len(models) == 0:
        raise ValueError("You must provide at least one model for main_multi")
    parser = argparse.ArgumentParser(description="CLI for working with models")
    _add_commands(parser, models, multi=True)

    args = parser.parse_args()
    return args.cmd(args, args.model().build(args))
