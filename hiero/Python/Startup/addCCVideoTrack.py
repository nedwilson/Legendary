import os
import hiero.core
import hiero.ui
from PySide.QtGui import *
from PySide.QtCore import *

class AddCCVideoTrack(QAction):
    def __init__(self):
        QAction.__init__(self, "Add CC Video Track", None)
        self.triggered.connect(self.addCCTrack)
        hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)

    def addCCTrack(self):
        # todo: pull this out into a config file
		g_showLUT = r'/Volumes/raid_vol01/work/darktower/SHARED/lut/TDT_10052016_REC709.cube'
		g_showRoot = r'/Volumes/raid_vol01/work/darktower'

		activeSeq = hiero.ui.activeSequence()
		trackItems = activeSeq.videoTracks()[-1].items()

        # todo: make sure that the CC track doesn't already exist. If it does, delete the effects in it and remake.
		ccTrack = hiero.core.VideoTrack("CC")
		activeSeq.addTrack(ccTrack)

		for ti in trackItems:
			csEffect = ccTrack.createEffect('OCIOColorSpace', timelineIn=ti.timelineIn(), timelineOut=ti.timelineOut())
			csEffect.node().knob('out_colorspace').setValue('AlexaV3LogC')

		for ti in trackItems:
			s_shot = ti.name()
			# todo: pull this out into a config file
			s_seq = ti.name()[0:2]
			s_cdlFile = os.path.join(g_showRoot, s_seq, s_shot, 'data', 'cdl', '%s.cdl'%s_shot)
			cdlEffect = ccTrack.createEffect('OCIOCDLTransform', timelineIn=ti.timelineIn(), timelineOut=ti.timelineOut())
			cdlEffect.node().knob('read_from_file').setValue(True)
			cdlEffect.node().knob('file').setValue(s_cdlFile)

		for ti in trackItems:
			lutEffect = ccTrack.createEffect('OCIOFileTransform', timelineIn=ti.timelineIn(), timelineOut=ti.timelineOut())
			lutEffect.node().knob('file').setValue(g_showLUT)

		for ti in trackItems:
			csrEffect = ccTrack.createEffect('OCIOColorSpace', timelineIn=ti.timelineIn(), timelineOut=ti.timelineOut())
			csrEffect.node().knob('in_colorspace').setValue('Rec709')

    def eventHandler(self, event):
        enabled = True
        title = "Add CC Video Track"
        self.setText(title)
        event.menu.addAction( self )

# The act of initialising the action adds it to the right-click menu...
AddCCVideoTrackInstance = AddCCVideoTrack()

# Add it to the Menu bar Edit menu to enable keyboard shortcuts
# timelineMenu = hiero.ui.findMenuAction("Timeline")
# timelineMenu.menu().addAction(AddCCVideoTrack)
