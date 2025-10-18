"""
PhantomGuard HTTP Honeypot
Minimal aiohttp server that logs all requests as events.
"""
import asyncio
from aiohttp import web
from typing import Callable


class EventLogger:
    def __init__(self, emit: Callable):
        self.emit = emit

    async def log_event(self, request):
        event = {
            'event_type': 'http_honeypot',
            'path': str(request.rel_url),
            'method': request.method,
            'headers': dict(request.headers),
            'remote': request.remote,
            'ts': request.time_service.now(),
        }
        self.emit(event)
        return web.Response(text='OK')


async def run_honeypot(emit: Callable, port: int = 8080):
    logger = EventLogger(emit)
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', logger.log_event)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[HTTP Honeypot] Listening on port {port}")
    while True:
        await asyncio.sleep(3600)
