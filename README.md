<!--
SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-License-Identifier: LicenseRef-RENCI
SPDX-License-Identifier: MIT
-->

![image not found](renci-logo.png "RENCI")

# APSViz-Collab-sync
Synchronizes data created by the various APSViz services and applications and processes with collaborators.

#### Licenses...
[![MIT License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/RENCI/APSVIZ-Supervisor/tree/master/LICENSE)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![RENCI License](https://img.shields.io/badge/License-RENCI-blue.svg)](https://www.renci.org/)
#### Components and versions...
[![Python](https://img.shields.io/badge/Python-3.12.3-orange)](https://github.com/python/cpython)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%203.1.0-yellow)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%208.2.0-blue)](https://github.com/pytest-dev/pytest)
#### Build status...
[![Pylint and Pytest](https://github.com/RENCI/APSViz-collab-sync/actions/workflows/pylint-pytest.yml/badge.svg)](https://github.com/RENCI/APSViz-collab-sync/actions/workflows/pylint-pytest.yml)
[![Build and push the Docker image](https://github.com/RENCI/APSViz-collab-sync/actions/workflows/image-push.yml/badge.svg)](https://github.com/RENCI/APSViz-collab-sync/actions/workflows/image-push.yml)

## Description
This [APSViz-Supervisor](https://github.com/RENCI/APSVIZ-Supervisor) component is designed to synchronize APSViz data with collaborators.

There are GitHub actions to maintain code quality in this repo:
 - Pylint (minimum score of 10/10 to pass),
 - Pytest (with code coverage),
 - Build/publish a Docker image.
