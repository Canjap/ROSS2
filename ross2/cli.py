import typer

from ross2.commands import stream

app = typer.Typer(help="ROSS2 — Remote Observation Scout Suite")

# Register the streaming subcommand package
app.add_typer(stream.app, help="Manage local video capture and live broadcasting feeds")

if __name__ == "__main__":
    app()
