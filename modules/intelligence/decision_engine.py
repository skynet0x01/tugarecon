#!/usr/bin/env python3

# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2026.
#
# Copyright (C) 2026 skynet0x01
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


# ----------------------------------------------------------------------------------------------------------

def decide_action(subdomain, impact, temporal_state, temporal_score):
    """
    Decide ação operacional com base no estado temporal e impacto
    """

    if temporal_state == "ESCALATED":
        return "PRIORITY_RESCAN"

    if temporal_state == "NEW":
        if impact >= 20:
            return "DEEP_SCAN"
        return "WATCH"

    if temporal_state == "FLAPPING":
        return "WATCH"

    if temporal_state == "STABLE":
        if impact >= 50:
            return "WATCH"
        return "IGNORE"

    if temporal_state == "DORMANT":
        return "IGNORE"

    return "IGNORE"
