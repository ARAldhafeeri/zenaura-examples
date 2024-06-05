from zenaura.client.tags.builder import Builder

def Div(class_name, children):
    div = Builder('div').with_attribute('class', class_name).build()
    div.children = children
    return div

def Image(src, alt, width, height, classname=""):
    return Builder("img").with_attributes(
        src=src,
        alt=alt,
        width=width,
        height=height,
    ).with_attribute("class", classname).build()

def Header1(text):
    return Builder('h1').with_text(text).build()

def Button(class_name, text, onclick_handler=None, name=None):
    builder = Builder('button').with_attribute('class', class_name).with_text(text)
    if onclick_handler:
        builder = builder.with_attribute('py-click', onclick_handler)
    if name:
        builder = builder.with_attribute("name", name)
    return builder.build()