# twatchbuilder-clockskin-converter
On the internet there are several formats to build watchfaces. One of them is the XML based "ClockSkin" format used by various Android watches.

This is a Python script to convert ClockSkin XML files into TWatchBuilder C++ code.

## Requirements
To execute the script you need to install these modules:

- pip install pillow
- pip install elementpath

## Use
To use it you must follow these steps:
- Download a watchface with this format. The site "coolwatchfaces.com" has several models in its "Android" section.
- Unzip the downloaded file and ensure there is a "clock_skin.xml" file inside.
- Modify the Python script to invoke the "process" function with these params:
	- The path for the watch's downloaded files 
	- The unique prefix for the watch (to differentiate between projects) 
	- A flag to indicate if the first image is used as fixed or a moving background (in most cases this should be "True")
- Run the script

If all run ok, the script will generate 3 artifacts in a folder named "twatch" inside the watch folder: 
- "icon.png" file, the icon for the watch
- "twatch.cpp", the code for the watch
- "assets" folder, including all the PNG images required for the watchface

Then upload these artifacts to TWatchBuilder.com:
- Create a new app on the site
- Name the app and save it
- Upload the "icon.png" file into the "Icon" field and save it
- Copy the content of the "twatch.cpp" file into the "Code" field and save it
- Upload all the files inside the "assets" folder into the "Assets" field
- Compile the watch
- Try it on your TWatch2020 watch

This is still a work in progress!!!! 

Good look

