#!/bin/env python
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from nmigen import signed, unsigned, Cat, Signal, Module
from nmigen.lib.fifo import SyncFIFOBuffered
from nmigen.hdl.dsl import FSM
from nmigen_cfu import SimpleElaboratable

from .stream import PayloadDefinition, Endpoint


class StreamFifo(SimpleElaboratable):
    """A FIFO with stream interfaces.

    Parameters:
    -----------

    type: PayloadDefinition
      The type of the item that will be passed through the FIFO
    depth:
      The number of items contained by the fifo


    Attributes:
    ----------

    input: Endpoint(type), in
      Incoming stream of items
    output: Endpoint(type), out
      Outgoing stream of items

    """

    def __init__(self, *, type, depth):
        self.depth = depth
        self.input = Endpoint(type)
        self.output = Endpoint(type)

    def elab(self, m: Module):
        m.submodules.wrapped = fifo = SyncFIFOBuffered(
            depth=self.depth, width=len(self.input.payload))

        m.d.comb += [
            fifo.w_en.eq(self.input.valid),
            fifo.w_data.eq(self.input.payload),
            self.input.ready.eq(fifo.w_rdy),
            self.output.valid.eq(fifo.r_rdy),
            self.output.payload.eq(fifo.r_data),
            fifo.r_en.eq(self.output.ready),
        ]