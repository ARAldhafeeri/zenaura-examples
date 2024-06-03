from zenaura.client.component import Component, Reuseable
from zenaura.client.tags.node import Node, Attribute
from zenaura.client.app import Route, App 
from public.routes import ClientRoutes
from dataclasses import dataclass
from functools import cache
from zenaura.client.mutator import mutator
from zenaura.client.tags.builder import Builder
from zenaura.client.page import Page
import asyncio 
import json




@dataclass
class CounterState:
	count: int
@dataclass
class CounterStyles:
    btn: str
    container: str
    container2: str
    h1: str
    controls: str
    main_container: str



STYLES = CounterStyles(
	btn="button-13", 
	h1="self-center text-xl font-semibold whitespace-nowrap dark:text-white",
	container= "card",
	controls = "flex flex-row",
    container2="logoContainer",
    main_container="mainContainer"
)

def Button( label_text : str, onclick_handler : str, id=None) -> Node:
    btn = Node(name="button")
    btn.attributes.append(Attribute(key="styles", value=STYLES.btn))
    if id:
        btn.attributes.append(Attribute(key="id", value=id))
    else:
        btn.attributes.append(Attribute(key="py-click", value=onclick_handler))

    btn.append_child(Node(name="label", children=[label_text]))
    return btn

def DomContainer() -> Node:
    virtualDom = Node(name="div")
    virtualDom.attributes = [
        Attribute(key="id", value="virtualDom"),
    ]

    virtualDom.children = [
        Node(name="svg")
    ]

    realDom = Node(name="div")
    realDom.attributes = [
        Attribute(key="id", value="realDom"),
    ]

    domContainer = Node(name="div")
    domContainer.attributes = [
        Attribute(key="styles", value=f"domContainer"),
    ]

    domContainer.children = [
        virtualDom,
        realDom,
    ]
    return domContainer

def Image(src : str) -> Node:
     return Node(
         name="img", 
         attributes=[
             Attribute(key="src", value=src), 
             Attribute("width", "100"), 
             Attribute("height", "200"),  
             Attribute(key="alt", value="logo")]
             )

class SimpleUi(Component):

    async def nvaigate(self, event):

        await router.navigate("/counter")

    def render(self):
        div = Node(name="div")
        div.attributes.append(
            Attribute("styles", "logoContainer")
        )
        btn = Node(name="button", children=["test"])
        btn.attributes = [
            Attribute("py-click", "simpleUi.nvaigate"),
            Attribute("styles", STYLES.btn),
            Attribute("id", "centered"),
        ]
        div.append_child(Image("public/logo.svg"))
        div.append_child(btn)
        return div



def CounterPresntaional(increaseBtn, decreaseBtn, headertext, count) -> Node:

    header = Builder('h1') \
    .with_child(
        headertext
    ).build()


    even = count % 2 == 0


    isEven = Builder('h2').with_child("even" if even else "odd").build()
    isEven2 = Builder('button').with_child("even" if even else "odd").build()

    condtionalAttr = Attribute("data-even", even) if even else Attribute("data-even", even)
    ctrl = Builder("div") \
        .with_attribute("styles", STYLES.controls) \
        .with_child(
            increaseBtn
        ).with_child(
            decreaseBtn
        ).build()

    return Builder("div") \
        .with_attribute("styles", STYLES.container) \
        .with_attribute(condtionalAttr.key, condtionalAttr.value ) \
        .with_attribute("id", "large-header") \
        .with_child(
            header 
        ).with_child(
           isEven
        ).with_child(
            isEven2 if even else Node("div")
        ).with_child(
            ctrl
    ).build()

@Reuseable
class Counter(Component):
    def __init__(self, dependencies):
        super().__init__()
        self.set_state({"count": 0})
        self.dependencies = dependencies  # If you need dependencies
        self.instance_name = dependencies["instance_name"]

    @mutator
    async def increment_counter1(self, event) -> None:
        self.set_state({"count": self.get_state()["count"] + 1})

    @mutator
    async def decrease_counter1(self, event) -> None:
        self.set_state({"count": self.get_state()["count"] - 1})


    def render(self) -> Node:
        return Builder("div") \
            .with_child(
                CounterPresntaional(  # Assuming you have this class
                    increaseBtn=Button("-", f"{self.instance_name}.decrease_counter1"),  # Note the change
                    decreaseBtn=Button("+", f"{self.instance_name}.increment_counter1"),  # Note the change
                    headertext=f"Count 1: {self.get_state()['count']}",
                    count=self.get_state()["count"]
                )
            ).build()


simpleUi = SimpleUi()

counter1 = Counter({"instance_name": "counter1"})
counter2 = Counter({"instance_name": "counter2"})
# # app 


# app 
router = App() 
simple_ui_page = Page([simpleUi])
counters_page = Page([counter1, counter2])
router.add_route(Route(
        title="test",
        path=ClientRoutes.home.value,
        page=simple_ui_page
    ))

router.add_route(Route(
		title="counter",
		path=ClientRoutes.counter.value,
		page=counters_page
    ))

router.add_route(Route(
		title="ssr",
		path=ClientRoutes.ssr.value,
		page=counters_page,
        ssr=True
    ))

event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(router.handle_location())