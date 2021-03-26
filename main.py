import sanelib
from lib.mdh import example as mdh_example
from util import timer

# Starting time
timer.start()

# Run library
mdh = sanelib.mdh
mdh_example.run(mdh)

# End time
timer.end()


