from flask import Flask, send_file, render_template
from public.main import counters_page, router
from public.routes import ClientRoutes
from zenaura.server import ZenauraServer
from zenaura.client.hydrator import HydratorCompilerAdapter
from zenaura.client.tags.node import Node
from zenaura.client.tags.attribute import Attribute
import io 

hyd = HydratorCompilerAdapter()
app = Flask(__name__,
            static_folder="public"
            )

@app.route(ClientRoutes.counter.value)
@app.route(ClientRoutes.home.value)
def root():
    return send_file('public/index.html')


@app.route('/ssr')
def ssr():    
    # Render the main HTML template with the rendered component
    return ZenauraServer.hydrate_page(counters_page)
    



if __name__ == "__main__":
    ZenauraServer.hydrate_app(router)
    app.run()