# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer, Label

import asyncio
from typing import Any
from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer
from textual.command import Provider, Hit
from rich.style import Style
from functools import partial


class CustomCommand(Provider):

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        #self.table = None

    #async def startup(self) -> None:
    #    my_app = self.app
    #    my_app.log.info(f"Loaded provider: CustomCommand")
    #    self.table = my_app.query(DataTable).first()

    async def search(self, query: str) -> Hit:
        matcher = self.matcher(query)

        #my_app = self.screen.app
        #assert isinstance(my_app, CompetitorsApp)
        '''
        my_app.log.info(f"Got query: {query}")
        for row_key in self.table.rows:
            row = self.table.get_row(row_key)
            my_app.log.info(f"Searching {row}")
            searchable = row[1]
            score = matcher.match(searchable)
            if score > 0:
                runner_detail = DetailScreen(row=row)
                yield Hit(
                    score,
                    matcher.highlight(f"{searchable}"),
                    partial(my_app.show_detail, runner_detail),
                    help=f"Show details about {searchable}"
                )
        '''

        my_app: App = self.screen.app
        for mode in my_app.MODES:
            print(mode)
            my_app.log.info(f"Searching {mode}")

            #searchable = "briques"
            searchable = f"page {mode}"
            score = matcher.match(searchable)
            if score > 0:
                #runner_detail = DetailScreen(row=row)
                yield Hit(
                    score,
                    matcher.highlight(f"{searchable}"),
                    #partial(my_app.show_detail, runner_detail),
                    partial(self.screen.app.switch_mode, mode),
                    help=f"switch_mode {searchable}"
                )
