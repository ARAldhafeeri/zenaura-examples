from zenaura.client.component import Component
from zenaura.client.mutator import mutator 
from public.presentational import * 
import requests
def DataDisplayComponent(data):
    return Div("data-dict", [
            Div("item", [Paragraph(key), Paragraph(str(value))])
            for key, value in data.items()
        ])

class DataFetcher(Component):
    def __init__(self):
        super().__init__()
        self.state = {"data": None, "error": None}  # Initial state

    async def fetch_data(self):
        try:
            api_url = 'https://randomuser.me/api/'  # Your API endpoint
            response = requests.get(api_url)
            if response.ok:
                self.state["data"] = response.json()
            else:
                self.state["error"] = "API request failed"
        except Exception as e:
            self.state["error"] = str(e)

    @mutator
    async def attached(self):
        await self.fetch_data()
        print(self.state["data"])


    def render(self):
        if self.state["error"]:
            return ErrorComponent(error=self.state["error"])
        elif self.state["data"]:
            return DataDisplayComponent(data=self.state["data"])
        else:
            return LoadingComponent()  

"""
{'results': [{'gender': 'male', 'name': {'title': 'Mr', 'first': 'Charles', 'last': 'Clark'}, 'location': {'street': {'number': 5328, 'name': 'Vimy St'}, 'city': 'Grand Falls', 'state': 'Nunavut', 'country': 'Canada', 'postcode': 'Z1S 2U2', 'coordinates': {'latitude': '-69.8976', 'longitude': '-134.5780'}, 'timezone': {'offset': '-6:00', 'description': 'Central Time (US & Canada), Mexico City'}}, 'email': 'charles.clark@example.com', 'login': {'uuid': '3338f687-3461-4a72-88e9-33eb19c9077d', 'username': 'tinymeercat320', 'password': 'kang', 'salt': 'mrAgPCkY', 'md5': '1e1006b14c2e083026c86c129be8c0b8', 'sha1': 'e29949ab4b75c8fa07b79312098e28edb7e10e27', 'sha256': 'e3f3e1ffcf4e73ece750f437f70ac840a941b154e002a5d7327ee84111f59230'}, 'dob': {'date': '1957-01-26T13:12:12.937Z', 'age': 67}, 'registered': {'date': '2020-10-19T19:29:09.124Z', 'age': 3}, 'phone': 'C57 P04-4851', 'cell': 'R98 P02-7749', 'id': {'name': 'SIN', 'value': '389514100'}, 'picture': {'large': 'https://randomuser.me/api/portraits/men/70.jpg', 'medium': 'https://randomuser.me/api/portraits/med/men/70.jpg', 'thumbnail': 'https://randomuser.me/api/portraits/thumb/men/70.jpg'}, 'nat': 'CA'}], 'info': {'seed': '61b28009e82e3240', 'results': 1, 'page': 1, 'version': '1.4'}}

"""