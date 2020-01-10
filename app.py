#!/usr/bin/env python3
# Qeb-Hwt
# Copyright(C) 2019, 2020 Red Hat, Inc.
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This is Qeb-Hwt."""

import os
import asyncio
import pathlib
import logging

import gidgethub

from octomachinery.app.server.runner import run as run_app
from octomachinery.app.routing import process_event_actions, process_event
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from octomachinery.github.config.app import GitHubAppIntegrationConfig
from octomachinery.github.api.app_client import GitHubApp
from octomachinery.github.api.raw_client import GitHubAPI
from octomachinery.utils.versiontools import get_version_from_scm_tag

from thoth.common import init_logging

from thoth.qeb_hwt.version import __version__


init_logging()

_LOGGER = logging.getLogger("aicoe.sesheta")
_LOGGER.info(f"Qeb-Hwt GitHub App, v{__version__}")
logging.getLogger("octomachinery").setLevel(logging.DEBUG)


@process_event("ping")
@process_webhook_payload
async def on_ping(*, hook, hook_id, zen):
    """React to ping webhook event."""
    app_id = hook["app_id"]

    _LOGGER.info("Processing ping for App ID %s " "with Hook ID %s " "sharing Zen: %s", app_id, hook_id, zen)

    _LOGGER.info("GitHub App from context in ping handler: %s", RUNTIME_CONTEXT.github_app)


@process_event("integration_installation", action="created")
@process_webhook_payload
async def on_install(
    action,  # pylint: disable=unused-argument
    installation,
    sender,  # pylint: disable=unused-argument
    repositories=None,  # pylint: disable=unused-argument
):
    """React to GitHub App integration installation webhook event."""
    _LOGGER.info("installed event install id %s", installation["id"])
    _LOGGER.info("installation=%s", RUNTIME_CONTEXT.app_installation)


@process_event("pull_request")
@process_webhook_payload
async def on_pull_request(action, number, pull_request, repository, installation, **kwargs):
    """React to GitHub App pull_request event."""
    _LOGGER.info("a pull_request #%d has been %s: %s", number, action, pull_request["html_url"])

    repo: str = repository["full_name"]
    head_sha: str = pull_request["head"]["sha"]

    api_url = f"/repos/{repo}/check-runs"

    # if action == "opened":
    github_api: GitHubAPI = RUNTIME_CONTEXT.app_installation_client
    github_api.post(
        api_url,
        {"name": "Thoth: Advise", "head_sha": head_sha},
        accept="application/vnd.github.antiope-preview+json"
    )


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(  # pylint: disable=expression-not-assigned
        name="Qeb-Hwt GitHub App",
        version=get_version_from_scm_tag(root="./", relative_to=__file__),
        url="https://github.com/apps/qeb-hwt",
    )
