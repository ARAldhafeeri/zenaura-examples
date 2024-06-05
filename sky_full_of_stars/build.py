
from zenaura.server import ZenauraServer
from public.main import router

ZenauraServer.hydrate_app(router, scripts=[
        '<link rel="stylesheet" href="public/gigavolt.min.css">',
        '<script src="public/highlight.min.js"></script>',  
        '<script src="public/python.min.js"></script>',
        '<script>hljs.highlightAll();</script>',
        """
        <script>
            const ws = new WebSocket("ws://localhost:5000/refresh");
            ws.onmessage = () => {
            console.log("Reloading...");
            location.reload();
            };
        </script>
        """
])

