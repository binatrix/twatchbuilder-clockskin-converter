import xml.etree.ElementTree as ET
from PIL import Image
import os
import zipfile
import shutil

def get_size(image_path):
    with Image.open(image_path) as image:
        return image.size

def rename(prefix, name):
    name2 = name
    if name2[0] == "_":
        name2 = prefix + name2
    else:
        name2 = prefix + "_" + name2
    name2 = name2.replace(" ", "_")
    name2 = name2.replace("-", "_")
    name2 = name2.replace("_.", ".")
    return name2.lower()
    
def resize(scale, file_in, file_out):
    with Image.open(file_in) as image: #.convert('RGB')
        width, height = image.size
        new_width = (int)(width * scale)
        new_height = (int)(height * scale)
        if new_width == 0:
            new_width = 1
        if new_height == 0:
            new_height = 1
        new_image = image.resize((new_width, new_height))
        new_image.save(file_out)

def get_node_str(elem, tag, defval):
    node = elem.find(tag)
    if node == None:
        return defval
    return node.text

def get_node_int(elem, tag, defval):
    return int(get_node_str(elem, tag, defval))

def process(path, prefix, use_back, new_width = 0):
    ## if ZIP file, uncrompress ClockSkin
    is_zip = path[-4:] == ".zip"
    if is_zip:
        zip_file = path
        path = os.path.dirname(zip_file)
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(path)
        path = zip_file[:-4]

    if not os.path.exists(path + "\\clock_skin.xml"):
        raise Exception("This is not an ClockSkin file")
        
    ## convert ClockSkin
    path_watch = path + "\\twatch"
    if not os.path.exists(path_watch):
        os.makedirs(path_watch)
    path_asset = path_watch + "\\assets"
    if not os.path.exists(path_asset):
        os.makedirs(path_asset)

    f = open(path_watch + "\\twatch.cpp", "w")
    f.write("#include \"StandardClock.h\"\n\n")

    tree1 = ET.parse(path + "\\clock_skin.xml")
    root1 = tree1.getroot()
    i = 0
    images = []
    scale = 1

    width, height = get_size(path + "\\clock_skin_model.png")
    resize(72 / width, path + "\\clock_skin_model.png", path_watch + "\\icon.png")
    if new_width != 0:
        width = new_width
    scale = 240 / width
    
    for elem1 in root1:
        name = get_node_str(elem1, "name", "")
        arraytype = get_node_int(elem1, "arraytype", 0)
        centerX = get_node_int(elem1, "centerX", 0)
        centerY = get_node_int(elem1, "centerY", 0)
        rotate = get_node_int(elem1, "rotate", 0)
        mulrotate = get_node_int(elem1, "mulrotate", 0)
        direction = get_node_int(elem1, "direction", 0)
        x = round(centerX * scale)
        y = round(centerY * scale)
        i = i + 1

        if name != None and name != "":
            name1 = rename(prefix, name)
            name2 = name1[:-4]
            if ".xml" in name:
                tree2 = ET.parse(path + "\\" + name)
                root2 = tree2.getroot()
                buf1 = []
                buf2 = []
                for elem2 in root2:
                    image = elem2.text
                    name1 = rename(prefix, image)
                    name2 = name1[:-4]
                    f.write("LV_IMG_DECLARE(" + name2 + ");\n")
                    resize(scale, path + "\\" + image, path_asset + "\\" + name1)
                    buf1.append(name1)
                    buf2.append(name2)
                w0 = 0
                if arraytype == 2 or arraytype == 6:
                    if len(buf1) > 10:
                        # get colon image width
                        w0, height = get_size(path_asset + "\\" + buf1[10])
                # get digit image width
                w1, height = get_size(path_asset + "\\" + buf1[0])
                json = {"t" : arraytype, "x": x, "y": y, "r": rotate, "d": direction, "w0": w0, "w1": w1, "images": buf2}
                images.append(json)
                
            else:
                f.write("LV_IMG_DECLARE(" + name2 + ");\n")
                resize(scale, path + "\\" + name, path_asset + "\\" + name1)
                width, height = get_size(path_asset + "\\" + name1)
                json = {"t" : arraytype, "x": x, "y": y, "r": rotate, "d": direction, "w": width, "h": height, "image": name2}
                images.append(json)

    f.write("\n")
    i = 0
    for img1 in images:
        if img1["t"] != 0:
            f.write("const lv_img_dsc_t* __images_" + str(i) + "[] = {")
            buf = ""
            for img2 in img1["images"]:
                if buf != "":
                    buf = buf + ", "
                buf = buf + "&" + img2
            f.write(buf)
            f.write("};\n")
            i = i + 1
        
    i = 0
    j = 0
    k = 0
    buf = ""
    for img1 in images:
        if use_back and i == 0: # ignore first image for background
            i = i + 1
            continue
        
        if img1["t"] != 0:
            x = img1["x"]
            y = str(img1["y"])
            t = img1["t"]
            w0 = img1["w0"]
            w1 = img1["w1"]
            wx = round((w1 + w0) / 2)
            if t == 2: # monthday
                if len(img1["images"]) > 10: # separator
                    sep = img1["images"][10]
                    buf = buf + "\t__clock.add_clock_back(&" + sep + ", {" + str(x) + ", " + y + "});\n"
                x1 = x - wx
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MONTH_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 - w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MONTH_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x + wx
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_DAY_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_DAY_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 5
                
            elif t == 3: # month
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MONTH, __images_" + str(k) + ", {" + str(x) + ", " + y + "});\n"
                j = j + 1

            elif t == 4: # day
                x1 = x - round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_DAY_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_DAY_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 2
                
            elif t == 5: # weekday
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_WEEKDAY, __images_" + str(k) + ", {" + str(x) + ", " + y + "});\n"
                j = j + 1
                
            elif t == 6: # hour-minute
                if len(img1["images"]) > 10: # separator
                    sep = img1["images"][10]
                    buf = buf + "\t__clock.add_clock_back(&" + sep + ", {" + str(x) + ", " + y + "});\n"
                x1 = x - wx
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_HOUR_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 - w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_HOUR_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x + wx
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MINUTE_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MINUTE_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 5
                
            elif t == 7: # hour-array
                x1 = x - round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_HOUR_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_HOUR_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 2
                
            elif t == 8: # minute-array
                x1 = x - round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MINUTE_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_MINUTE_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 2

            elif t == 9: # second-array
                x1 = x - round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_SECOND_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_SECOND_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 2

            elif t == 10: # weather
                a = 1

            elif t == 11: # temp
                a = 1

            elif t == 12: # steps
                x1 = x - (3 * w1)
                if len(img1["images"]) > 10:
                    lead = img1["images"][10]
                    buf = buf + "\t__clock.add_clock_back(&" + lead + ", {" + str(x1) + ", " + y + "});\n"
                    j = j + 1
                    x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_STEPS_TEN_THOUSAND, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_STEPS_THOUSAND, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_STEPS_HUNDRED, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_STEPS_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_STEPS_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 5
                
            elif t == 14: # battery
                if len(img1["images"]) > 10:
                    x1 = x - w1
                    lead = img1["images"][10]
                    buf = buf + "\t__clock.add_clock_back(&" + lead + ", {" + str(x1) + ", " + y + "});\n"
                    j = j + 1
                x1 = x
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_BATTERY_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_BATTERY_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 2
                if len(img1["images"]) > 11:
                    x1 = x1 + w1
                    perc = img1["images"][11]
                    buf = buf + "\t__clock.add_clock_back(&" + perc + ", {" + str(x1) + ", " + y + "});\n"
                    j = j + 1

            elif t == 16: # year
                x1 = x - round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_YEAR_HUNDRED, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 - w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_YEAR_THOUSAND, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x + round(w1 / 2)
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_YEAR_TEN, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                x1 = x1 + w1
                buf = buf + "\t__clock.add_clock_sprite(TIME_RES_YEAR_UNIT, __images_" + str(k) + ", {" + str(x1) + ", " + y + "});\n"
                j = j + 4

            k = k + 1
                
        else: # single image
            x = img1["x"]
            y = img1["y"]
            r = img1["r"]
            d = img1["d"]
            w = img1["w"]
            h = img1["h"]
            x0 = round(w / 2)
            y0 = round(h / 2)
            if r == 1: # hour pointer
                buf = buf + "\t__clock.add_clock_hand(TIME_RES_HOUR, &" + img1["image"] + ", {" + str(x) + ", " + str(y) + "}, {" + str(x0) + ", " + str(y0) + "}, false);\n"
                j = j + 1
            elif r == 2: # minute pointer
                buf = buf + "\t__clock.add_clock_hand(TIME_RES_MINUTE, &" + img1["image"] + ", {" + str(x) + ", " + str(y) + "}, {" + str(x0) + ", " + str(y0) + "}, false);\n"
                j = j + 1
            elif r == 3: # second pointer
                buf = buf + "\t__clock.add_clock_hand(TIME_RES_SECOND, &" + img1["image"] + ", {" + str(x) + ", " + str(y) + "}, {" + str(x0) + ", " + str(y0) + "}, false);\n"
                j = j + 1
            elif r == 6: # battery pointer
                buf = buf + "\t__clock.add_clock_hand(TIME_RES_BATTERY, &" + img1["image"] + ", {" + str(x) + ", " + str(y) + "}, {" + str(x0) + ", " + str(y0) + "}, false, 0, 100";
                if d == 0:
                    buf = buf + ", 0, 30);\n"
                else:
                    buf = buf + ", -30, 0);\n"
                j = j + 1
            elif r == 10: # second pointer shadow
                buf = buf + "\t__clock.add_clock_hand(TIME_RES_SECOND, &" + img1["image"] + ", {" + str(x) + ", " + str(y) + "}, {" + str(x0) + ", " + str(y0) + "}, false);\n"
                j = j + 1
            else:
                buf = buf + "\t__clock.add_clock_back(&" + img1["image"] + ", {" + str(x) + ", " + str(y) + "});\n"
                j = j + 1
            
        i = i + 1

    f.write("\n")
    f.write("StandardClockSimple __clock;\n\n")
    f.write("void __show() {\n")
    if use_back:
        f.write("\t__clock.init(LV_COLOR_BLACK, &" + images[0]["image"] + ", " + str(j) + ");\n")
    else:
        f.write("\t__clock.init(LV_COLOR_BLACK, " + str(j) + ");\n")
    
    f.write(buf)

    f.write("\t__clock.show();\n")
    f.write("}\n")

    f.write("\n")
    f.write("void __hide() {\n")
    f.write("\t__clock.hide();\n")
    f.write("}\n")

    f.write("\n")
    f.write("void __loop () {\n")
    f.write("}\n")
    f.close()

    ## create output zip file
    zip_out = path + "_twatchbuilder.zip"
    if os.path.exists(zip_out):
        os.remove(zip_out)
    zf = zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED)
    for dirname, subdirs, files in os.walk(path_watch):
        length = len(path_watch)
        for filename in files:
            zf.write(os.path.join(dirname, filename), os.path.join(dirname[length:], filename))
    zf.close()
    if is_zip:
        shutil.rmtree(path)

# Main
process("C:\\Users\\Marcelo\\Downloads\\clocks\\galaxy_watch.zip", "galaxy2", True)
