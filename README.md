Python control for Panasonic Blu-Ray players
============================================

This is a simple Python API for controlling Panasonic Blu-Ray players. It has only been tested with the DMP-BDT220, which dates from 2012. All players supported by the [Panasonic Blu-ray Remote 2012 Android app](https://play.google.com/store/apps/details?id=com.panasonic.avc.diga.blurayremote2012) should be supported; i.e. DMP-BDT120, DMP-BDT220, DMP-BDT221, DMP-BDT320, DMP-BDT500 and DMP-BBT01 devices.

Newer players with "UB" prefixes (e.g. the UB-9000) support a (very) limited set of functions.

Example use
-----------

Connect to a player on 192.168.0.4 and find out the current playing status:

```
import panacotta

bluray = panacotta.PansonicBD('192.168.0.4')
print("Device is currently %s" % bluray.get_play_status()[0])
```

Note that the device must be on the same subnet as the host running this API; requests from a different subnet will return a failure.

Press the power button:

```
import panacotta

bluray = panacotta.PansonicBD('192.168.0.4')
bluray.send_key('POWER')
```
