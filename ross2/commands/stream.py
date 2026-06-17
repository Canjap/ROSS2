import typer
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from loguru import logger
from ross2.slam.vision import stream_local_annotated_frames

app = typer.Typer()
server_app = FastAPI(title="ROSS2 Tunnel Mapping Prototype")

@server_app.get("/live")
async def live_feed():
    """Streaming endpoint matching standard multipart HTTP standards."""
    return StreamingResponse(
        stream_local_annotated_frames(model=None, camera_index=0),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.command(name="stream")
def stream_server(port: int = 8080):
    """Launch the server to broadcast local camera footage."""
    logger.info(f"Spinning up streaming server on port {port}")
    typer.echo(f"\n Server starting: view  video stream at:")
    typer.echo(f" http://<your_raspberry_pi_ip>:{port}/live\n")
    
    uvicorn.run(server_app, host="127.0.0.1", port=port)