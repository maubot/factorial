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
from __future__ import annotations

try:
    from _pydecimal import localcontext, Decimal, MAX_EMAX
    pydecimal = True
except ImportError:
    from decimal import localcontext, Decimal, MAX_EMAX
    pydecimal = False
import math

from maubot import Plugin, MessageEvent
from maubot.handlers import command

MAX_EXACT_FACTORIAL = 10000
if pydecimal:
    MAX_APPROX_FACTORIAL = 10**100
    MAX_FACTORIAL_EXPONENT = 10**110  # Approximate to fit the MAX_APPROX_FACTORIAL result
else:
    if MAX_EMAX >= 999999999999999999:  # 64-bit
        MAX_APPROX_FACTORIAL = 61154108320430275
    elif MAX_EMAX >= 425000000:  # 32-bit
        MAX_APPROX_FACTORIAL = 57988439
    else:  # ???
        MAX_APPROX_FACTORIAL = MAX_EXACT_FACTORIAL
    MAX_FACTORIAL_EXPONENT = MAX_EMAX
MAX_EXACT_VALUE_LENGTH = 50
MAX_EXACT_VALUE = 10 ** MAX_EXACT_VALUE_LENGTH - 1
MAX_FACTORIALS_IN_MESSAGE = 10
SCIENTIFIC_NOTATION_DECIMALS = 5


class FactorialBot(Plugin):
    @staticmethod
    def _stirling(n: int) -> Decimal:
        with localcontext() as ctx:
            ctx.Emax = MAX_FACTORIAL_EXPONENT
            dtau = Decimal(math.tau)
            de = Decimal(math.e)
            dn = Decimal(n)
            return (dtau * dn).sqrt() * (dn / de) ** dn

    @staticmethod
    def _factorial(n: int, interval: int) -> int:
        if n < 0:
            raise ValueError("factorial() not defined for negative values")
        result = 1
        while n > 0:
            result *= n
            n -= interval
        return result

    @staticmethod
    def _science(dec: Decimal) -> str:
        dt = dec.as_tuple()
        first_digit = dt.digits[0]
        decimals = dt.digits[1:SCIENTIFIC_NOTATION_DECIMALS+1]
        decimals_str = "".join(str(x) for x in decimals)
        exponent = dt.exponent + len(dt.digits) - 1
        return f"{first_digit}.{decimals_str} × 10<sup>{exponent}</sup>"

    @command.passive("([0-9]+)(!+)", multiple=True)
    async def handler(self, evt: MessageEvent, matches: list[tuple[str, str]]) -> None:
        await evt.mark_read()
        msgs = []
        for _, n_str, interval_str in matches:
            if len(msgs) >= MAX_FACTORIALS_IN_MESSAGE:
                msgs.append("...")
                break

            n = int(n_str)
            interval = len(interval_str)
            symbol = "="
            if n / interval > MAX_EXACT_FACTORIAL:
                if interval == 1 and n <= MAX_APPROX_FACTORIAL:
                    result = self._science(self._stirling(n))
                    symbol = "≈"
                else:
                    result = "over 9000"
                    symbol = "is"
            else:
                result = self._factorial(n, interval)
                if result > MAX_EXACT_VALUE:
                    result = self._science(Decimal(result))
                    symbol = "≈"
            msgs.append(f"{n}{'!' * interval} {symbol} {result}  ")
        if len(msgs) == 0:
            return
        await evt.reply("\n".join(msgs), allow_html=True)
