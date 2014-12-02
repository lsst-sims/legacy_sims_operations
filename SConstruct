# -*- python -*-
# OPSIM top-level SConstruct
import os
import fileutils
import SCons.Node.FS
import state

srcDir = Dir('.').srcnode().abspath
state.init(srcDir)
env = state.env

#########################
#
# Defining dependencies
#
#########################

# by default run build+test
all = env.Alias("all", [env.Alias("build"), env.Alias("test")])
env.Default(all)

env.Depends("build", env.Alias("init-build-env"))
env.Depends("install", env.Alias("build"))

env.Alias("install",
          [env.Alias("admin"),
           env.Alias("opsim"),
           env.Alias("templates")])

################################
#
# Build documentation
#
################################
doc = env.Command("build-doc", [],
                  "cd doc && PATH={0} make html".format(os.getenv("PATH")))
env.Alias("doc", doc)

# documentation generation must be possible even if build
# environment isn't available
if ['doc'] == COMMAND_LINE_TARGETS:
    state.log.debug("Only building OPSIM documentation")
else:
################################
#
# Init build environment
#
################################
    state.initBuild()
    env.Replace(configuration_prefix = os.path.join( env['prefix'], "cfg"))

#########################
#
# Install admin commands
#
#########################
    adminbin_target = os.path.join(env['prefix'], "bin")
    env.RecursiveInstall(adminbin_target, os.path.join("admin", "bin"))
    python_admin = env.InstallPythonModule(target=env['python_prefix'],
                                           source=os.path.join("admin", "python"))

    template_target = os.path.join(env['configuration_prefix'], "templates")
    env.RecursiveInstall(template_target, os.path.join("admin", "templates", "configuration"))

    env.Alias("admin",
              [python_admin,
               template_target,
               adminbin_target])

#############################
#
# Install OPSIM code
#
#############################

    def rec_install(direc):
        target = os.path.join(env['prefix'], direc)
        env.RecursiveInstall(target, direc)
        return target

    bin_target = rec_install("bin")
    conf_target = rec_install("conf")
    data_target = rec_install("DataForInstall")
    doc_target = rec_install("doc")
    log_target = rec_install("log")
    tests_target = rec_install("tests")
    tools_target = rec_install("tools")

    opsimpy_target = env.InstallPythonModule(target=os.path.join(env['prefix'], "python"),
                                             source="python")

    env.Alias("opsim",
              [bin_target,
               conf_target,
               data_target,
               doc_target,
               log_target,
               opsimpy_target,
               tests_target,
               tools_target])

#########################################
#
# Templates :
# - fill user configuration file
# - alias for OPSIM start/stop commands
#
#########################################

    def get_template_targets():

        template_dir_path = os.path.join("admin", "templates", "installation")
        target_lst = []

        state.log.info("Applying configuration information " +
                        "via templates files located in " +
                        "{0}".format(template_dir_path)
        )

        script_dict = {'{{OPSIM_DIR}}': os.path.abspath(env['prefix']),
                       '{{MYSQL_DIR}}': env['MYSQL_DIR'],
                       }

        for src_node in fileutils.recursive_glob(template_dir_path, "*", env):

            target_node = fileutils.replace_base_path(template_dir_path, env['configuration_prefix'], src_node, env)

            if isinstance(src_node, SCons.Node.FS.File):

                state.log.debug("Template SOURCE : %s, TARGET : %s" % (src_node, target_node))
                env.Substfile(target_node, src_node, SUBST_DICT=script_dict)
                target_lst.append(target_node)

        return target_lst

    env.Alias("templates", get_template_targets())

# List all aliases
try:
    from SCons.Node.Alias import default_ans
except ImportError:
    pass
else:
    aliases = default_ans.keys()
    aliases.sort()
    env.Help('\n')
    env.Help('Recognized targets:\n')
    for alias in aliases:
        env.Help('  %s\n' % alias)
