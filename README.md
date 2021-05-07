# SolidPythonCli
Quick CLI wrapper for building dev tools to use with openpyscad with the goal of making it easier to build/models

## Usage

For now I don't have this hosted anywhere but I setup mine something like:

```
git clone git@github.com:nickdavies/SolidPythonCli.git solid_cli
git clone git@github.com:nickdavies/3dprinting-models.git models

virtualenv venv
cd solid_cli
../venv/bin/pip install -e . # or drop the -e if you don't intend to edit solid_cli itself
```

Then a basic usage looks like:

```
import argparse
from dataclasses import dataclass

import solid
import solid.utils
from solid_cli import Args, Model, main_single


@dataclass
class SingleCubeArgs(Args):
    # How large should the cube be
    cube_size: int
    
    @classmethod
    def add_additional_args(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--cube-size",
            type=int,
            default=3,
            help="How large should the cube be",
        )
        
class SingleCube(Model):
    """
    An example model which makes a single cube
    """

    args_cls = SingleCubeArgs
    
    def build(self, args):    
        return solid.cube([args.cube_size, args.cube_size, args.cube_size])
        
if __name__ == "__main__":
    main_single(DeskMountHoles)       
```
