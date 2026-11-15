import socket  # noqa: F401
import asyncio


async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break

        writer.write(b"+PONG\r\n")
        await writer.drain()

async def main():
    server = await asyncio.start_server(
        handle_client, "localhost", 6379
    )

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
