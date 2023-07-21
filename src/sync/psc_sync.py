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


class PSCDataSync:
    """
    Class that contains methods to get catalog member records for PSC data synchronization.

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

        # load environment variables specific for PSC operations
        self.psc_sync_url: str = os.getenv('PSC_SYNC_URL')
        self.psc_auth_header: dict = {'Content-Type': 'application/json', 'Authorization': f'Bearer {os.environ.get("PSC_SYNC_TOKEN")}'}
        self.psc_sync_projects: list = os.environ.get('PSC_SYNC_PROJECTS').split(',')
        self.psc_physical_location: str = 'PSC'

        # get the system we are running on
        self.system = os.getenv('SYSTEM', "Not set")

    def run(self, run_id: str, physical_location: str) -> bool:
        """
        Gets the catalog member records for the run id and sends them to PSC

        :param run_id:
        :param physical_location:
        :return:
        """
        # init the return
        success = True

        # is this coming from PSC
        if physical_location.startswith(self.psc_physical_location):
            try:
                # make the DB request to get the catalogs
                catalog_data: dict = self.db_info.get_catalog_member_records(run_id=run_id, filter_event_type='nowcast')

                # if we got data push it to PSC
                if catalog_data is not None and catalog_data['catalogs'] is not None:
                    # clean up the past run data
                    catalog_data = self.filter_catalog_past_runs(catalog_data)

                    # make sure that all catalogs are have the proper target project code
                    if self.check_project_codes(catalog_data):
                        # make the call to push the data to PSC
                        success = self.push_to_psc(catalog_data, run_id)

                        # did it fail
                        if not success:
                            self.logger.warning('Error: PSC sync failure for run id %s.', run_id)
                    else:
                        self.logger.warning('Warning: One or more catalogs for run id %s were not for PSC.', run_id)
                else:
                    self.logger.warning('Warning: No records found in the database for run id %s.', run_id)

            except Exception:
                self.logger.exception('Failed to get sync data from the database for run id %s.', run_id)

                # set the failure code
                success = False
        else:
            self.logger.debug('%s is not a %s run.', run_id, self.psc_physical_location)

        # return the data to the caller
        return success

    def check_project_codes(self, catalog_data: dict) -> bool:
        """
        checks to make sure all catalog member entries have PSC project codes.

        :param catalog_data:
        :return:
        """
        # init the return value
        success: bool = True

        # loop through the catalog entries
        for catalog in catalog_data['catalogs']:
            # is this a legit PSC entry
            if catalog['project_code'] not in self.psc_sync_projects:
                # set the not found flag
                success = False

                # no need to continue
                break

        # return to the caller
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
            # execute the post
            ret_val = requests.post(self.psc_sync_url, headers=self.psc_auth_header, json=catalog_data, timeout=10)

            # was the call unsuccessful. 201 is returned on success for ths one
            if ret_val.status_code != 200:
                # log the error
                self.logger.error('Error: PSC sync request failure code %s for run id %s.', ret_val.status_code, run_id)

                # set the failure flag
                success = False
        except Exception:
            self.logger.exception('Exception: PSC sync request failure for run id %s.', run_id)

            # set the failure return code
            success = False

        # return the success flag
        return success

    @staticmethod
    def get_unique_catalog_ids(catalog_data: dict) -> list:
        """
        gets the unique catalog IDs

        :param catalog_data:
        :return:
        """
        # get the unique keys in the dict
        ret_val: list = list(set('-'.join(x['member_def']['id'].split('-')[:-1]) for x in catalog_data['catalogs']))

        # return to the caller
        return ret_val

    def filter_catalog_past_runs(self, catalog_data: dict) -> dict:
        """
        filters out the non-PSC past run data

        :param catalog_data:
        :return:
        """
        # make sure we have something to filter
        if catalog_data['past_runs'] is not None:
            # filter out non-PSC data from the past_runs
            catalog_data['past_runs'] = list(filter(lambda item: (item['project_code'] in self.psc_sync_projects), catalog_data['past_runs']))

        # add in the system this is coming from
        catalog_data['system'] = self.system

        # return to the caller
        return catalog_data
