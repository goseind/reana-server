# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2021, 2022 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Server info functionality Flask-Blueprint."""

import logging
import traceback

from flask import Blueprint, jsonify
from marshmallow import Schema, fields

from reana_commons.config import DEFAULT_WORKSPACE_PATH, WORKSPACE_PATHS

from reana_server.config import (
    SUPPORTED_COMPUTE_BACKENDS,
    WORKSPACE_RETENTION_PERIOD,
    REANA_KUBERNETES_JOBS_MAX_USER_MEMORY_LIMIT,
    REANA_KUBERNETES_JOBS_MEMORY_LIMIT,
    REANA_KUBERNETES_JOBS_TIMEOUT_LIMIT,
    REANA_KUBERNETES_JOBS_MAX_USER_TIMEOUT_LIMIT,
)
from reana_server.decorators import signin_required

blueprint = Blueprint("info", __name__)


@blueprint.route("/info", methods=["GET"])
@signin_required(token_required=False)
def info(user, **kwargs):  # noqa
    r"""Get information about the cluster capabilities.

    ---
    get:
      summary: Get information about the cluster capabilities.
      operationId: info
      description: >-
        This resource reports information about cluster capabilities.
      produces:
       - application/json
      parameters:
        - name: access_token
          in: query
          description: The API access_token of workflow owner.
          required: true
          type: string
      responses:
        200:
          description: >-
            Request succeeded. The response contains general info about the cluster.
          schema: InfoSchema
          examples:
            application/json:
              {
                "workspaces_available": {
                    "title": "List of available workspaces",
                    "value": ["/usr/share","/eos/home","/var/reana"]
                },
                "default_workspace": {
                    "title": "Default workspace",
                    "value": "/usr/share"
                },
                "compute_backends": {
                    "title": "List of supported compute backends",
                    "value": [
                        "kubernetes",
                        "htcondorcern",
                        "slurmcern"
                    ]
                },
                "kubernetes_memory_limit": {
                    "title": "Default memory limit for Kubernetes jobs",
                    "value": "3Gi"
                },
                "kubernetes_max_memory_limit": {
                    "title": "Maximum allowed memory limit for Kubernetes jobs",
                    "value": "10Gi"
                },
                "maximum_workspace_retention_period": {
                    "title": "Maximum retention period in days for workspace files",
                    "value": "3650"
                },
                "default_kubernetes_jobs_timeout": {
                    "title": "Default timeout for Kubernetes jobs",
                    "value": "604800"
                },
                "maximum_kubernetes_jobs_timeout": {
                    "title": "Maximum timeout for Kubernetes jobs",
                    "value": "1209600"
                },
              }
        500:
          description: >-
            Request failed. Internal controller error.
          schema:
            type: object
            properties:
              message:
                type: string
          examples:
            application/json:
              {
                "message": "Internal controller error."
              }
    """
    try:
        cluster_information = dict(
            workspaces_available=dict(
                title="List of available workspaces",
                value=list(WORKSPACE_PATHS.values()),
            ),
            default_workspace=dict(
                title="Default workspace", value=DEFAULT_WORKSPACE_PATH
            ),
            compute_backends=dict(
                title="List of supported compute backends",
                value=SUPPORTED_COMPUTE_BACKENDS,
            ),
            default_kubernetes_memory_limit=dict(
                title="Default memory limit for Kubernetes jobs",
                value=REANA_KUBERNETES_JOBS_MEMORY_LIMIT,
            ),
            kubernetes_max_memory_limit=dict(
                title="Maximum allowed memory limit for Kubernetes jobs",
                value=REANA_KUBERNETES_JOBS_MAX_USER_MEMORY_LIMIT,
            ),
            maximum_workspace_retention_period=dict(
                title="Maximum retention period in days for workspace files",
                value=WORKSPACE_RETENTION_PERIOD,
            ),
            default_kubernetes_jobs_timeout=dict(
                title="Default timeout for Kubernetes jobs",
                value=REANA_KUBERNETES_JOBS_TIMEOUT_LIMIT,
            ),
            maximum_kubernetes_jobs_timeout=dict(
                title="Maximum timeout for Kubernetes jobs",
                value=REANA_KUBERNETES_JOBS_MAX_USER_TIMEOUT_LIMIT,
            ),
        )
        return InfoSchema().dump(cluster_information)

    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"message": str(e)}), 500


class ListStringInfoValue(Schema):
    """Schema for a value represented by a list of strings."""

    title = fields.String()
    value = fields.List(fields.String())


class StringInfoValue(Schema):
    """Schema for a value represented by a string."""

    title = fields.String()
    value = fields.String(allow_none=False)


class StringNullableInfoValue(Schema):
    """Schema for a value represented by a nullable string."""

    title = fields.String()
    value = fields.String(allow_none=True)


class InfoSchema(Schema):
    """Marshmallow schema for ``info`` endpoint."""

    workspaces_available = fields.Nested(ListStringInfoValue)
    default_workspace = fields.Nested(StringInfoValue)
    compute_backends = fields.Nested(ListStringInfoValue)
    default_kubernetes_memory_limit = fields.Nested(StringInfoValue)
    kubernetes_max_memory_limit = fields.Nested(StringNullableInfoValue)
    maximum_workspace_retention_period = fields.Nested(StringNullableInfoValue)
    default_kubernetes_jobs_timeout = fields.Nested(StringInfoValue)
    maximum_kubernetes_jobs_timeout = fields.Nested(StringInfoValue)
