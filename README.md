# DJI Tello Color Tracking Demo

A color tracker for the DJI/Ryze Tello based on telloCV with added functionalities like 3D movement, adaptive color tracking, color switching and other controllable parameters. Intended to use with a round object of medium size, currently set up for a balloon on a stick. The size of the object is relevant for the movement of the drone since the radius of the enclosing circle is used to move the drone closer to or further away from the object.

## Usage

### Installation

Requirements:
*Python 3.6; 
DJITelloPy 1.5; 
OpenCV 4.0; 
PyGame 1.9.4; 
NumPy 1.16.1;*
(should work with other versions as well)

Clone repo and install the necessary requirements via pip:

```
$ git clone http://git.mistlab.ca/moritz/tello-tracking-demo.git
$ cd tello-tracking-demo
$ pip install requirements.txt
```

### Controls

The drone is controlled by the keyboard:

| Keys			  | Commands |
|-----------------|--------|
|**Tab** 		  | Takeoff |
|**Shift** 		  | Land |
|**Space**		  | Emergency Shutdown |
|**W,A,S,D**	  | Forward, backward, left and right |
|**Q** and **E**  | Counter clockwise and clockwise rotations |
|**R** and **F**  | Up and down |
|**T**			  | Start/Stop tracking |
|**C**			  | Select central pixel value as new color for tracking |
|**\#**  		  | Switch controllable parameter |
|**\+** and **-** | Raise or lower controllable parameter |

When pressing any button (except the ones related to the controllable parameters), the tracking is automatically stopped and needs to be activated again manually (**T**).

### Suggestions for the usage

Turn on the Tello and connect to it. Then start program:

```
$ python3 tellotracker.py
```

Now take the Drone and point the camera towards the object or color you'd like it to follow. Then start tracking (**T**) and press **C** to select the color of the central pixel as init value for the tracking. While doing so, make sure that you select a suiting color (**\#**, then **+** or **-**) from the controllable parameters. This method ensures that that the color to track stays in a useful range. After these steps, turn off the tracking again (**T**) and place the drone somewhere for takeoff. When the takeoff (**Tab**) was successful and the object with the desired color is in the field of view of the camera, start tracking (**T**) & have fun.

## References

Based on the TelloCV implementation from:
https://github.com/Ubotica/telloCV/
