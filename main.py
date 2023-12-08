import asyncio
from machine import Pin, Signal
import socket
import time


class State:
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


class ToldoServer:
    MAX_TIME = 20

    def __init__(self):
        self.state = State.IDLE
        self.start_time = -1
        self.p_up = Signal(22, Pin.OUT, invert=True, value=0)
        self.p_down = Signal(23, Pin.OUT, invert=True, value=0)

    def handle_request(self, reader, writer):
            data = await reader.read(16)
            cmd = data.decode("utf-8").strip()

            # if we're in the middle of an operation, simply abort.
            if self.state != State.IDLE and cmd in ["up", "down"]:
                self.state = State.IDLE
                asyncio.sleep(2)
            elif cmd == "up":
                self.state = State.UP
                self.start_time = time.time()
            elif cmd == "down":
                self.state = State.DOWN
                self.start_time = time.time()
            elif cmd == "status":
                pass
            else:
                self.state = State.IDLE

            writer.write(f"Status is: {self.state}\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def start(self):
        self.idle()
        server = await asyncio.start_server(self.handle_request, '0.0.0.0', 8888)
        while True:
            await asyncio.sleep(1)

    def idle(self):
        self.p_up.off()
        self.p_down.off()
        self.state = State.IDLE

    async def loop(self):
        while True:
            if time.time() - self.start_time < self.MAX_TIME and self.state == State.UP:
                self.p_up.on()
            elif time.time() - self.start_time < self.MAX_TIME and self.state == State.DOWN:
                self.p_down.on()
            else:
                self.idle()

            await asyncio.sleep(0.1)

    def run(self):
        asyncio.run(asyncio.gather(self.start(), self.loop()))

