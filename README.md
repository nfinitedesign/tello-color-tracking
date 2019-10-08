# DJI Tello Color Tracking Demo

A color tracker for the *DJI/Ryze Tello* based on [telloCV](https://github.com/Ubotica/telloCV/) with added functionalities like 3D movement, adaptive color tracking, color switching and other controllable parameters. Intended to be used with a round object of medium size, currently set up for a **balloon on a stick**. The size of the object is relevant for the movement of the drone since the radius of the enclosing circle is used to move the drone closer to or further away from the object.

Demo video of the program controlling the drone to keep a blue ballon, that is moved by a robotic arm, in sight and at a certain distance:

![Tracking a Blue Balloon on a Robot Arm.](robotarmdemo.gif)

\* Robot controls are not included. Video from [MIST Lab](https://mistlab.ca/) ([Twitter](https://twitter.com/mist_lab)).

## Usage

### Installation

Requirements (should work with other versions as well):
- Python 3.6;
- DJITelloPy 1.5;
- OpenCV 4.0;
- PyGame 1.9.4;
- NumPy 1.16.1;


Clone repo and install the necessary requirements via pip:

```
$ git clone https://github.com/nfinitedesign/tello-color-tracking.git
$ cd tello-tracking-demo
$ pip install requirements.txt
```

### Controls ###

The drone is controlled by the keyboard:

| Keys			  | Commands |
|-----------------|--------|
|**Tab** 		  | Takeoff |
|**Shift** 		  | Land |
|**Space**		  | Emergency Shutdown |
|**W,S,A,D**	  | Forward, backward, left and right |
|**Q** and **E**  | Counter clockwise and clockwise rotations |
|**R** and **F**  | Up and down |
|**T**			  | Start/Stop tracking |
|**C**			  | Select central pixel value as new color for tracking |
|**\#**  		  | Switch controllable parameter |
|**\+** and **-** | Raise or lower controllable parameter |

When pressing any button (except the ones related to the controllable parameters), the tracking is automatically stopped and needs to be manually activated again (**T**).

### Starting the Tracker ###

Turn on *Tello* and connect to it's WiFi, then run the script:

```
$ python tellotracker.py
```

The tracking should work out-of-the-box with the provided values for the colors under some conditions. However, to insure a more stable tracking right from the start it is advisable to define the color to be tracked before flight. Therefore, take the connected drone and point the camera towards the object with the color you'd like it to follow. Then start tracking (**T**) and press **C** to select the color of the central pixel as initial value for the tracking. While doing so, make sure that you select a suiting color (**\#**, then **+** or **-**) from the controllable parameters. This method ensures that that the color used for tracking stays in a certain range. After these steps, turn off the tracking again (**T**) and place the drone somewhere for takeoff. When the takeoff (**Tab**) was successful and the object with the desired color is in the field of view of the camera, start tracking (**T**) & have fun with it.

Keep in mind that tracking might fail for certain reasons, e.g. if the background contains objects of the same color. Therefore, always be ready to intervene if the tracking or the drone behaves unexpectedly.

## References ###

Based on the TelloCV implementation from:
https://github.com/Ubotica/telloCV/
