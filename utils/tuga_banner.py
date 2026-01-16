# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Import internal functions
from utils.tuga_colors import Y, R, W

# ----------------------------------------------------------------------------------------------------------
# Banner: Tuga or Portuguese — same spirit ;)
def banner():
    print(R + r"""
              ______                  ____
             /_  __/_  ______ _____ _/ __ \___  _________  ____
              / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \
             / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /
            /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  Version 2.52
                      /____/                               # Coded By skynet0x01 #
    """ + W)
    print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country. 2020-2026\n" + W)

