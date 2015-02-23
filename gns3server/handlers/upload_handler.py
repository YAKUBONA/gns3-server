# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import stat

from ..config import Config
from ..web.route import Route


class UploadHandler:

    @classmethod
    @Route.get(
        r"/upload",
        description="Manage upload of GNS3 images",
        api_version=None
    )
    def index(request, response):
        image_files = []
        try:
            for root, _, files in os.walk(UploadHandler.image_directory()):
                for filename in files:
                    image_file = os.path.join(root, filename)
                    if os.access(image_file, os.X_OK):
                        image_files.append(os.path.join(root, filename))
        except OSError:
            pass
        response.template("upload.html", files=image_files)

    @classmethod
    @Route.post(
        r"/upload",
        description="Manage upload of GNS3 images",
        api_version=None
    )
    def upload(request, response):
        data = yield from request.post()

        if not data["file"]:
            response.redirect("/upload")
            return

        destination_path = os.path.join(UploadHandler.image_directory(), data["file"].filename)
        try:
            os.makedirs(UploadHandler.image_directory(), exist_ok=True)
            with open(destination_path, "wb+") as f:
                chunk = data["file"].file.read()
                f.write(chunk)
            st = os.stat(destination_path)
            os.chmod(destination_path, st.st_mode | stat.S_IXUSR)
        except OSError as e:
            response.html("Could not upload file: {}".format(e))
            response.set_status(500)
            return
        response.redirect("/upload")

    @staticmethod
    def image_directory():
        server_config = Config.instance().get_section_config("Server")
        return os.path.expanduser(server_config.get("image_directory", "~/GNS3/images"))
