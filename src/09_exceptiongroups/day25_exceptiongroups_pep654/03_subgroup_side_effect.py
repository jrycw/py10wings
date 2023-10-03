# 03
def log_and_ignore_ENOENT(err):
    if isinstance(err, OSError) and err.errno == ENOENT:
        log(err)
        return False
    else:
        return True

try:
    . . .
except ExceptionGroup as eg:
    eg = eg.subgroup(log_and_ignore_ENOENT)
    if eg is not None:
        raise eg