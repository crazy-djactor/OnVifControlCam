import zeep
import asyncio, sys
from onvif import ONVIFCamera

IP="192.168.1.108"   # Camera IP address
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
    print('status {} {} {}   ? => '.format(status.Position.PanTilt.x, status.Position.PanTilt.y,
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


if __name__ == '__main__':
    setup_move()