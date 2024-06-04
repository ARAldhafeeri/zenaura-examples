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

def Paragraph(text):
    return Builder('p').with_text(text).build()

def Spinner(text):
    return Div("spinner-container", [
            Header1(text),
        ]
    )

def LoadingComponent():
    """Displays a loading indicator while data is being fetched."""
    return Div("loading", [
        Spinner("spinner"),  # Replace 'Spinner' with your actual spinner component
        Paragraph("Loading data...")
    ])

def ErrorComponent(error):
    """Displays an error message when data fetching fails."""
    return Div("error", [
        Image("./public/error.png", "error", "45", "45"),
        Header1("Error Fetching Data"),
        Paragraph(error)
    ])