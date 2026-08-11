# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Delete command.
"""

from paconn import _DELETE
from paconn.common.util import display
from paconn.settings.util import load_powerapps_and_flow_rp
from paconn.settings.settingsbuilder import SettingsBuilder
from knack.prompting import prompt_y_n


def delete(
        environment,
        connector_id,
        force,
        powerapps_url,
        powerapps_version,
        settings_file):
    """
    Delete command to remove a custom connector.
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
        command_context=_DELETE)

    # Get connector info for display purposes
    try:
        connector_info = powerapps_rp.get_connector(
            environment=settings.environment,
            connector_id=settings.connector_id)

        connector_name = connector_info.get('properties', {}).get('displayName', settings.connector_id)
        display(f'Target connector: {connector_name} ({settings.connector_id})')
    except Exception:
        # If we can't get connector info, just proceed with the ID
        connector_name = settings.connector_id
        display(f'Target connector: {settings.connector_id}')

    # Confirm deletion unless force is specified
    if not force:
        confirm = prompt_y_n(f'Are you sure you want to delete connector "{connector_name}"? '
                             'This action cannot be undone.')
        if not confirm:
            display('Delete operation cancelled.')
            return

    # Perform the deletion
    try:
        response_text = powerapps_rp.delete_connector(
            environment=settings.environment,
            connector_id=settings.connector_id)

        display(f'Connector "{connector_name}" deleted successfully.')
        if response_text and response_text.strip():
            display(f'Response: {response_text}')

    except Exception as e:
        display(f'Error deleting connector: {str(e)}')
        raise
