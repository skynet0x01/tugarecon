#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.

# import go here
# ----------------------------------------------------------------------------------------------------------
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
            /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  Version 2.4
                      /____/                               # Coded By skynet0x01 #
    """ + W)
    print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country. 2020-2025\n" + W)

