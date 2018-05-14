"""
Description:
YamlDotNet wrapper module for pyRevit.

Documentation:
https://github.com/aaubry/YamlDotNet/wiki
"""

import importlib

from pyrevit import EXEC_PARAMS
from pyrevit.framework import clr
from pyrevit.framework import IO
from pyrevit.coreutils.logger import get_logger
from pyrevit.loader import addin


logger = get_logger(__name__)


YAML_LIB = 'YamlDotNet'

if not EXEC_PARAMS.doc_mode:
    libyaml_dll = addin.get_addin_dll_file(YAML_LIB)
    logger.debug('Loading dll: {}'.format(libyaml_dll))

    try:
        clr.AddReferenceToFileAndPath(libyaml_dll)
        # public libyaml module
        libyaml = importlib.import_module(YAML_LIB)
    except Exception as load_err:
        logger.error('Can not load {} module. | {}'.format(YAML_LIB, load_err))


def load(yaml_file):
    with open(yaml_file, 'r') as yamlfile:
        yamlstr = libyaml.RepresentationModel.YamlStream()
        yamlstr.Load(IO.StringReader(yamlfile.read()))
        if yamlstr.Documents.Count >= 1:
            return yamlstr.Documents[0].RootNode