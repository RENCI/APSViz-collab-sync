# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Main entry point for the PSC synchronizer.

    Author: Phil Owen, 05/10/2023
"""

import os
import requests


from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation


class PSCSync:
    """
    Class that contains methods to get catalog member records for PSC.

    """
    def __init__(self, _logger=None):
        """
        Initializes this class

        """
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSVIZ.PSCSync", level=log_level, line_format='medium', log_file_path=log_path)

        # specify the DBs to gain connectivity to
        db_names: tuple = ('apsviz',)

        # create a DB connection object
        self.db_info = PGImplementation(db_names, self.logger)

        # load environment variables
        self.psc_sync_url = os.getenv('PSC_SYNC_URL')
        self.psc_sync_token = os.environ.get('PSC_SYNC_TOKEN')

    def run(self, run_id: str) -> bool:
        """
        Gets the catalog member records for the run id and sends them to PSC

        :param run_id:
        :return:
        """
        # init the return
        success = True

        try:
            # make the DB request to get the catalogs
            catalog_data: dict = self.db_info.get_catalog_member_records(run_id)

            # if we got data push it to PSC
            if catalog_data is not None:
                # make the call to push the data to PSC
                success = self.push_to_psc(catalog_data, run_id)

                # did it fail
                if not success:
                    self.logger.warning('Error: PSC sync failure for run id %s.', run_id)
            else:
                self.logger.warning('Warning: No records found in the database for run id %s.', run_id)

        except Exception:
            self.logger.exception('Failed to get sync data from data base for run id %s.', run_id)

            # set the failure code
            success = False

        # return the data to the caller
        return success

    def push_to_psc(self, catalog_data: dict, run_id: str = 'N/A') -> bool:
        """
        Pushes data to the PSC web service endpoint

        :param run_id
        :param catalog_data:
        :return:
        """
        # init the return code
        success = True

        try:
            # build the URL to the service
            url = f'{self.psc_sync_url}'

            # execute the post
            ret_val = requests.post(url, auth=self.psc_sync_token, json=catalog_data, timeout=10)

            # was the call unsuccessful. 201 is returned on success for ths one
            if ret_val.status_code != 200:
                # log the error
                self.logger.error('Error: PSC sync failure code %s for run id %s.', ret_val.status_code, run_id)

                # set the failure flag
                success = False
        except Exception:
            self.logger.exception('Exception: PSC sync failure for run id %s.', run_id)

            # set the failure return code
            success = False

        # return the success flag
        return success
