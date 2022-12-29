from quart import Quart
from quart_cors import cors
from discord.ext.ipc import Client

app = Quart(__name__)
app = cors(app, allow_origin="*")
ipc = Client(secret_key="🐼")

@app.route('/commands')
async def commands():
    resp = await ipc.request("list_commands")
    return resp.response

if __name__ == '__main__':
    app.run()
