# SimpleSeg

SimpleSeg is a GUI application written in Python for manual multiclass image segmentation. It is made for you, if you want a simple and easy to use solution to quickly review or edit your image segmentation masks locally on your machine.

# Features

- Easy installation and setup
- KISS (Keep it simple, stupid!)
- Supports BW (1-channel) and Colored (3-channel) images
- Supports up to 10 class labels

# Installation and Setup

### 1) Install Python package

After cloning this repository, `cd` into the directory. Then run these commands to install the package into your active python environment and to run the GUI with the example data. If you want to load your personal data, continue with step 2.

```bash
pip install -e .
```

Optional: Run SimpleSeg with example data:

```bash
python example_main.py
```

### 2) Create a wrapper for your data

To use your data with `SimpleSeg`, you need to create your own Subclass of `AbstractData` that that implements a few required methods within specifications. These are basic functions such as `get_image()` and `get_mask()`.

```python
from simpleseg import AbstractData

class ExampleData(AbstractData):
    def get_image(self, index: int):
        ...
```

The full interface that needs to be implemented is defined in [Link to AbstractData](src/simpleseg/data/dataclass.py). You can check if your dataclass satisfies the specifications with `validate_data()`.

```python
from simpleseg import validate_data

data = ExampleData(...)
validate_data(data)
```

Have a look at a fully working example implementation of `AbstractData` in [example_data.py](example_data.py)

### 3) Run simpleseg

Create a python script in which you create `SegmentationApp()` with your version of `ExampleData`.

```python
from simpleseg import SegmentationApp

dataset = ExampleData(...)
datasets = [dataset]  # add one or more datasets
SegmentationApp(datasets)
```

# Run tests

to execute tests, run

```bash
pytest
```
