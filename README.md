# Smart Parking AI MVP

## Overview

Smart Parking AI is an intelligent system designed to monitor parking lots in real time, detect vehicle presence, track slot availability, and provide live updates and analytics. The MVP leverages computer vision and AI to deliver accurate, robust, and user-friendly parking management.

## Features

- **Real-Time Vehicle Detection:** Detects vehicle presence and slot occupancy using camera/video input.
- **Slot Availability Monitoring:** Instantly updates the status (occupied/vacant) of each parking slot.
- **Parking Duration Tracking:** Records entry/exit times and calculates duration per slot.
- **Live Dashboard:** Visualizes slot status, durations, and provides intuitive color-coded feedback.
- **Data Persistence:** Stores historical and real-time data for analysis and recovery.
- **Performance Optimized:** Low-latency, stable processing for multiple slots and live streams.
- **Extensible Architecture:** Modular design for easy enhancements and deployment.

## MVP Scope

1. **Detect Vehicle Presence & Slot Availability in Real Time**
2. **Real-Time Notifications of Slot Availability**
3. **Track Parking Duration**

## Outcomes

- Accurate, real-time vehicle and slot detection
- Stable, low-latency live processing
- Reliable parking duration tracking
- Robust backend data management
- Intuitive, responsive dashboard
- Deployment-ready MVP

## Getting Started

### Prerequisites

- Python 3.8+
- OpenCV, NumPy, and other dependencies (see `requirements.txt`)
- Camera or video input source

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Wangpos/parking.git
   cd parking
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure camera/video source and slot regions in the config file.
4. Run the main application:
   ```bash
   python main.py
   ```

## Contributing

1. Fork the repository and create your branch (`git checkout -b feature/your-feature`)
2. Commit your changes (`git commit -am 'Add new feature'`)
3. Push to the branch (`git push origin feature/your-feature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License.

## Authors & Acknowledgments

- Project by eDruk-CST-Intern
- Special thanks to all contributors and collaborators.

## Contact

For questions or support, please open an issue or contact the maintainers.