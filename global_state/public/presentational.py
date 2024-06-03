from zenaura.client.tags.builder import Builder
from zenaura.client.tags.node import Node, Attribute
    
def Header1(text):
    return Builder('h1').with_text(text).build()

def Paragraph(text, class_name=None):
    builder = Builder('p').with_text(text)
    if class_name:
        builder = builder.with_attribute('class', class_name)
    return builder.build()

def Div(class_name, children):
    div = Builder('div').with_attribute('class', class_name).build()
    div.children = children
    return div

def Button(class_name, text, onclick_handler=None, name=None):
    builder = Builder('button').with_attribute('class', class_name).with_text(text)
    if onclick_handler:
        builder = builder.with_attribute('py-click', onclick_handler)
    if name:
        builder = builder.with_attribute("name", name)
    return builder.build()

def CounterPresntaional(increaseBtn, headertext, count) -> Node:
    return Builder("div") \
        .with_attribute("id", "large-header") \
        .with_children(
            headertext,
            increaseBtn
        ).build()
