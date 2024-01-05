# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Class for database functionalities

    Author: Phil Owen, RENCI.org
"""

from src.common.pg_utils_multi import PGUtilsMultiConnect
from src.common.logger import LoggingUtil


class PGImplementation(PGUtilsMultiConnect):
    """
        Class that contains DB calls for the PSC data sync.

        Note this class inherits from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, _logger=None, _auto_commit=True):
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSViz.Collab_sync.PGImplementation", level=log_level, line_format='medium',
                                                   log_file_path=log_path)

        # init the base class
        PGUtilsMultiConnect.__init__(self, 'APSViz.Collab_sync.PGImplementation', db_names, _logger=self.logger, _auto_commit=_auto_commit)

    def __del__(self):
        """
        Calls super base class to clean up DB connections and cursors.

        :return:
        """
        # clean up connections and cursors
        PGUtilsMultiConnect.__del__(self)

    def get_catalog_member_records(self, run_id: str = None, project_code: str = None, filter_event_type: str = None, limit: int = None) -> dict:
        """
        gets the apsviz catalog member record for the run id passed. the SP default
        record count returned can be overridden.

        :param run_id:
        :param project_code:
        :param filter_event_type:
        :param limit:
        :return:
        """

        # init the return
        ret_val: dict = {}

        # did we get a run id
        if run_id is not None:
            run_id = f"_run_id := '{run_id}%'"
        else:
            run_id = '_run_id := NULL'

        # did we get a project code
        if project_code is not None:
            project_code = f", _project_code := '{project_code}'"
        else:
            project_code = ', _project_code := NULL'

        # did we get a filter event type
        if filter_event_type is not None:
            filter_event_type = f", _filter_event_type := '{filter_event_type}'"
        else:
            filter_event_type = ', _filter_event_type := NULL'

        # did we get a limit
        if limit is not None:
            limit = f', _limit := {limit}'
        else:
            limit = ', _limit := NULL'

        # create the sql. note we are appending a '%' wildcard to get all products for this run
        sql: str = f"SELECT public.get_catalog_member_records({run_id}{project_code}{filter_event_type}{limit});"

        # get the layer list
        ret_val = self.exec_sql('apsviz', sql)

        # return the data
        return ret_val
