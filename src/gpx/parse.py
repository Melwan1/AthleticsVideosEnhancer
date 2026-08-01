from gpx.gpx import GPX
from pathlib import Path
import pprint
from xml.etree import ElementTree as ET
from datetime import datetime

class GPXParser:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def to_gpx(self) -> GPX:
        self.tree = ET.parse(self.file_path).getroot()
        ns = {"gpx": "http://www.topografix.com/GPX/1/1", "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1" }

        points = []
        for pt in self.tree.findall(".//gpx:trkpt", ns):
            point_time = pt.find(".//gpx:time", ns)
            elevation = pt.find(".//gpx:ele", ns)
            hr = pt.findtext(".//gpxtpx:hr", namespaces=ns)
            points.append({
                "lat": float(pt.get("lat", default = 0.0)),
                "lon": float(pt.get("lon", default = 0.0)),
                "time": None if point_time is None or point_time.text is None else datetime.fromisoformat(point_time.text),
                "elevation": None if elevation is None or elevation.text is None else int(float((elevation.text))),
                "hr": hr
            })
        gpx = GPX(points)
        return gpx
