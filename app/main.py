import socket  # noqa: F401
import asyncio


def ping(args: list[str]):
    if len(args) != 0:
        return b"PING: expected no argument\n"
    
    return b"+PONG\r\n"

def echo (args: list[str]):
    if len(args) != 1:
        return b"ECHO: expected 1 argument\n"

    return b""

commands = {
    "PING": ping,
    "ECHO": echo,
}

# TODO 
def parse(reader: asyncio.StreamReader):
    data = reader.readuntil(b"\r\n")
    if data[0] == "*":  # array
        # Extract the number of elements.
        # Call your parser recursively for each element.
        # Collect the returned values into a Python list.
        pass 
    if data[0] == "$":  # bulk string
        #   Extract the byte length.
        #   Read exactly that many bytes.
        #   Consume the trailing 2-byte CRLF.
        #   Return the string.
        pass

async def handle_client(reader, writer):
    while True:
        command, args = await parse(reader)

        if command in commands:
            writer.write(commands[command](args))
        else:
            writer.write(b"Unidentified command\n")
        
        await writer.drain()

async def main():
    server = await asyncio.start_server(
        handle_client, "localhost", 6379
    )

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
