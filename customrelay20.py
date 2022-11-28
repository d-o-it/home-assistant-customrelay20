"""Custom Relay 20 implementation."""

import logging
import asyncio
import asyncio.tasks
import serialio

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = 3.0


class CustomRelay20:
    def __init__(self, serial: serialio) -> None:
        self.serial = serial
        self.serial_lock = asyncio.Lock()

    async def __worker(self, cmd: int):
        try:
            await self.serial.open()
            data = bytearray([cmd])
            _LOGGER.debug("Sending %s", data.hex())
            await self.serial.write(data)
        finally:
            await self.serial.close()

    async def __process(self, cmd: int):
        await self.serial_lock.acquire()
        try:
            await asyncio.wait_for(self.__worker(cmd), _TIMEOUT)
        finally:
            self.serial_lock.release()

    async def set(self, card: int, relay: int):
        """Set `relay` of `card`."""
        _LOGGER.info("Switch on card %i relay %i", card, relay)
        if not 0 < relay < 21:
            raise Exception("invalid relay number")

        await self.__process(relay & 255)

    async def clear(self, card: int, relay: int):
        """Clear `relay` of `card`."""
        _LOGGER.info("Switch off card %i relay %i", card, relay)
        if not 0 < relay < 21:
            raise Exception("invalid relay number")

        await self.__process((relay + 20) & 255)
