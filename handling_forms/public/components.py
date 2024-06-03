from zenaura.client.component import Component
from public.presentational import UserForm

class UserFormComponent(Component):
    def __init__(self, instance_name):
        super().__init__()
        self.instance_name = instance_name
        self.state = {

                "name": "",

                "email": "",

                "message": ""

            }

    def update_state(self, field, value):

        self.state[field] = value
        
    def submit_form(self):

        print("Form submitted with:", self.state)
    def handle_input(self, event):
        field = event.target.name
        value = event.target.value
        self.update_state(field, value)
        print(self.state)


    def handle_submit(self, event):
        event.preventDefault()
        self.submit_form()

    def render(self):
        return UserForm(f"{self.instance_name}.handle_submit",f"{self.instance_name}.handle_input")