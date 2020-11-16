# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.dataproc_v1.services.workflow_template_service import (
    WorkflowTemplateServiceAsyncClient,
)
from google.cloud.dataproc_v1.services.workflow_template_service import (
    WorkflowTemplateServiceClient,
)
from google.cloud.dataproc_v1.services.workflow_template_service import pagers
from google.cloud.dataproc_v1.services.workflow_template_service import transports
from google.cloud.dataproc_v1.types import clusters
from google.cloud.dataproc_v1.types import jobs
from google.cloud.dataproc_v1.types import shared
from google.cloud.dataproc_v1.types import workflow_templates
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert WorkflowTemplateServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        WorkflowTemplateServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        WorkflowTemplateServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        WorkflowTemplateServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        WorkflowTemplateServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        WorkflowTemplateServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [WorkflowTemplateServiceClient, WorkflowTemplateServiceAsyncClient]
)
def test_workflow_template_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds

        assert client.transport._host == "dataproc.googleapis.com:443"


def test_workflow_template_service_client_get_transport_class():
    transport = WorkflowTemplateServiceClient.get_transport_class()
    assert transport == transports.WorkflowTemplateServiceGrpcTransport

    transport = WorkflowTemplateServiceClient.get_transport_class("grpc")
    assert transport == transports.WorkflowTemplateServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            WorkflowTemplateServiceClient,
            transports.WorkflowTemplateServiceGrpcTransport,
            "grpc",
        ),
        (
            WorkflowTemplateServiceAsyncClient,
            transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    WorkflowTemplateServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(WorkflowTemplateServiceClient),
)
@mock.patch.object(
    WorkflowTemplateServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(WorkflowTemplateServiceAsyncClient),
)
def test_workflow_template_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(WorkflowTemplateServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(WorkflowTemplateServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (
            WorkflowTemplateServiceClient,
            transports.WorkflowTemplateServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            WorkflowTemplateServiceAsyncClient,
            transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            WorkflowTemplateServiceClient,
            transports.WorkflowTemplateServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            WorkflowTemplateServiceAsyncClient,
            transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    WorkflowTemplateServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(WorkflowTemplateServiceClient),
)
@mock.patch.object(
    WorkflowTemplateServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(WorkflowTemplateServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_workflow_template_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            ssl_channel_creds = mock.Mock()
            with mock.patch(
                "grpc.ssl_channel_credentials", return_value=ssl_channel_creds
            ):
                patched.return_value = None
                client = client_class(client_options=options)

                if use_client_cert_env == "false":
                    expected_ssl_channel_creds = None
                    expected_host = client.DEFAULT_ENDPOINT
                else:
                    expected_ssl_channel_creds = ssl_channel_creds
                    expected_host = client.DEFAULT_MTLS_ENDPOINT

                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=expected_host,
                    scopes=None,
                    ssl_channel_credentials=expected_ssl_channel_creds,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    with mock.patch(
                        "google.auth.transport.grpc.SslCredentials.ssl_credentials",
                        new_callable=mock.PropertyMock,
                    ) as ssl_credentials_mock:
                        if use_client_cert_env == "false":
                            is_mtls_mock.return_value = False
                            ssl_credentials_mock.return_value = None
                            expected_host = client.DEFAULT_ENDPOINT
                            expected_ssl_channel_creds = None
                        else:
                            is_mtls_mock.return_value = True
                            ssl_credentials_mock.return_value = mock.Mock()
                            expected_host = client.DEFAULT_MTLS_ENDPOINT
                            expected_ssl_channel_creds = (
                                ssl_credentials_mock.return_value
                            )

                        patched.return_value = None
                        client = client_class()
                        patched.assert_called_once_with(
                            credentials=None,
                            credentials_file=None,
                            host=expected_host,
                            scopes=None,
                            ssl_channel_credentials=expected_ssl_channel_creds,
                            quota_project_id=None,
                            client_info=transports.base.DEFAULT_CLIENT_INFO,
                        )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    is_mtls_mock.return_value = False
                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=client.DEFAULT_ENDPOINT,
                        scopes=None,
                        ssl_channel_credentials=None,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            WorkflowTemplateServiceClient,
            transports.WorkflowTemplateServiceGrpcTransport,
            "grpc",
        ),
        (
            WorkflowTemplateServiceAsyncClient,
            transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_workflow_template_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            WorkflowTemplateServiceClient,
            transports.WorkflowTemplateServiceGrpcTransport,
            "grpc",
        ),
        (
            WorkflowTemplateServiceAsyncClient,
            transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_workflow_template_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_workflow_template_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.dataproc_v1.services.workflow_template_service.transports.WorkflowTemplateServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = WorkflowTemplateServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_workflow_template(
    transport: str = "grpc",
    request_type=workflow_templates.CreateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate(
            id="id_value", name="name_value", version=774,
        )

        response = client.create_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.CreateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


def test_create_workflow_template_from_dict():
    test_create_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_create_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.CreateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate(
                id="id_value", name="name_value", version=774,
            )
        )

        response = await client.create_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.CreateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


@pytest.mark.asyncio
async def test_create_workflow_template_async_from_dict():
    await test_create_workflow_template_async(request_type=dict)


def test_create_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.CreateWorkflowTemplateRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        call.return_value = workflow_templates.WorkflowTemplate()

        client.create_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.CreateWorkflowTemplateRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )

        await client.create_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_workflow_template(
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


def test_create_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_workflow_template(
            workflow_templates.CreateWorkflowTemplateRequest(),
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


@pytest.mark.asyncio
async def test_create_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_workflow_template(
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


@pytest.mark.asyncio
async def test_create_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_workflow_template(
            workflow_templates.CreateWorkflowTemplateRequest(),
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


def test_get_workflow_template(
    transport: str = "grpc", request_type=workflow_templates.GetWorkflowTemplateRequest
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate(
            id="id_value", name="name_value", version=774,
        )

        response = client.get_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.GetWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


def test_get_workflow_template_from_dict():
    test_get_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_get_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.GetWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate(
                id="id_value", name="name_value", version=774,
            )
        )

        response = await client.get_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.GetWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


@pytest.mark.asyncio
async def test_get_workflow_template_async_from_dict():
    await test_get_workflow_template_async(request_type=dict)


def test_get_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.GetWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        call.return_value = workflow_templates.WorkflowTemplate()

        client.get_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.GetWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )

        await client.get_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_workflow_template(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_workflow_template(
            workflow_templates.GetWorkflowTemplateRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_workflow_template(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_workflow_template(
            workflow_templates.GetWorkflowTemplateRequest(), name="name_value",
        )


def test_instantiate_workflow_template(
    transport: str = "grpc",
    request_type=workflow_templates.InstantiateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.instantiate_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.InstantiateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_instantiate_workflow_template_from_dict():
    test_instantiate_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_instantiate_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.InstantiateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.instantiate_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.InstantiateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_instantiate_workflow_template_async_from_dict():
    await test_instantiate_workflow_template_async(request_type=dict)


def test_instantiate_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.InstantiateWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.instantiate_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_instantiate_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.InstantiateWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.instantiate_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_instantiate_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.instantiate_workflow_template(
            name="name_value", parameters={"key_value": "value_value"},
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].parameters == {"key_value": "value_value"}


def test_instantiate_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.instantiate_workflow_template(
            workflow_templates.InstantiateWorkflowTemplateRequest(),
            name="name_value",
            parameters={"key_value": "value_value"},
        )


@pytest.mark.asyncio
async def test_instantiate_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.instantiate_workflow_template(
            name="name_value", parameters={"key_value": "value_value"},
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].parameters == {"key_value": "value_value"}


@pytest.mark.asyncio
async def test_instantiate_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.instantiate_workflow_template(
            workflow_templates.InstantiateWorkflowTemplateRequest(),
            name="name_value",
            parameters={"key_value": "value_value"},
        )


def test_instantiate_inline_workflow_template(
    transport: str = "grpc",
    request_type=workflow_templates.InstantiateInlineWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.instantiate_inline_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.InstantiateInlineWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_instantiate_inline_workflow_template_from_dict():
    test_instantiate_inline_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_instantiate_inline_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.InstantiateInlineWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.instantiate_inline_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.InstantiateInlineWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_instantiate_inline_workflow_template_async_from_dict():
    await test_instantiate_inline_workflow_template_async(request_type=dict)


def test_instantiate_inline_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.InstantiateInlineWorkflowTemplateRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.instantiate_inline_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_instantiate_inline_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.InstantiateInlineWorkflowTemplateRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.instantiate_inline_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_instantiate_inline_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.instantiate_inline_workflow_template(
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


def test_instantiate_inline_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.instantiate_inline_workflow_template(
            workflow_templates.InstantiateInlineWorkflowTemplateRequest(),
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


@pytest.mark.asyncio
async def test_instantiate_inline_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.instantiate_inline_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.instantiate_inline_workflow_template(
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


@pytest.mark.asyncio
async def test_instantiate_inline_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.instantiate_inline_workflow_template(
            workflow_templates.InstantiateInlineWorkflowTemplateRequest(),
            parent="parent_value",
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


def test_update_workflow_template(
    transport: str = "grpc",
    request_type=workflow_templates.UpdateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate(
            id="id_value", name="name_value", version=774,
        )

        response = client.update_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.UpdateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


def test_update_workflow_template_from_dict():
    test_update_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_update_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.UpdateWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate(
                id="id_value", name="name_value", version=774,
            )
        )

        response = await client.update_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.UpdateWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, workflow_templates.WorkflowTemplate)

    assert response.id == "id_value"

    assert response.name == "name_value"

    assert response.version == 774


@pytest.mark.asyncio
async def test_update_workflow_template_async_from_dict():
    await test_update_workflow_template_async(request_type=dict)


def test_update_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.UpdateWorkflowTemplateRequest()
    request.template.name = "template.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        call.return_value = workflow_templates.WorkflowTemplate()

        client.update_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "template.name=template.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.UpdateWorkflowTemplateRequest()
    request.template.name = "template.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )

        await client.update_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "template.name=template.name/value",) in kw[
        "metadata"
    ]


def test_update_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_workflow_template(
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


def test_update_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_workflow_template(
            workflow_templates.UpdateWorkflowTemplateRequest(),
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


@pytest.mark.asyncio
async def test_update_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.WorkflowTemplate()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.WorkflowTemplate()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_workflow_template(
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].template == workflow_templates.WorkflowTemplate(id="id_value")


@pytest.mark.asyncio
async def test_update_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_workflow_template(
            workflow_templates.UpdateWorkflowTemplateRequest(),
            template=workflow_templates.WorkflowTemplate(id="id_value"),
        )


def test_list_workflow_templates(
    transport: str = "grpc",
    request_type=workflow_templates.ListWorkflowTemplatesRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.ListWorkflowTemplatesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_workflow_templates(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.ListWorkflowTemplatesRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListWorkflowTemplatesPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_workflow_templates_from_dict():
    test_list_workflow_templates(request_type=dict)


@pytest.mark.asyncio
async def test_list_workflow_templates_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.ListWorkflowTemplatesRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.ListWorkflowTemplatesResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_workflow_templates(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.ListWorkflowTemplatesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListWorkflowTemplatesAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_workflow_templates_async_from_dict():
    await test_list_workflow_templates_async(request_type=dict)


def test_list_workflow_templates_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.ListWorkflowTemplatesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        call.return_value = workflow_templates.ListWorkflowTemplatesResponse()

        client.list_workflow_templates(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_workflow_templates_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.ListWorkflowTemplatesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.ListWorkflowTemplatesResponse()
        )

        await client.list_workflow_templates(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_workflow_templates_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.ListWorkflowTemplatesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_workflow_templates(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_workflow_templates_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_workflow_templates(
            workflow_templates.ListWorkflowTemplatesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_workflow_templates_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = workflow_templates.ListWorkflowTemplatesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            workflow_templates.ListWorkflowTemplatesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_workflow_templates(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_workflow_templates_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_workflow_templates(
            workflow_templates.ListWorkflowTemplatesRequest(), parent="parent_value",
        )


def test_list_workflow_templates_pager():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
                next_page_token="abc",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[], next_page_token="def",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[workflow_templates.WorkflowTemplate(),],
                next_page_token="ghi",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_workflow_templates(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, workflow_templates.WorkflowTemplate) for i in results)


def test_list_workflow_templates_pages():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
                next_page_token="abc",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[], next_page_token="def",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[workflow_templates.WorkflowTemplate(),],
                next_page_token="ghi",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_workflow_templates(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_workflow_templates_async_pager():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
                next_page_token="abc",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[], next_page_token="def",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[workflow_templates.WorkflowTemplate(),],
                next_page_token="ghi",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_workflow_templates(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, workflow_templates.WorkflowTemplate) for i in responses
        )


@pytest.mark.asyncio
async def test_list_workflow_templates_async_pages():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_workflow_templates),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
                next_page_token="abc",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[], next_page_token="def",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[workflow_templates.WorkflowTemplate(),],
                next_page_token="ghi",
            ),
            workflow_templates.ListWorkflowTemplatesResponse(
                templates=[
                    workflow_templates.WorkflowTemplate(),
                    workflow_templates.WorkflowTemplate(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_workflow_templates(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_workflow_template(
    transport: str = "grpc",
    request_type=workflow_templates.DeleteWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.DeleteWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_workflow_template_from_dict():
    test_delete_workflow_template(request_type=dict)


@pytest.mark.asyncio
async def test_delete_workflow_template_async(
    transport: str = "grpc_asyncio",
    request_type=workflow_templates.DeleteWorkflowTemplateRequest,
):
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == workflow_templates.DeleteWorkflowTemplateRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_workflow_template_async_from_dict():
    await test_delete_workflow_template_async(request_type=dict)


def test_delete_workflow_template_field_headers():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.DeleteWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        call.return_value = None

        client.delete_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_workflow_template_field_headers_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = workflow_templates.DeleteWorkflowTemplateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_workflow_template(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_workflow_template_flattened():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_workflow_template(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_workflow_template_flattened_error():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_workflow_template(
            workflow_templates.DeleteWorkflowTemplateRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_workflow_template_flattened_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_workflow_template), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_workflow_template(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_workflow_template_flattened_error_async():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_workflow_template(
            workflow_templates.DeleteWorkflowTemplateRequest(), name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = WorkflowTemplateServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = WorkflowTemplateServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = WorkflowTemplateServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = WorkflowTemplateServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.WorkflowTemplateServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.WorkflowTemplateServiceGrpcTransport,
        transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport, transports.WorkflowTemplateServiceGrpcTransport,
    )


def test_workflow_template_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.WorkflowTemplateServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_workflow_template_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.dataproc_v1.services.workflow_template_service.transports.WorkflowTemplateServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.WorkflowTemplateServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_workflow_template",
        "get_workflow_template",
        "instantiate_workflow_template",
        "instantiate_inline_workflow_template",
        "update_workflow_template",
        "list_workflow_templates",
        "delete_workflow_template",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_workflow_template_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.dataproc_v1.services.workflow_template_service.transports.WorkflowTemplateServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.WorkflowTemplateServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_workflow_template_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.dataproc_v1.services.workflow_template_service.transports.WorkflowTemplateServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.WorkflowTemplateServiceTransport()
        adc.assert_called_once()


def test_workflow_template_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        WorkflowTemplateServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


def test_workflow_template_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.WorkflowTemplateServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_workflow_template_service_host_no_port():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="dataproc.googleapis.com"
        ),
    )
    assert client.transport._host == "dataproc.googleapis.com:443"


def test_workflow_template_service_host_with_port():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="dataproc.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "dataproc.googleapis.com:8000"


def test_workflow_template_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.WorkflowTemplateServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_workflow_template_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.WorkflowTemplateServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.WorkflowTemplateServiceGrpcTransport,
        transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
    ],
)
def test_workflow_template_service_transport_channel_mtls_with_client_cert_source(
    transport_class,
):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.WorkflowTemplateServiceGrpcTransport,
        transports.WorkflowTemplateServiceGrpcAsyncIOTransport,
    ],
)
def test_workflow_template_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_workflow_template_service_grpc_lro_client():
    client = WorkflowTemplateServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_workflow_template_service_grpc_lro_async_client():
    client = WorkflowTemplateServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_workflow_template_path():
    project = "squid"
    region = "clam"
    workflow_template = "whelk"

    expected = "projects/{project}/regions/{region}/workflowTemplates/{workflow_template}".format(
        project=project, region=region, workflow_template=workflow_template,
    )
    actual = WorkflowTemplateServiceClient.workflow_template_path(
        project, region, workflow_template
    )
    assert expected == actual


def test_parse_workflow_template_path():
    expected = {
        "project": "octopus",
        "region": "oyster",
        "workflow_template": "nudibranch",
    }
    path = WorkflowTemplateServiceClient.workflow_template_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_workflow_template_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "cuttlefish"

    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = WorkflowTemplateServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "mussel",
    }
    path = WorkflowTemplateServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "winkle"

    expected = "folders/{folder}".format(folder=folder,)
    actual = WorkflowTemplateServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nautilus",
    }
    path = WorkflowTemplateServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "scallop"

    expected = "organizations/{organization}".format(organization=organization,)
    actual = WorkflowTemplateServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "abalone",
    }
    path = WorkflowTemplateServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "squid"

    expected = "projects/{project}".format(project=project,)
    actual = WorkflowTemplateServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "clam",
    }
    path = WorkflowTemplateServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "whelk"
    location = "octopus"

    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = WorkflowTemplateServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
    }
    path = WorkflowTemplateServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = WorkflowTemplateServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.WorkflowTemplateServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = WorkflowTemplateServiceClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.WorkflowTemplateServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = WorkflowTemplateServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
