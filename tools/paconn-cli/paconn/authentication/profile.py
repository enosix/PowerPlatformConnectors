# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""
User profile management class.`
"""
import adal
from urllib.parse import urljoin
# AADTokenCredentials for multi-factor authentication
from msrestazure.azure_active_directory import AADTokenCredentials
import requests
import json


class Profile:
    """
    A Class representing user profile.
    """

    def __init__(self, client_id, tenant, resource, authority_url):
        self.client_id = client_id
        self.tenant = tenant
        self.resource = resource
        self.authority_url = authority_url

    def _get_authentication_context(self):
        auth_url = urljoin(self.authority_url, self.tenant)

        return adal.AuthenticationContext(
            authority=auth_url,
            api_version=None)

    def authenticate_device_code(self):
        """
        Authenticate the end-user using device auth.
        """
        context = self._get_authentication_context()

        code = context.acquire_user_code(
            resource=self.resource,
            client_id=self.client_id)

        print(code['message'])

        mgmt_token = context.acquire_token_with_device_code(
            resource=self.resource,
            user_code_info=code,
            client_id=self.client_id)

        credentials = AADTokenCredentials(
            token=mgmt_token,
            client_id=self.client_id)

        return credentials.token

    def _get_service_principal_object_id(self, graph_token, client_id):
        """
        Get the object ID of the service principal using Microsoft Graph API.
        """
        try:
            # Extract access token from the ADAL token response
            access_token = graph_token.get('accessToken') or graph_token.get('access_token')
            if not access_token:
                return client_id
                
            # Microsoft Graph API endpoint to get service principal by appId
            url = f"https://graph.microsoft.com/v1.0/servicePrincipals?$filter=appId eq '{client_id}'"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('value') and len(data['value']) > 0:
                return data['value'][0]['id']  # This is the object ID
            else:
                # Fallback to client_id if we can't find the service principal
                return client_id
        except Exception:
            # Fallback to client_id if Graph API call fails
            return client_id

    def authenticate_service_principal(self, client_secret):
        """
        Authenticate using service principal credentials.
        """
        context = self._get_authentication_context()

        # First, get a token for Microsoft Graph to look up the service principal object ID
        graph_token = context.acquire_token_with_client_credentials(
            resource="https://graph.microsoft.com/",
            client_id=self.client_id,
            client_secret=client_secret)

        # Get the service principal's actual object ID
        sp_object_id = self._get_service_principal_object_id(
            graph_token, 
            self.client_id)

        # Now get the token for the actual resource
        mgmt_token = context.acquire_token_with_client_credentials(
            resource=self.resource,
            client_id=self.client_id,
            client_secret=client_secret)

        credentials = AADTokenCredentials(
            token=mgmt_token,
            client_id=self.client_id)

        # Add the correct oid (service principal object ID)
        token = credentials.token
        token['oid'] = sp_object_id

        return token
