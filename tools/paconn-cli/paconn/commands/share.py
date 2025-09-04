# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Share command.
"""

import json
import os

from paconn import _SHARE
from paconn.common.util import display
from paconn.settings.util import load_powerapps_and_flow_rp
from paconn.settings.settingsbuilder import SettingsBuilder


def share(
        environment,
        connector_id,
        permissions_file,
        powerapps_url,
        powerapps_version,
        settings_file):
    """
    Share command to modify connector permissions.
    """
    # Get settings
    settings = SettingsBuilder.get_settings(
        environment=environment,
        settings_file=settings_file,
        connector_id=connector_id,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version,
        api_properties=None,
        api_definition=None,
        icon=None,
        script=None)

    powerapps_rp, _ = load_powerapps_and_flow_rp(
        settings=settings,
        command_context=_SHARE)

    # Load and validate the permissions JSON file
    if not os.path.exists(permissions_file):
        raise ValueError(f"Permissions file not found: {permissions_file}")

    try:
        with open(permissions_file, 'r', encoding='utf-8') as f:
            permissions_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in permissions file: {e}")

    # Validate required fields in the permissions data
    required_fields = ['roleName', 'principal']
    for field in required_fields:
        if field not in permissions_data:
            raise ValueError(f"Missing required field in permissions file: {field}")

    # Call the API to modify permissions
    response_text = powerapps_rp.modify_permissions(
        environment=settings.environment,
        connector_id=settings.connector_id,
        permissions_data=permissions_data)

    display(f'Permissions modified successfully for connector {settings.connector_id}.')
    display(f'Response: {response_text}')
