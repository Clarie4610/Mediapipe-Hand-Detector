# Mediapipe-Hand-Detector

- Made in PyCharm Project Ver. 2021.1.3. (Warning:Newer versions do not work)
- Python Version: 3.7.0
***
-This program is for capturing hand wrist XY coordinates, depth and measured time by using depth camera "RealSense d435i"

-The program is running in 30FPS so it is gathering coodinates and depth in every about 0.033 seconds.

-However there's a certain point where the depth can not be measured and recorded as 0. So I made it measured in the range of 30px x 30px centered on the wrist coordinates.

-After measuring them I deleted the 0 ones and recorded the median of the numbers.

-Finally all the datas are combined and output as a csv file.
