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
dir(env)
srcDir = Dir('.').srcnode().abspath
print "A:", env['prefix']
print "B:", srcDir

# Makes sure env.Substfile is available
env.Tool('textfile')
env.Tool('recinstall')

# Add the setup configuration files to the install target.
env.Alias("install-cfg", [env.Alias("configuration"), env.Alias("templates")])
env.Depends("install", env.Alias("install-cfg"))

finder = binfind.Find()

opts = SCons.Script.Variables("custom.py")
opts.AddVariables((SCons.Variables.PathVariable('MYSQL_DIR', 
                                    'mysql install dir',
                                    finder.prefixFromBin('MYSQL_DIR',
                                                         "mysqld_safe"),
                                    SCons.Variables.PathVariable.PathIsDir)),)
opts.Update(env)
# This override causes issues with EUPS distribution, so don't do it then.
if "EupsBuildDir" and "build" not in srcDir:
    opts.AddVariables((PathVariable('prefix', 'opsim install dir', srcDir,
                                    SCons.Variables.PathVariable.PathIsDirCreate)))

    opts.Update(env)

env.Replace(configuration_prefix=os.path.join(env['prefix'], "cfg"))

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

    script_dict = {'{{OPSIM_DIR}}': os.path.abspath(env['prefix']),
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
