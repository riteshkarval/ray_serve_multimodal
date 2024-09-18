
def init_logger(filename="out.log"):
    mm_home = os.getenv('MM_HOME', '.')
    log_level = os.getenv('LOGLEVEL', 'info').lower()
    logFormatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s")
    myLogger = logging.getLogger()
    if log_level == "debug":
        myLogger.setLevel(logging.DEBUG)
    elif log_level in ["warn", "warning"]:
        myLogger.setLevel(logging.WARN)
    elif log_level == "error":
        myLogger.setLevel(logging.ERROR)
    else:
        myLogger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler(os.path.join(mm_home, filename))
    fileHandler.setFormatter(logFormatter)
    myLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    myLogger.addHandler(consoleHandler)
    return myLogger
