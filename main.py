# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Main entry point for the APSViz collaborator synchronizer.

    Author: Phil Owen, 05/10/2023
"""
import sys
import argparse

from src.sync.psc_sync import PSCDataSync


def run_psc_collab_sync(run_id: str) -> bool:
    """
    Runs thd PSC collaborator sync

    :param run_id
    :return:
    """

    # create the PSC data sync component
    psc_sync = PSCDataSync()

    # initiate the PSC sync. return value of True indicates success
    retval: bool = psc_sync.run(run_id)

    # return to the caller. invert the return for a proper sys exit code
    return retval


if __name__ == '__main__':
    #
    # main entry point for the sync run.
    #

    # create a command line parser
    parser = argparse.ArgumentParser(description='help', formatter_class=argparse.RawDescriptionHelpFormatter)

    # assign the expected input args
    parser.add_argument('-r', '--run_id', help='Input is a valid APSViz supervisor run ID.')

    # parse the command line
    args = parser.parse_args()

    # execute the rule file(s)
    ret_val: bool = run_psc_collab_sync(args.run_id)

    # exit with pass/fail
    sys.exit(0)
