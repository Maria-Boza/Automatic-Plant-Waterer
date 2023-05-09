# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

from threading import Thread

watering_sched = []

PAGE="""\
<html>
    <head>
        <title>Automatic Plant Waterer</title>
        <meta charset = "UTF-8">
        <meta name = "viewport" content = "width = device-width, initial-scale = 1">
        <link href = "https://agheck.github.io/style.css" rel="stylesheet" type="text/css">
        <script defer src="http://pyscript.net/alpha/pyscript.js"></script>
        <style>
          body {
            font-family: Arial, Helvetica, sans-serif;
          }
        </style>
    </head>

    <body>
        <div id = "everything">
            <div id = "main-title">
                Automatic Plant Waterer
            </div>
            <div id = "class-info">
                <center>Ashley Heckman (agh93) & Maria Boza (mib57)</center>
                <center>ECE 5725 Final Project</center>
                <center>Spring 2023</center>
            </div>
            <br>
            <div id = "all-but-title">
                <div id = "subtitle">
                    Livestream
                </div>
                <div class = "main-text">
                    Check out the live camera stream to see how your plant is doing! Watch 
                    those plants grow!
                </div>
                <center><img src="stream.mjpg" width="320" height="240"></center>
                <div id = "subtitle">
                    Sensor Measurements
                </div>
                <div class = "main-text">
                    The watering system has four measurements. The current measurements are:
                    <ul>
                        <li>Soil Moisture: </li>
                        <li>Temperature: </li>
                        <li>Humidity: </li>
                        <li>Sunlight: </li>
                    </ul>
                </div>
                <div id = "subtitle">
                    Watering Schedule
                </div>
                <div class = "main-text">
                    The plant waterer has three modes of watering:
                    <ul>
                        <li>Manual: The system will not automatically water the plant. The user 
                            must manually turn the water on and off.
                        </li>
                        <br>
                        <li>
                            Moisture: The system will automatically water the plant when the soil 
                            moisture drops below the desired level.
                        </li>
                        <br>
                        <li>
                            Intervals: The system will automatically water the plant at set intervals. 
                            For example, water the plant for 30 seconds every other day.
                        </li>
                    </ul>
                    The current watering schedule is
                    {watering_sched[len(watering_sched) - 1]}
                </div>
            </div>
        </div>
    </body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

output = StreamingOutput()
class Cam(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            #camera.rotation = 90
            camera.start_recording(output, format='mjpeg')
            try:
                address = ('', 8000)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
            finally:
                camera.stop_recording()

a = 0
class Control(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            global a
            #a += 1
            #print(str(a))
        
    
Cam()
Control()
while True:
    pass
