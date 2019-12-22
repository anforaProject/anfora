import asyncio
import asyncio.coroutines
import functools
import os
import sys
import threading
from concurrent.futures import Future, ThreadPoolExecutor
import contextvars

class SyncToAsync:
    """
    Utility class which turns a synchronous callable into an awaitable that
    runs in a threadpool. It also sets a threadlocal inside the thread so
    calls to AsyncToSync can escape it.
    If thread_sensitive is passed, the code will run in the same thread as any
    outer code. This is needed for underlying Python code that is not
    threadsafe (for example, code which handles SQLite database connections).
    If the outermost program is async (i.e. SyncToAsync is outermost), then
    this will be a dedicated single sub-thread that all sync code runs in,
    one after the other. If the outermost program is sync (i.e. AsyncToSync is
    outermost), this will just be the main thread. This is achieved by idling
    with a CurrentThreadExecutor while AsyncToSync is blocking its sync parent,
    rather than just blocking.
    """

    # If they've set ASGI_THREADS, update the default asyncio executor for now
    if "ASGI_THREADS" in os.environ:
        loop = asyncio.get_event_loop()
        loop.set_default_executor(
            ThreadPoolExecutor(max_workers=int(os.environ["ASGI_THREADS"]))
        )

    # Maps launched threads to the coroutines that spawned them
    launch_map = {}

    # Storage for main event loop references
    threadlocal = threading.local()

    # Single-thread executor for thread-sensitive code
    single_thread_executor = ThreadPoolExecutor(max_workers=1)

    def __init__(self, func, thread_sensitive=False):
        self.func = func
        self._thread_sensitive = thread_sensitive
        self._is_coroutine = asyncio.coroutines._is_coroutine
        try:
            self.__self__ = func.__self__
        except AttributeError:
            pass

    async def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()

        # Work out what thread to run the code in
        if self._thread_sensitive:
            if hasattr(AsyncToSync.executors, "current"):
                # If we have a parent sync thread above somewhere, use that
                executor = AsyncToSync.executors.current
            else:
                # Otherwise, we run it in a fixed single thread
                executor = self.single_thread_executor
        else:
            executor = None  # Use default

        if contextvars is not None:
            context = contextvars.copy_context()
            child = functools.partial(self.func, *args, **kwargs)
            func = context.run
            args = (child,)
            kwargs = {}
        else:
            func = self.func

        # Run the code in the right thread
        future = loop.run_in_executor(
            executor,
            functools.partial(
                self.thread_handler,
                loop,
                self.get_current_task(),
                sys.exc_info(),
                func,
                *args,
                **kwargs
            ),
        )
        return await asyncio.wait_for(future, timeout=None)

    def __get__(self, parent, objtype):
        """
        Include self for methods
        """
        return functools.partial(self.__call__, parent)

    def thread_handler(self, loop, source_task, exc_info, func, *args, **kwargs):
        """
        Wraps the sync application with exception handling.
        """
        # Set the threadlocal for AsyncToSync
        self.threadlocal.main_event_loop = loop
        # Set the task mapping (used for the locals module)
        current_thread = threading.current_thread()
        if AsyncToSync.launch_map.get(source_task) == current_thread:
            # Our parent task was launched from this same thread, so don't make
            # a launch map entry - let it shortcut over us! (and stop infinite loops)
            parent_set = False
        else:
            self.launch_map[current_thread] = source_task
            parent_set = True
        # Run the function
        try:
            # If we have an exception, run the function inside the except block
            # after raising it so exc_info is correctly populated.
            if exc_info[1]:
                try:
                    raise exc_info[1]
                except:
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        finally:
            # Only delete the launch_map parent if we set it, otherwise it is
            # from someone else.
            if parent_set:
                del self.launch_map[current_thread]

    @staticmethod
    def get_current_task():
        """
        Cross-version implementation of asyncio.current_task()
        Returns None if there is no task.
        """
        try:
            if hasattr(asyncio, "current_task"):
                # Python 3.7 and up
                return asyncio.current_task()
            else:
                # Python 3.6
                return asyncio.Task.current_task()
        except RuntimeError:
            return None


# Lowercase is more sensible for most things
sync_to_async = SyncToAsync