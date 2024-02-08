import machine, os, gc
from .. import sdcard

logfile_path = "/sd/logs"

LOG_INFO = 0b00001
LOG_WARNING = 0b00010
LOG_ERROR = 0b00100
LOG_DEBUG = 0b01000
LOG_EXCEPTION = 0b10000
LOG_ALL = LOG_INFO | LOG_WARNING | LOG_ERROR | LOG_DEBUG | LOG_EXCEPTION

_logging_types = LOG_INFO | LOG_WARNING | LOG_ERROR | LOG_EXCEPTION

# the log file will be truncated if it exceeds _log_truncate_at bytes in
# size. the defaults values are designed to limit the log to at most
# three blocks on the Pico
_log_truncate_at = 11 * 1024 * 0  # disabled
_log_truncate_to = 8 * 1024


# Set the Chip Select (CS) pin high
cs = machine.Pin(17, machine.Pin.OUT)

# Intialize the SD Card
spi = machine.SPI(
    0,
    baudrate=1000000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
    sck=machine.Pin(18),
    mosi=machine.Pin(19),
    miso=machine.Pin(16),
)
sd = sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = os.VfsFat(sd)
os.mount(vfs, "/sd")


def exists_dir(path) -> bool:
    try:
        os.listdir(path)
        return True
    except:
        return False


def mkdir(path: str):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.args[0] == 17:
            pass


if not exists_dir(logfile_path):
    mkdir(logfile_path)


def datetime_string():
    dt = machine.RTC().datetime()
    return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)


def date_string():
    return datetime_string().split(" ")[0]


def file_size(file):
    try:
        return os.stat(file)[6]
    except OSError:
        return 0


def set_truncate_thresholds(truncate_at, truncate_to):
    global _log_truncate_at
    global _log_truncate_to
    _log_truncate_at = truncate_at
    _log_truncate_to = truncate_to


def enable_logging_types(types):
    global _logging_types
    _logging_types = _logging_types | types


def disable_logging_types(types):
    global _logging_types
    _logging_types = _logging_types & ~types


# truncates the log file down to a target size while maintaining
# clean line breaks
def truncate(file, target_size):
    # get the current size of the log file
    size = file_size(file)

    # calculate how many bytes we're aiming to discard
    discard = size - target_size
    if discard <= 0:
        return

    with open(file, "rb") as infile:
        with open(file + ".tmp", "wb") as outfile:
            # skip a bunch of the input file until we've discarded
            # at least enough
            while discard > 0:
                chunk = infile.read(1024)
                discard -= len(chunk)

            # try to find a line break nearby to split first chunk on
            break_position = max(
                chunk.find(b"\n", -discard),  # search forward
                chunk.rfind(b"\n", -discard),  # search backwards
            )
            if break_position != -1:  # if we found a line break..
                outfile.write(chunk[break_position + 1 :])

            # now copy the rest of the file
            while True:
                chunk = infile.read(1024)
                if not chunk:
                    break
                outfile.write(chunk)

    # delete the old file and replace with the new
    os.remove(file)
    os.rename(file + ".tmp", file)


def log(level, text):
    datetime = datetime_string()
    log_entry = "{0} [{1:8} /{2:>4}kB] {3}".format(
        datetime, level, round(gc.mem_free() / 1024), text
    )
    print(log_entry)
    log_filename = "{0}/{1}.txt".format(logfile_path, date_string())

    with open(log_filename, "a") as logfile:
        logfile.write(log_entry + "\n")

    if _log_truncate_at and file_size(log_filename) > _log_truncate_at:
        truncate(log_filename, _log_truncate_to)


def info(*items):
    if _logging_types & LOG_INFO:
        log("info", " ".join(map(str, items)))


def warn(*items):
    if _logging_types & LOG_WARNING:
        log("warning", " ".join(map(str, items)))


def error(*items):
    if _logging_types & LOG_ERROR:
        log("error", " ".join(map(str, items)))


def debug(*items):
    if _logging_types & LOG_DEBUG:
        log("debug", " ".join(map(str, items)))


def exception(*items):
    if _logging_types & LOG_EXCEPTION:
        log("exception", " ".join(map(str, items)))
