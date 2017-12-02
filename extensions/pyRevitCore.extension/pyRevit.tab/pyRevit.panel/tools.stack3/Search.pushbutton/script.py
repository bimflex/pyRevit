import os
import os.path as op

from pyrevit import HOST_APP
from pyrevit import coreutils
from pyrevit.loader import sessionmgr
from pyrevit import forms
from pyrevit import script
import pyrevit.extensions as exts


__context__ = 'zerodoc'


logger = script.get_logger()


HELP_SWITCH = '/help'
DOC_SWITCH = '/doc'
INFO_SWITCH = '/info'
CLEAN_SWITCH = '/clean'
FULLFRAME_SWITCH = '/full'
OPEN_SWITCH = '/open'
SHOW_SWITCH = '/show'
ATOM_SWITCH = '/atom'
NPP_SWITCH = '/npp'
NP_SWITCH = '/np'
ALT_FLAG = '/alt'


def print_help():
    print('Switches:')


def show_command_info(pyrvtcmd):
    print('Script Source: {}\n\n'
          'Alternate Script Source: {}\n\n'
          'Sys Paths: {}\n\n'
          'Help Source: {}\n\n'
          'Name: {}\n\n'
          'Bundle Name: {}\n\n'
          'Extension Name: {}\n\n'
          'Unique Id: {}\n\n'
          'Needs Clean Engine: {}\n\n'
          'Needs Fullframe Engine: {}\n\n'
          'Class Name: {}\n\n'
          'Availability Class Name: {}\n\n'
          .format(pyrvtcmd.script,
                  pyrvtcmd.alternate_script,
                  pyrvtcmd.syspaths.split(';'),
                  pyrvtcmd.helpsource,
                  pyrvtcmd.name,
                  pyrvtcmd.bundle,
                  pyrvtcmd.extension,
                  pyrvtcmd.unique_id,
                  pyrvtcmd.needs_clean_engine,
                  pyrvtcmd.needs_fullframe_engine,
                  pyrvtcmd.typename,
                  pyrvtcmd.extcmd_availtype
                  )
          )


def show_command_docstring(pyrvtcmd):
    script_content = coreutils.ScriptFileParser(selected_cmd.script)
    doc_string = script_content.get_docstring()
    custom_docstring = script_content.extract_param(exts.DOCSTRING_PARAM)
    if custom_docstring:
        doc_string = custom_docstring

    print(doc_string)


def open_command_helpurl(pyrvtcmd):
    script_content = coreutils.ScriptFileParser(selected_cmd.script)
    helpurl = script_content.extract_param(exts.COMMAND_HELP_URL)
    if helpurl:
        script.open_url(helpurl)
        return True

    return False


def print_source(selected_cmd, altsrc=False):
    output = script.get_output()
    source = \
        selected_cmd.script if not altsrc else selected_cmd.alternate_script
    if source:
        with open(source, 'r') as s:
            output.print_code(s.read())


def open_in_editor(editor_name, selected_cmd, altsrc=False):
    source = \
        selected_cmd.script if not altsrc else selected_cmd.alternate_script
    if source:
        os.popen('{} "{}"'.format(editor_name, source))


# get all default postable commands
postable_cmds = {x.name:x for x in HOST_APP.get_postable_commands()}

# find all available commands (for current selection)
# in currently active document
pyrevit_cmds = {}
for cmd in sessionmgr.find_all_available_commands():
    if cmd.name:
        pyrevit_cmds[cmd.name] = cmd


# build the search database
search_db = []
search_db.extend(pyrevit_cmds.keys())
search_db.extend(postable_cmds.keys())

# search
matched_cmdname, switches = \
    forms.SearchPrompt.show(search_db,
                            switches=[HELP_SWITCH,
                                      DOC_SWITCH,
                                      INFO_SWITCH,
                                      CLEAN_SWITCH,
                                      FULLFRAME_SWITCH,
                                      OPEN_SWITCH,
                                      SHOW_SWITCH,
                                      ATOM_SWITCH,
                                      NPP_SWITCH,
                                      NP_SWITCH,
                                      ALT_FLAG],
                            search_tip='pyRevit Search')

# if asking for help show help and exit
if switches[HELP_SWITCH] and not matched_cmdname:
    print_help()
    script.exit()


if matched_cmdname:
    # if postable command
    if matched_cmdname in postable_cmds.keys():
        if any(switches.values()):
            forms.alert('This is a native Revit command.')
        else:
            __revit__.PostCommand(postable_cmds[matched_cmdname].rvtobj)
    # if pyrevit command
    else:
        selected_cmd = pyrevit_cmds[matched_cmdname]
        if switches[INFO_SWITCH]:
            show_command_info(selected_cmd)
        elif switches[HELP_SWITCH]:
            if not open_command_helpurl(selected_cmd):
                show_command_docstring(selected_cmd)
        elif switches[DOC_SWITCH]:
            show_command_docstring(selected_cmd)
        elif switches[OPEN_SWITCH]:
            coreutils.open_folder_in_explorer(op.dirname(selected_cmd.script))
        elif switches[SHOW_SWITCH]:
            print_source(selected_cmd, altsrc=switches[ALT_FLAG])
        elif switches[ATOM_SWITCH]:
            open_in_editor('atom', selected_cmd,
                           altsrc=switches[ALT_FLAG])
        elif switches[NPP_SWITCH]:
            open_in_editor('notepad++', selected_cmd,
                           altsrc=switches[ALT_FLAG])
        elif switches[NP_SWITCH]:
            open_in_editor('notepad', selected_cmd,
                           altsrc=switches[ALT_FLAG])
        else:
            clean_engine = switches[CLEAN_SWITCH]
            fullframe_engine = switches[FULLFRAME_SWITCH]
            sessionmgr.execute_command_cls(selected_cmd.extcmd_type,
                                           clean_engine=clean_engine,
                                           fullframe_engine=fullframe_engine)