import logging
import aiohttp


async def on_request_start(session, trace_config_ctx, params):
    logging.info("HTTP START [%r], [%r]", session, params)


def http_debug():
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    return trace_config
