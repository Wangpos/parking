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

## How to Run after the installation is complete:

```bash
# Activate environment
source env/bin/activate  
# Run the main detection system
./env/bin/python <your_script.py> # Replace <your_script.py> with the main file that you want to run
```

## Installtion Instructions

If you wnat to install the required packages manually, into the environment, you can use the following commands:

The first step is activating the environment and use it.
In MAC OS it is command shift p and then select the Python: Select Interpreter option and select the environment you created.

Then use the following commands to install the required packages:
```bash
# activate environment
source env/bin/activate
# install opencv
pip install opencv-python
# install ultralytics
pip install ultralytics
# and so on for other packages if needed
```
