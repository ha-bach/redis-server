import socket  # noqa: F401
import asyncio


# SERVER EXCEPTIONS

class ClientDisconnected(Exception):
    pass


class ProtocolError(Exception):
    pass

# SERVER COMMANDS

def ping(args: list[bytes]):
    if len(args) != 0:
        return b"PING: expected no argument\n"
    
    return b"+PONG\r\n"

def echo (args: list[bytes]):
    if len(args) != 1:
        return b"PING: expected 1 argument\n"
    message = args[0]
    return b"$" + str(len(message)).encode("ascii") + b"\r\n" + message + b"\r\n"

available_commands = {
    "PING": ping,
    "ECHO": echo,
}

# TODO 
async def parse(reader: asyncio.StreamReader):
    try:
        type = (await reader.readexactly(1))
    except asyncio.IncompleteReadError as e:
        if len(e.partial) == 0: # client closed connection
            raise ClientDisconnected()
        
    type = type.decode('ascii')

    if type == "*":  # array
        print("parsing RESP array...")
        # Extract the number of elements.
        array_length = (await reader.readuntil(b"\r\n"))[:-2].decode('utf-8')
        if not array_length.isdigit():
            raise ProtocolError("Did not see size in array header")
        # Parse each element in the array
        message = []
        for i in range(int(array_length)):
            message.append(await parse(reader))

        return message
     
    if type == "$":  # bulk string
        print("parsing RESP bulk string")
        #   Extract the byte length.
        string_length = (await reader.readuntil(b"\r\n"))[:-2].decode('utf-8')
        if not string_length.isdigit():
            raise ProtocolError("Did not see size in bulk string header.")
        
        #   Read exactly that many bytes.
        string = await reader.readexactly(int(string_length))
        print("reading bulk string: " + repr(string))

        #   Consume the trailing 2-byte CRLF.
        crlf = await(reader.readexactly(2))
        if crlf.decode('utf-8') != "\r\n":
            raise ProtocolError("Did not see expected CRLF.")
        
        return string

    else:
        raise ProtocolError("Invalid RESP2 prefix.")

async def handle_client(reader, writer):
    try:
        while True:
            print("listening for message....")
            message = (await parse(reader))

            command, args = message[0].decode('utf-8'), message[1:]
            print("Command: " + repr(command))
            print("Arguments: " + repr(args))

            if command in available_commands:
                writer.write(available_commands[command](args))
            else:
                writer.write(b"Unidentified command\n")
            
            await writer.drain()
    except ClientDisconnected:
        print("Client disconnected.")

    except ProtocolError as e:
        print(f"Protocol error: {e}")
        print("Closing connection.")

    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, "localhost", 6379
    )

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
