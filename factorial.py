# factorial - A maubot plugin that calculates factorials.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import List, Tuple

from maubot import Plugin, MessageEvent
from maubot.handlers import command

MAX_FACTORIAL = 10000
MAX_EXACT_VALUE_LENGTH = 50
MAX_FACTORIALS_IN_MESSAGE = 10
SCIENTIFIC_NOTATION_DECIMALS = 5


class FactorialBot(Plugin):
    @staticmethod
    def _factorial(n: int, interval: int) -> int:
        if n < 0:
            raise ValueError("factorial() not defined for negative values")
        result = 1
        while n > 0:
            result *= n
            n -= interval
        return result

    @command.passive("([0-9]+)(!+)", multiple=True)
    async def handler(self, evt: MessageEvent, matches: List[Tuple[str, str]]) -> None:
        await evt.mark_read()
        msgs = []
        for _, n_str, interval_str in matches:
            if len(msgs) >= MAX_FACTORIALS_IN_MESSAGE:
                msgs.append("...")
                break

            n = int(n_str)
            interval = len(interval_str)
            symbol = "="
            if n / interval > MAX_FACTORIAL:
                result = "over 9000"
                symbol = "is"
            else:
                result = str(self._factorial(n, interval))
                if len(result) > MAX_EXACT_VALUE_LENGTH:
                    result = (f"{result[0]}.{result[1:SCIENTIFIC_NOTATION_DECIMALS+1]}"
                              f" × 10<sup>{len(result)-1}</sup>")
                    symbol = "≈"
            msgs.append(f"{n}{'!' * interval} {symbol} {result}  ")
        if len(msgs) == 0:
            return
        await evt.reply("\n".join(msgs), allow_html=True)
