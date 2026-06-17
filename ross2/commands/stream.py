import socket

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from loguru import logger
import typer
import uvicorn

from ross2.slam.vision import stream_local_annotated_frames

app = typer.Typer()
server_app = FastAPI(title="ROSS2 Tunnel Mapping Prototype")


def get_local_ip() -> str:
    """
    Triggers a dummy socket connection to detect the primary outbound network
    IP address actively used by the Pi (works for both Wi-Fi and Ethernet).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect or send traffic, just queries the OS routing table
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


@server_app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Mutes browser tab icon requests to clean up terminal logs."""
    return Response(status_code=204)


@server_app.get("/live")
async def live_feed():
    """Streaming endpoint matching standard multipart HTTP standards."""
    return StreamingResponse(
        stream_local_annotated_frames(model=None, camera_index=0),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.command(name="stream")
def stream_server(port: int = 8080):
    """Launch the server to broadcast camera footage over Wi-Fi or Ethernet."""
    # 1. Automatically fetch the active IP address assigned to the Pi
    active_ip = get_local_ip()

    logger.info(f"Spinning up streaming server on catch-all interface [0.0.0.0] on port {port}")

    typer.echo("\n🚀 Server starting!")
    typer.echo(f"  Local Loopback (Same Machine): http://localhost:{port}/live")

    if active_ip != "127.0.0.1":
        typer.echo(f"  Wired/Wireless Network Stream: http://{active_ip}:{port}/live")
    else:
        typer.echo(
            "  ⚠️ Warning: No active network interface detected. Plug in your cable or connect to Wi-Fi."
        )
    typer.echo("")

    # Keep host at 0.0.0.0 so it stays bound to all physical hardware interfaces
    uvicorn.run(server_app, host="0.0.0.0", port=port)
