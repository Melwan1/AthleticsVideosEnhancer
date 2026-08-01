from pathlib import Path
import click
from gpx.parse import GPXParser
import time

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file", type=Path)
def parse_gpx(file: Path):
    parser = GPXParser(file)
    gpx = parser.to_gpx()
    print(gpx.total_stats())
    for int_time in range(gpx.moving_time):
        print(" ", gpx.format_time(int_time), "  ", gpx.format_pace(gpx.get_pace_at(int_time)), "   ", gpx.format_distance(gpx.get_distance_at(int_time)), end="    \r")
        time.sleep(0.9997)

if __name__ == "__main__":
    cli()
