# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
List command.
"""

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
        settings_file):
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
            # Return structured data with PascalCase keys for knack to format
            result_data = []
            for connector in custom_connectors:
                properties = connector.get('properties', {})
                created_by = properties.get('createdBy', {})
                
                connector_data = {
                    'Name': connector.get('name', ''),
                    'Id': connector.get('id', ''),
                    'Type': connector.get('type', ''),
                    'DisplayName': properties.get('displayName', ''),
                    'IconUri': properties.get('iconUri', ''),
                    'IconBrandColor': properties.get('iconBrandColor', ''),
                    'Description': properties.get('description', ''),
                    'CreatedBy': created_by.get('displayName', '') if created_by else ''
                }
                result_data.append(connector_data)
            
            return result_data
        else:
            display('No custom connectors found in environment {}.'.format(settings.environment))
            return []
    else:
        display('No custom connectors found in environment {}.'.format(settings.environment))
        return []
