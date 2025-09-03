# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
List command.
"""

import json

from paconn import _LIST

from paconn.common.util import display
from paconn.settings.util import load_powerapps_and_flow_rp
from paconn.settings.settingsbuilder import SettingsBuilder

# Constants for response parsing
_PROPERTIES = 'properties'
_IS_CUSTOM_API = 'isCustomApi'


def list(
        environment,
        powerapps_url,
        powerapps_version,
        settings_file,
        raw_json=False):
    """
    List command.
    """
    # Get settings
    settings = SettingsBuilder.get_settings(
        environment=environment,
        settings_file=settings_file,
        api_properties=None,
        api_definition=None,
        icon=None,
        script=None,
        connector_id=None,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version)

    powerapps_rp, _ = load_powerapps_and_flow_rp(
        settings=settings,
        command_context=_LIST)

    connectors = powerapps_rp.get_all_connectors(
        environment=settings.environment)

    if 'value' in connectors and connectors['value']:
        # Filter to only custom connectors
        all_connectors = connectors['value']
        custom_connectors = [
            conn for conn in all_connectors
            if conn.get(_PROPERTIES, {}).get(_IS_CUSTOM_API, False)
        ]

        if custom_connectors:
            if raw_json:
                display(json.dumps(custom_connectors, indent=2))
            else:
                display('Found {} custom connector(s) in environment {}:'.format(
                    len(custom_connectors),
                    settings.environment))

                for connector in custom_connectors:
                    display('  - {}'.format(
                        connector.get('name', 'Unknown')))

                    # Show additional details if available
                    properties = connector.get('properties', {})
                    display_name = properties.get('displayName', '')
                    description = properties.get('description', '')
                    created_by = properties.get('createdBy', {})
                    creator_name = created_by.get('displayName', '') if created_by else ''

                    if display_name:
                        display('    Display Name: {}'.format(display_name))
                    if description:
                        display('    Description: {}'.format(description[:100] + ('...' if len(description) > 100 else '')))
                    if creator_name:
                        display('    Created By: {}'.format(creator_name))

                    display('')  # Empty line for readability
        else:
            display('No custom connectors found in environment {}.'.format(settings.environment))
    else:
        display('No custom connectors found in environment {}.'.format(settings.environment))
