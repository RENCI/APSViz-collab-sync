# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test DB operations

    Author: Phil Owen, 5/1/2023
"""
import pytest
from src.common.pg_impl import PGImplementation
from src.sync.psc_sync import PSCDataSync


@pytest.mark.skip(reason="Local test only")
def test_db_connection_creation():
    """
    Tests the creation and usage of the db utils DB multi-connect class

    :return:
    """
    # specify the DBs to gain connectivity to
    db_names: tuple = ('apsviz',)

    # create a DB connection object
    db_info = PGImplementation(db_names)

    # check the object returned
    assert len(db_info.dbs) == len(db_names)

    # for each db specified
    for db_name in db_names:
        # make a db request
        ret_val = db_info.exec_sql(db_name, 'SELECT version()')

        # check the data returned
        assert ret_val.startswith('PostgreSQL')


@pytest.mark.skip(reason="Local test only")
def test_get_catalogs():
    """
    method to test getting catalog data given a run id

    :return:
    """
    # get the PSC sync object
    psc_sync = PSCDataSync()

    catalog_data: dict = {}

    # get the catalog data. no run id and no limits is an error
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(None, None, 0)

    # check the result, expect the error
    assert len(catalog_data) == 1 and 'Error' in catalog_data

    # get the catalog data. no run id and no limits is an error
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(None, None, None)

    # check the result, expect the error
    assert len(catalog_data) == 1 and 'Error' in catalog_data

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records('4358-2023050106-namforecast')

    # check the record counts
    assert len(catalog_data['catalogs']) > 1
    assert len(catalog_data['past_runs']) > 1

    # set a limit
    limit = 5

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(None, None, limit)

    # get the unique catalog ids
    catalog_ids = psc_sync.get_unique_catalog_ids(catalog_data)

    # check the record count
    assert len(catalog_ids) == limit

    # get the current count of past runs
    count = len(catalog_data['past_runs'])

    # remove all non-PSC past run data
    catalog_data = psc_sync.filter_catalog_past_runs(catalog_data)

    # there should be a difference
    assert count > len(catalog_data['past_runs'])

    # set a limit
    limit = 3

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(None, 'nopp', limit)

    # check the record count
    assert len(catalog_data) > 1

    # get the unique catalog ids
    catalog_ids = psc_sync.get_unique_catalog_ids(catalog_data)

    # check the record count
    assert len(catalog_ids) == limit

    # get the catalog data. An invalid project returns no records
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(None, 'fail', limit)

    # check the record count
    assert catalog_data['catalogs'] is None
    assert catalog_data['past_runs'] is None


@pytest.mark.skip(reason="Local test only")
def test_push_to_psc():
    """
    method to test the push of information to a PSC web service

    :return:
    """
    # get the PSC sync object
    psc_sync = PSCDataSync()

    # set the expected number of records returned
    limit = 5

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(limit=limit)

    # get the unique keys in the dict
    catalogs: list = list(set('-'.join(x['member_def']['id'].split('-')[:-1]) for x in catalog_data))

    # check the record count
    assert len(catalogs) == limit

    # push the data to PSC
    success: bool = psc_sync.push_to_psc(catalog_data=catalog_data)

    # check to see if it went in
    assert success


@pytest.mark.skip(reason="Local test only")
def test_run():
    """
    method to test a run of retrieving catalog data from the DB and pushing it to PSC.

    :return:
    """
    # get the PSC sync object
    psc_sync = PSCDataSync()

    # get the catalog data and send it to PSC
    success: bool = psc_sync.run('4358-2023050106-namforecast', 'PSC')  # 4358-2023050106-namforecast 4255-05-obs

    # check the return code
    assert success

    # get the catalog data and send it to PSC
    success: bool = psc_sync.run('4255-05-obs', 'PSC')  # 4358-2023050106-namforecast 4255-05-obs

    # check the return code
    assert not success
