from pathlib import Path

from simpleseg import SegmentationApp, validate_data

from example_data import DemoData

datasets: list[DemoData] = [
    DemoData(
        dataset_path=Path(r"example_data/bw-data"),
        name="bw demo data",
    ),
    DemoData(
        dataset_path=Path(r"example_data/rgb-data"),
        name="rgb demo data",
    ),
]

validate_data(datasets[0])

gui = SegmentationApp(datasets=datasets, n_classes=3)
