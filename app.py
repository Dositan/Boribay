from quart import Quart, jsonify
from discord.ext.ipc import Client

app = Quart(__name__)
ipc = Client(secret_key="🐼")

@app.route('/info')
async def info():
    resp = await ipc.request("general_info")
    return jsonify(resp.data)

if __name__ == '__main__':
    app.run()
