# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# dummy fastapi service to test BaseServiceContext
# cf https://fastapi.tiangolo.com/#example

from fastapi import FastAPI

app = FastAPI()


@app.get("/alive")
def alive():
    return {"Hello": "World"}
