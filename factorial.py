# factorial - A maubot plugin that calculates factorials.
# Copyright (C) 2018 Tulir Asokan
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
from maubot import Plugin, CommandSpec, PassiveCommand
from mautrix.types import MessageEvent

COMMAND_FACTORIAL = "xyz.maubot.factorial"

MAX_FACTORIAL = 10000
MAX_EXACT_VALUE_LENGTH = 50
MAX_FACTORIALS_IN_MESSAGE = 10
SCIENTIFIC_NOTATION_DECIMALS = 5


class FactorialBot(Plugin):
    async def start(self) -> None:
        self.set_command_spec(CommandSpec(
            passive_commands=[PassiveCommand(
                name=COMMAND_FACTORIAL,
                matches="([0-9]+)(!+)",
                match_against="body",
            )],
        ))
        self.client.add_command_handler(COMMAND_FACTORIAL, self.handler)

    @staticmethod
    def _factorial(n: int, interval: int) -> int:
        if n < 0:
            raise ValueError("factorial() not defined for negative values")
        result = 1
        while n > 0:
            result *= n
            n -= interval
        return result

    async def handler(self, evt: MessageEvent) -> None:
        try:
            command = evt.unsigned.passive_command[COMMAND_FACTORIAL]
        except KeyError:
            return
        await evt.mark_read()
        msgs = []
        for capture in command.captured:
            if len(msgs) >= MAX_FACTORIALS_IN_MESSAGE:
                msgs.append("...")
                break
            elif len(capture) != 3:
                continue

            n = int(capture[1])
            interval = len(capture[2])
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
        await evt.reply("\n".join(msgs))
