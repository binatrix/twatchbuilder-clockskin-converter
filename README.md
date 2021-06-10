# twatchbuilder-clockskin-converter
On the Internet there are several formats to build watch faces. One of them is the XML-based "ClockSkin" format used by various Android clocks.

This is a Python script to convert XML ClockSkin files into TWatchBuilder C ++ code.

## Requirements
To run the script you need to install these modules:

- pip installation pillow
- pip install elementpath

## Use
To use it you must follow these steps:
- Download a watch face with "ClockSkin" format. The site "coolwatchfaces.com" has several models in its "Android" section.
- Modify the Python script to invoke the "process" function with these parameters:
	- The path of the ZIP file downloaded from the watch or the folder of the unzipped files
	- The unique prefix for the clock (to differentiate between projects)
	- A flag to indicate if the first image is used as a fixed or moving background (in most cases it should be "True")
	- Optional, a width for the clock (in most cases ignore it)
- Run the script

If all are successful, the script will generate a ZIP artifact called "xxxxx_twatchbuilder.zip". This file contains:
- "icon.png" file, the clock icon
- "twatch.cpp", the code of the watch
- "assets" folder, including all PNG images needed for the watch face

## Create your Watch
Now, you can create a watch with this ZIP artifact in TWatchBuilder.com:
- First, create a new application on the site.
- Name the application and save it
- Upload the ZIP file and wait for it to complete
- Compile the watch
- Try it on your TWatch2020 watch

Good look !!
