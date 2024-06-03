from zenaura.client.app import App, Route
from zenaura.client.page import Page
from public.components import Counter, counter_subject
import asyncio

# Create counter components
counter1 = Counter(counter_subject, "counter1")
counter2 = Counter(counter_subject, "counter2")
counter3 = Counter(counter_subject, "counter3")
counter4 = Counter(counter_subject, "counter4")

print(counter1.id != counter2.id != counter3.id != counter4.id)
router = App()
router.add_route(
    Route(
        "Home", 
        "/",
        Page(
            [counter1, counter2, counter3, counter4]
       ) 
    )
)


# Run the application
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(router.handle_location())