import socket

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import typer
import uvicorn

# Import the updated generic generator
from ross2.slam.vision_pi import stream_local_frames

app = typer.Typer()
server_app = FastAPI(title="ROSS2 Tunnel Mapping Prototype")


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


@server_app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# ---------------------------------------------------------
# ENDPOINT 1: The fast, raw navigation stream
# ---------------------------------------------------------
@server_app.get("/live")
async def live_feed():
    return StreamingResponse(
        stream_local_frames(camera_index=-1, enable_detection=False),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# ---------------------------------------------------------
# ENDPOINT 2: Cascade Face Detector
# ---------------------------------------------------------
@server_app.get("/cascade")
async def human_detection_feed():
    return StreamingResponse(
        stream_local_frames(camera_index=-1, enable_detection=True, model="cascade"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
# ---------------------------------------------------------
# ENDPOINT 3: HOG Human Detection
# ---------------------------------------------------------
@server_app.get("/hog")
async def human_detection_feed():
    return StreamingResponse(
        stream_local_frames(camera_index=-1, enable_detection=True, model="hog"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@app.command(name="stream_pi")
def stream_server(port: int = 8080):
    active_ip = get_local_ip()

    typer.echo("\n🚀 Server starting!")

    if active_ip != "127.0.0.1":
        typer.echo(f"  Raw Video Stream:       http://{active_ip}:{port}/live")
        typer.echo(f"  Detection Stream:       http://{active_ip}:{port}/cascade")
        typer.echo(f"  Detection Stream:       http://{active_ip}:{port}/hog ")        
    else:
        typer.echo(f"  Raw Video Stream:       http://localhost:{port}/live")
        typer.echo(f"  Detection Stream:       http://{active_ip}:{port}/cascade")
        typer.echo(f"  Detection Stream:       http://{active_ip}:{port}/hog")   
    typer.echo("")
    uvicorn.run(server_app, host="0.0.0.0", port=port)
