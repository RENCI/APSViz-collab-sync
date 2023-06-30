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
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(limit=0)

    # check the result, expect the error
    assert catalog_data != -1 and len(catalog_data) == 1 and 'Error' in catalog_data

    # get the catalog data. no run id and no limits is an error
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records()

    # check the result, expect the error
    assert catalog_data != -1 and len(catalog_data) == 1 and 'Error' in catalog_data

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(run_id='4358-2023050106-namforecast')

    # check the record counts
    assert catalog_data != -1 and 'catalogs' in catalog_data and 'past_runs' in catalog_data
    assert len(catalog_data['catalogs']) >= 1 and len(catalog_data['past_runs']) >= 1

    # get the catalog data, this time use a nowcast run filtering out the nowcast data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(run_id='4409-008-nowcast', filter_event_type='nowcast')

    # check the record counts
    assert catalog_data != -1 and catalog_data['catalogs'] is None
    assert len(catalog_data['past_runs']) >= 1

    # set a limit
    limit = 5

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(limit=limit)

    # check the record counts
    assert catalog_data != -1 and 'catalogs' in catalog_data and 'past_runs' in catalog_data
    assert len(catalog_data['catalogs']) >= 1 and len(catalog_data['past_runs']) >= 1

    # get the unique catalog ids
    catalog_ids = psc_sync.get_unique_catalog_ids(catalog_data)

    # check the record counts
    assert catalog_data != -1 and 'catalogs' in catalog_data and 'past_runs' in catalog_data
    assert len(catalog_data['catalogs']) >= 1 and len(catalog_data['past_runs']) >= 1

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
    catalog_data_pt1: dict = psc_sync.db_info.get_catalog_member_records(project_code='lffs', limit=limit)

    # check the record counts
    assert catalog_data_pt1 != -1 and 'catalogs' in catalog_data_pt1 and 'past_runs' in catalog_data_pt1
    assert len(catalog_data_pt1['catalogs']) >= 1 and len(catalog_data_pt1['past_runs']) >= 1

    # get the catalog data
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(project_code='lffs', filter_event_type='nowcast', limit=limit)

    # check the record counts
    assert catalog_data != -1 and 'catalogs' in catalog_data and 'past_runs' in catalog_data
    assert len(catalog_data['catalogs']) >= 1 and len(catalog_data['past_runs']) >= 1

    # we should have a different count because we filtered out the nowcasts
    assert len(catalog_data_pt1['catalogs']) > len(catalog_data['catalogs'])

    # get the unique catalog ids
    catalog_ids = psc_sync.get_unique_catalog_ids(catalog_data)

    # check the record count
    assert len(catalog_ids) == limit

    # get the catalog data. A non-existent project returns no records
    catalog_data: dict = psc_sync.db_info.get_catalog_member_records(project_code='no-recs-ret', limit=limit)

    # check the record count
    assert catalog_data != -1 and catalog_data['catalogs'] is None and catalog_data['past_runs'] is None


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

    # init the catalog data
    catalog_data: dict = {}

    # init some PSC runs
    psc_runs = ['4409-003-ofcl-maxwvel63', '4409-006-ofcl-maxwvel63', '4409-006-ofcl-swan', '4409-006-ofcl-maxele63', '4409-003-ofcl-swan',
                '4409-003-ofcl-obs', '4409-006-ofcl-obs', '4409-007-nowcast-swan', '4409-007-nowcast-maxwvel63', '4409-007-nowcast-maxele63',
                '4409-007-nowcast-obs', '4409-008-nowcast-swan', '4409-008-nowcast-maxele63', '4409-008-nowcast-maxwvel63', '4409-008-nowcast-obs',
                '4409-007-ofcl-swan', '4409-007-ofcl-maxwvel63', '4409-007-ofcl-maxele63', '4409-007-ofcl-obs', '4409-008-ofcl-swan',
                '4409-008-ofcl-maxele63', '4409-008-ofcl-maxwvel63', '4409-008-ofcl-obs', '4409-009-nowcast-swan', '4409-009-nowcast-maxele63',
                '4409-009-nowcast-maxwvel63', '4409-009-nowcast-obs', '4409-010-nowcast-swan', '4409-010-nowcast-maxele63',
                '4409-010-nowcast-maxwvel63', '4409-010-nowcast-obs', '4409-009-ofcl-maxele63', '4409-009-ofcl-swan', '4409-009-ofcl-maxwvel63',
                '4409-009-ofcl-obs', '4409-010-ofcl-maxele63', '4409-010-ofcl-maxwvel63', '4409-010-ofcl-swan', '4409-010-ofcl-obs',
                '4409-011-nowcast-swan', '4409-011-nowcast-maxele63', '4409-011-nowcast-maxwvel63', '4409-011-nowcast-obs', '4409-011-ofcl-maxele63',
                '4409-011-ofcl-swan', '4409-011-ofcl-maxwvel63', '4409-011-ofcl-obs', '4409-012-nowcast-swan', '4409-012-nowcast-maxele63',
                '4409-012-nowcast-maxwvel63', '4409-012-nowcast-obs', '4409-012-ofcl-maxele63', '4409-012-ofcl-maxwvel63', '4409-012-ofcl-swan',
                '4409-012-ofcl-obs', '4409-003-ofcl-maxele63', '4409-005-nowcast-swan', '4409-005-nowcast-maxele63', '4409-005-nowcast-maxwvel63',
                '4409-005-nowcast-obs', '4409-005-ofcl-maxele63', '4409-005-ofcl-swan', '4409-005-ofcl-maxwvel63', '4409-005-ofcl-obs',
                '4409-006-nowcast-maxele63', '4409-006-nowcast-swan', '4409-006-nowcast-maxwvel63', '4409-006-nowcast-obs', '4409-004-ofcl-maxele63',
                '4409-004-ofcl-swan', '4409-004-ofcl-maxwvel63', '4409-004-ofcl-obs']

    for item in psc_runs:
        catalog_data: dict = psc_sync.db_info.get_catalog_member_records(run_id=item, limit=limit)

        # check the record count
        assert 'catalogs' in catalog_data and len(catalog_data['catalogs']) >= 1

        # push the data to PSC
        assert psc_sync.push_to_psc(catalog_data=catalog_data)

    # get the unique keys in the dict
    catalogs: list = list(set('-'.join(x['member_def']['id'].split('-')[:-1]) for x in catalog_data))

    # check the record count
    assert len(catalogs) == limit

    # check to see if it went in
    assert psc_sync.push_to_psc(catalog_data=catalog_data)


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
