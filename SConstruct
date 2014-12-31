# -*- python -*-
# OPSIM top-level SConstruct
import os

import SCons.Node.FS
import SCons.Script
import SCons.Variables

import binfind
import fileutils
import pstate
from lsst.sconsUtils import scripts

pstate.init()

env = scripts.BasicSConstruct("sims_operations")

# Makes sure env.Substfile is available
env.Tool('textfile')
env.Tool('recinstall')

# Add the setup configuration files to all target.
all = env.Alias("all", [env.Alias("configuration"), env.Alias("templates")])
env.Default(all)

finder = binfind.Find()

opts = SCons.Script.Variables("custom.py")
opts.AddVariables((SCons.Variables.PathVariable('MYSQL_DIR', 
                                    'mysql install dir',
                                    finder.prefixFromBin('MYSQL_DIR',
                                                         "mysqld_safe"),
                                    SCons.Variables.PathVariable.PathIsDir)),)
opts.Update(env)

abs_prefix = os.path.abspath(env['prefix'])

env.Replace(configuration_prefix=os.path.join(abs_prefix, "cfg"))

template_target = os.path.join(env['configuration_prefix'], "templates")
env.RecursiveInstall(template_target, os.path.join("templates", 
                                                   "configuration"))

env.Alias("configuration", [template_target])

def get_template_targets():
    template_dir_path = os.path.join("templates", "installation")
    target_lst = []

    pstate.log.info("Applying configuration information " +
                    "via templates files located in " +
                    "{0}".format(template_dir_path)
    )

    script_dict = {'{{OPSIM_DIR}}': abs_prefix,
                   '{{MYSQL_DIR}}': env['MYSQL_DIR'],
                   }

    for src_node in fileutils.recursive_glob(template_dir_path, "*", env):
        target_node = fileutils.replace_base_path(template_dir_path, 
                                                  env['configuration_prefix'],
                                                  src_node, env)

        if isinstance(src_node, SCons.Node.FS.File):
            pstate.log.debug("Template SOURCE : %s, TARGET : %s" % (src_node, 
                                                                    target_node))
            env.Substfile(target_node, src_node, SUBST_DICT=script_dict)
            target_lst.append(target_node)

    return target_lst

env.Alias("templates", get_template_targets())
