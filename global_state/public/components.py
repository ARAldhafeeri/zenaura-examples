import asyncio
from zenaura.client.component import Component
from public.presentational import * 
from zenaura.client.observer import Observer, Subject
from zenaura.client.dom import zenaura_dom
from zenaura.client.component import Component, Reuseable
from public.presentational import Div, Header1, Paragraph, CounterPresntaional, Button

# Create the subject
counter_subject = Subject()
counter_subject.state = {"counter1": 0, "counter2": 0, "counter3": 0, "counter4": 0}


# create counter observer:
class CounterObserver(Observer):
    pass

@Reuseable
class Counter(Component, CounterObserver):
    def __init__(self, subject, counter_name):
        super().__init__()
        self.subject = subject
        self.subject.attach(self)
        self.counter_name = counter_name
    
    async def increment(self, event):
        self.subject.state[self.counter_name] += 1
        await zenaura_dom.render(self)
        self.subject.notify()

    def update(self, value):
        if self.subject.state["counter1"] == 5:
            for k in self.subject.state.keys():
                self.subject.state[k] = 0
        asyncio.get_event_loop().run_until_complete(zenaura_dom.render(self))

    def render(self):
        return Div("container", [
            CounterPresntaional(
                Button("btn", "Increment", f"{self.counter_name}.increment"),
                Header1(f"count {self.subject.state[self.counter_name]}"),
                self.subject.state[self.counter_name],
                
            )
        ])
