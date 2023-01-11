# brew install imagemagick
# python setup.py install
# pip install python-weather
# https://openweathermap.org/weather-conditions
import cv2
import numpy as np
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont

class Config:
    #weather
    city = "Vladivostok"
    theme = "d"
    fontPath = './CaviarDreams.ttf'
    fontColor = (242, 242, 241)

def greyscale(img):
    greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return greyscale

def bright(img, beta_value):
    img_bright = cv2.convertScaleAbs(img, beta=beta_value)
    return img_bright

def sharpen(img):
    kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
    img_sharpen = cv2.filter2D(img, -1, kernel)
    return img_sharpen

def sepia(img):
    img_sepia = np.array(img, dtype=np.float64) # converting to float to prevent loss
    img_sepia = cv2.transform(img_sepia, np.matrix([[0.272, 0.534, 0.131],
                                    [0.349, 0.686, 0.168],
                                    [0.393, 0.769, 0.189]])) # multipying image with special sepia matrix
    img_sepia[np.where(img_sepia > 255)] = 255 # normalizing values greater than 255 to 255
    img_sepia = np.array(img_sepia, dtype=np.uint8)
    return img_sepia

def pencil_sketch_grey(img):
    #inbuilt function to create sketch effect in colour and greyscale
    sk_gray, sk_color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.1) 
    return  sk_gray

def pencil_sketch_col(img):
    #inbuilt function to create sketch effect in colour and greyscale
    sk_gray, sk_color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.1) 
    return  sk_color

def HDR(img):
    hdr = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    return  hdr

def invert(img):
    inv = cv2.bitwise_not(img)
    return inv

from scipy.interpolate import UnivariateSpline
def LookupTable(x, y):
    spline = UnivariateSpline(x, y)
    return spline(range(256))

def Summer(img):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel,red_channel  = cv2.split(img)
    red_channel = cv2.LUT(red_channel, increaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
    sum= cv2.merge((blue_channel, green_channel, red_channel ))
    return sum

def Winter(img):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel,red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, decreaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increaseLookupTable).astype(np.uint8)
    win= cv2.merge((blue_channel, green_channel, red_channel))
    return win

def addTextInPos(img, ft, text, x, y):
    new_im = Image.new("RGBA", (img.shape[1], img.shape[0]), "black")
    new_im.setim(img)

    draw = ImageDraw.Draw(new_im)
    draw.text((x, y), text, font=ft, fill=Config.fontColor)
    img = new_im.getim()
    return img

def transparentOverlay(src, overlay, pos=(0, 0)):
    h, w, _ = overlay.shape  # Size of foreground
    rows, cols, _ = src.shape  # Size of background Image
    y, x = pos[0], pos[1]  # Position of foreground/overlay image
    # loop over all pixels and apply the blending equation
    for i in range(h):
        for j in range(w):
            if x + i >= rows or y + j >= cols:
                continue
            alpha = float(overlay[i][j][3] / 255.0)  # read the alpha channel
            src[x + i][y + j] = alpha * overlay[i][j] + (1 - alpha) * src[x + i][y + j]
    return src

def addImageInPos(oriImg, waterImg, opacity, x, y):
    overlay = transparentOverlay(oriImg, waterImg, (x, y))
    output = oriImg.copy()
    
    cv2.addWeighted(overlay, opacity, output, 1 - opacity, 0, output)
    return output
    
def addWeatherWidget(img, x, y):
    b_channel, g_channel, r_channel = cv2.split(img)
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
    img = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    import requests, json
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = Config.city
    API_KEY = ""
    #URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    response = requests.get(BASE_URL, params={'q': CITY, 'units': 'metric', 'lang': 'en', 'APPID': API_KEY})
    # Sending HTTP request
    #response = requests.get(URL)
    
    # checking the status code of the request
    if response.status_code == 200:
        data = response.json()
        print(data)
        main = data['main']

        # getting temperature
        temperature = main['temp']
        # getting feel like
        temp_feel_like = main['feels_like']  
        # getting the humidity
        humidity = main['humidity']
        # getting the pressure
        pressure = main['pressure']

        # weather report
        weather_report = data['weather']

        icon = weather_report[0]['icon']
        # wind report
        wind_report = data['wind']

        if Config.theme == 'd':
            icon = icon[:-1] + 'd'
        else:
            icon = icon[:-1] + 'n'
        weatherIcoPath = './weatherIcons/' + icon + '.png'
        im = cv2.imread(weatherIcoPath, cv2.IMREAD_UNCHANGED)
        img = addImageInPos(img, im, 100, x, y)
        
        ft = ImageFont.truetype(Config.fontPath, 32)
        img = addTextInPos(img, ft, str(temperature)+'°C', x + 100, y + 25)
        ft = ImageFont.truetype(Config.fontPath, 16)
        img = addTextInPos(img, ft, weather_report[0]['description'], x + 100, y + 60)

        #print(f"{CITY:-^35}")
        #print(f"City ID: {data['id']}")   
        #print(f"Temperature: {temperature}")
        #print(f"Feel Like: {temp_feel_like}")    
        #print(f"Humidity: {humidity}")
        #print(f"Pressure: {pressure}")
        #print(f"Weather Report: {weather_report[0]['description']}")
        #print(f"Wind Speed: {wind_report['speed']}")
        #print(f"Time Zone: {data['timezone']}")
    else:
        # showing the error message
        print("Error in the HTTP request")
    return img


res = addWeatherWidget(bright(cv2.imread('./w.jpg'), -50), 50, 500)
cv2.imwrite('out.png', res)
#cv2.imshow("image", res);
