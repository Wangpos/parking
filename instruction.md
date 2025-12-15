# Automatic-Number-Plate-Recognition-YOLOv8

## Demo

## Project Setup

- Make an environment with python=3.10 using the following command

```bash
conda create --prefix ./env python==3.10 -y
```

- Activate the environment

```bash
conda activate ./env
```

- Install the project dependencies using the following command

```bash
pip install -r requirements.txt
```

- Run main.py with the sample video file to generate the test.csv file

```python
python main.py
```

- Run the add_missing_data.py file for interpolation of values to match up for the missing frames and smooth output.

```python
python add_missing_data.py
```

- Finally run the visualize.py passing in the interpolated csv files and hence obtaining a smooth output for license plate detection.

```python
python visualize.py
```
