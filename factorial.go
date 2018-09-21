// factorial - A maubot plugin that calculates factorials.
// Copyright (C) 2018 Tulir Asokan
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>. 

package main

import (
	"fmt"
	"math/big"
	"strconv"
	"strings"

	"maubot.xyz"
)

type FactorialBot struct {
	client maubot.MatrixClient
	log    maubot.Logger
}

const CommandFactorial = "xyz.maubot.factorial"

func (bot *FactorialBot) Start() {
	bot.client.SetCommandSpec(&maubot.CommandSpec{
		PassiveCommands: []maubot.PassiveCommand{{
			Name:         CommandFactorial,
			Matches:      "([0-9]+)(!+)",
			MatchAgainst: maubot.MatchAgainstBody,
		}},
	})
	bot.client.AddCommandHandler(CommandFactorial, bot.MessageHandler)
}

func (bot *FactorialBot) Stop() {}

func factorial(n, interval int64) (result *big.Int) {
	result = big.NewInt(1)
	for i := n; i > 0; i -= interval {
		result.Mul(result, big.NewInt(i))
	}
	return result
}

const MaxFactorial = 10000
const MaxExactValueLength = 50
const ScientificNotationDecimals = 5

func (bot *FactorialBot) MessageHandler(evt *maubot.Event) maubot.CommandHandlerResult {
	command, ok := evt.Unsigned.PassiveCommand[CommandFactorial]
	if !ok || len(command.Captured) == 0 {
		return maubot.Continue
	}

	evt.MarkRead()
	var msg strings.Builder
	for _, capture := range command.Captured {
		if len(capture) != 3 {
			continue
		}

		n, err := strconv.Atoi(capture[1])
		if err != nil {
			continue
		}

		interval := len(capture[2])

		var result string
		if n/interval > MaxFactorial {
			result = "over 9000"
		} else {
			result = factorial(int64(n), int64(interval)).String()
			if len(result) > MaxExactValueLength {
				result = fmt.Sprintf("%c.%s × 10<sup>%d</sup>",
					result[0],
					result[1:ScientificNotationDecimals+1],
					len(result)-1)
			}
		}
		fmt.Fprintf(&msg, "%d%s = %s  \n", n, strings.Repeat("!", interval), result)
	}
	if msg.Len() == 0 {
		return maubot.Continue
	}
	_, err := evt.Reply(msg.String())
	if err != nil {
		bot.log.Errorfln("Failed to reply to %s: %v", evt.ID, err)
	}
	return maubot.StopCommandPropagation
}

var Plugin = maubot.PluginCreator{
	Create: func(client maubot.MatrixClient, logger maubot.Logger) maubot.Plugin {
		return &FactorialBot{
			client: client,
			log:    logger,
		}
	},
	Name:    "maubot.xyz/factorial",
	Version: "1.0.0",
}
