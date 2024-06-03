from zenaura.client.tags.builder import Builder

def Div(class_name, children):
    div = Builder('div').with_attribute('class', class_name).build()
    div.children = children
    return div

def Label(text):
    return Builder('label').with_text(text).build()

def Input(type, name, oninput):
    return Builder('input').with_attributes(
        type=type,
        name=name,
    ).with_attribute(
        "py-change", oninput
    ).build()

def TextArea(name, oninput):
    return Builder('textarea').with_attributes(
        name=name,
    ).with_attribute(
        "py-change", oninput
    ).build()

def Button(type, text):
    return Builder('button').with_attributes(
        type=type
    ).with_text(text).build()

def UserForm(onsubmit, handle_input):
    return Builder('form').with_attribute(
        "py-submit", onsubmit
    ).with_children(
        Div('form-group', [
            Label("Name:"),
            Input("text", "name", handle_input),
            Label("Email:"),
            Input("email", "email", handle_input),

            Label("Message:"),
            TextArea("message", handle_input),
            Button("submit", "Submit")
        ])
    ).build()