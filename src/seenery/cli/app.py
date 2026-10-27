import webbrowser
from datetime import datetime, timedelta

import typer
from rich.console import Console

app = typer.Typer(help="seenery CLI")
console = Console()


@app.command()
def version() -> None:
    """Print the current version."""
    from seenery import __version__

    console.print(__version__)


@app.command()
def photos(
    days: int = typer.Option(30, min=1, help="Report on photos from the last N days."),
    open_browser: bool = typer.Option(
        True, "--open-browser/--no-open-browser", help="Open auth and picker URLs in a browser."
    ),
) -> None:
    """Report per-day photo counts for the last N days via the Google Photos Picker API."""
    from seenery.config import SETTINGS
    from seenery.photos.auth import load_access_token
    from seenery.photos.picker import PickerClient
    from seenery.photos.report import build_daily_report

    try:
        token = load_access_token(
            SETTINGS.google_client_secrets_file,
            SETTINGS.google_token_file,
            open_browser=open_browser,
        )
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    client = PickerClient.from_token(token, timeout=SETTINGS.request_timeout)
    try:
        session = client.create_session()
        try:
            console.print(
                f"Select your photos from the last {days} days in Google Photos:\n"
                f"  {session.picker_uri}"
            )
            if open_browser:
                webbrowser.open(session.picker_uri)
            with console.status("Waiting for you to finish picking..."):
                client.wait_until_picked(session)
            items = list(client.list_media_items(session.id))
        finally:
            client.delete_session(session.id)
    finally:
        client.close()

    now = datetime.now().astimezone()
    report = build_daily_report(items, since=now - timedelta(days=days))
    if not report:
        console.print(f"No photos from the last {days} days were selected.")
        return

    for summary in report:
        console.print(f"[bold]{summary.day.isoformat()}[/bold]")
        console.print(f"Number of photos: {summary.photo_count}")
        # The Google Photos APIs strip GPS data from both metadata and downloads.
        name = summary.first_photo.media_file.filename if summary.first_photo.media_file else ""
        console.print(f"Location: unavailable (first photo: {name or summary.first_photo.id})")
