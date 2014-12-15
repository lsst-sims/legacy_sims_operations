import SCons.Script

log = None

def init():
    import utils
    global log
    log = utils.Log()
    log.verbose = SCons.Script.GetOption("verbose")
    log.traceback = SCons.Script.GetOption("traceback")
