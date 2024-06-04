from zenaura.client.app import Route, App
from zenaura.client.page import Page
from public.routes import ClientRoutes
from public.components import DataFetcher
import asyncio


starter = DataFetcher()

# App and routing
router = App()
home_page = Page([starter])

router.add_route(Route(
    title="Developer-Focused | Zenaura",
    path=ClientRoutes.home.value,
    page=home_page
))

# Run the application
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(router.handle_location())

