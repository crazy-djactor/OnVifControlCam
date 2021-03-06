import zeep
import asyncio, sys
from onvif import ONVIFCamera
import cv2
import numpy as np
import urllib
from urllib.request import urlopen

IP="192.168.2.22"   # Camera IP address
PORT=80           # Port
USER="admin"         # Username
PASS="C0nc3ll0M4r1n"        # Password

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
moverequest = None
ptz = None
active = False

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue
zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

def setup_move():
    mycam = ONVIFCamera(IP, PORT, USER, PASS)
    # Create media service object
    media = mycam.create_media_service()
    print("setup_move {} {}", mycam, media)
    # Create ptz service object
    global ptz
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]
    profileToken = media_profile.token

    # Get presets
    print("Get Presets...")
    gp = ptz.create_type('GetPresets')
    gp.ProfileToken = profileToken
    presets = ptz.GetPresets(gp)
    for preset in presets:
        if (hasattr(preset, "Name")):
            name = preset.Name
        else:
            name = ""
        position = preset['PTZPosition']

        print("preset {} => ({}, {}, {})".format(name, position.PanTilt.x,
                                             position.PanTilt.y,
                                             position.Zoom.x))
    # GetStatus
    print("GetStatus")
    status = ptz.GetStatus({'ProfileToken': profileToken})
    print('status {} {} {}   ? => {}'.format(status.Position.PanTilt.x, status.Position.PanTilt.y,
                                      status.Position.Zoom.x,
                                   status.MoveStatus.PanTilt))

    # abMove = ptz.create_type('AbsoluteMove')
    # abMove.ProfileToken = profileToken
    # print('status {} {} {} {}'.format(status.Position.PanTilt.x, status.Position.PanTilt.y,
    #                                   status.Velocity.PanTilt.x, status.Velocity.PanTilt.y))

    return
    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    global moverequest
    moverequest = ptz.create_type('ContinuousMove')
    moverequest.ProfileToken = media_profile.token
    if moverequest.Velocity is None:
        moverequest.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position


    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    # global XMAX, XMIN, YMAX, YMIN
    # XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    # XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    # YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    # YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

def url_to_image(url):
    # password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    # password_mgr.add_password(None, url, USER, PASS)
    # handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    # opener = urllib.request.build_opener(handler)
    # urllib.request.install_opener(opener)
    # resp = urlopen(url)
    import requests
    from requests.auth import HTTPDigestAuth
    resp = requests.get(url, auth=HTTPDigestAuth(USER, PASS))
    if resp.status_code == 200:
        image = np.asarray(bytearray(resp.content), dtype="uint8")
        image2 = cv2.imdecode(image, cv2.IMREAD_COLOR)
        cv2.imshow('image', image2)
        return image
    else:
        return None


class CameraController:
    presets = []
    status = None

    def get_current_preset(self):
        mycam = ONVIFCamera(IP, PORT, USER, PASS, '../wsdl/')
        # Create media service object
        media = mycam.create_media_service()
        print("setup_move {} {}", mycam, media)
        # Create ptz service object

        ptz = mycam.create_ptz_service()
        # Get target profile
        media_profile = media.GetProfiles()[0]
        profileToken = media_profile.token

        # GetStatus
        print("GetStatus")
        self.status = ptz.GetStatus({'ProfileToken': profileToken})
        print('status {} {} {}   ? => {}'.format(self.status.Position.PanTilt.x, self.status.Position.PanTilt.y,
                                                 self.status.Position.Zoom.x,
                                                 self.status.MoveStatus.PanTilt))

        min_dist = 100
        current_prest = None
        for preset in self.presets:
            position = preset['PTZPosition']
            dist = pow((self.status.Position.PanTilt.x - position.PanTilt.x), 2) + pow((self.status.Position.PanTilt.y - position.PanTilt.y), 2)
            if dist < min_dist:
                min_dist = dist
                current_prest = preset

        snapshot = media.GetSnapshotUri({'ProfileToken': profileToken})
        print('snapshot uri {}'.format(snapshot))
        # image = io.imread(snapshot)
        # n_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # cv2.imwrite('./image1.jpg', n_image)
        image = url_to_image(snapshot.Uri)
        cv2.imwrite('./image2.jpg', image)

        return current_prest, self.status.MoveStatus.PanTilt, snapshot

    def get_presets(self):
        mycam = ONVIFCamera(IP, PORT, USER, PASS, '../wsdl/')
        # Create media service object
        media = mycam.create_media_service()
        print("setup_move {} {}", mycam, media)
        # Create ptz service object

        ptz = mycam.create_ptz_service()
        # Get target profile
        media_profile = media.GetProfiles()[0]
        profileToken = media_profile.token

        # Get presets
        print("Get Presets...")
        gp = ptz.create_type('GetPresets')
        gp.ProfileToken = profileToken
        self.presets = ptz.GetPresets(gp)
        for preset in self.presets:
            if (hasattr(preset, "Name")):
                name = preset.Name
            else:
                name = ""
            position = preset['PTZPosition']

            print("preset {} => ({}, {}, {})".format(name, position.PanTilt.x,
                                                 position.PanTilt.y,
                                                 position.Zoom.x))
        return self.presets


if __name__ == '__main__':
    # url_to_image('http://192.168.1.108/onvifsnapshot/media_service/snapshot?channel=1&subtype=0')
    # setup_move()
    camera = CameraController()
    camera.get_presets()
    camera.get_current_preset()