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

available_commands = {
    "PING": ping,
    "ECHO": echo,
}

# TODO 
async def parse(reader: asyncio.StreamReader):
    type = (await reader.readexactly(1)).decode('ascii')
    if type == "*":  # arrayT
        print("parsing RESP array...")
        # Extract the number of elements.
        # Call your parser recursively for each element.
        # Collect the returned values into a Python list.
        pass 
    if type == "$":  # bulk string
        print("parsing RESP bulk string")
        #   Extract the byte length.
        string_length = (await reader.readuntil(b"\r\n"))[:-2].decode('utf-8')
        if not string_length.isdigit():
            print("ERROR: did not detect bulk string size in header")
            return ''
        #   Read exactly that many bytes.
        string = (await reader.readexactly(int(string_length))).decode('utf-8') 
        print("reading bulk string: " + string)
        #   Consume the trailing 2-byte CRLF.
        await(reader.readexactly(2))
        #   Return the string.
        return string

async def handle_client(reader, writer):
    while True:
        print("listening for message....")
        message = (await parse(reader)).split(" ")

        command, args = message[0], message[1:]
        print("Command is: " + repr(command))

        if command in available_commands:
            writer.write(available_commands[command](args))
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
