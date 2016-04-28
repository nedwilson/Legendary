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
		g_showLUT = r'/Volumes/monovfx/inhouse/zmonolith/SHARED/lut/AlexaV3_K1S1_LogC2Video_EE_davinci3d_Profile_To_Rec709_2-4_G1_Og1_P1_Lum.cube'
		g_showRoot = r'/Volumes/monovfx/inhouse/zmonolith'

		activeSeq = hiero.ui.activeSequence()
		trackItems = activeSeq.videoTracks()[-1].items()

		ccTrack = hiero.core.VideoTrack("CC")
		activeSeq.addTrack(ccTrack)

		for ti in trackItems:
			csEffect = ccTrack.createEffect('OCIOColorSpace', timelineIn=ti.timelineIn(), timelineOut=ti.timelineOut())
			csEffect.node().knob('out_colorspace').setValue('AlexaV3LogC')

		for ti in trackItems:
			s_shot = ti.name()
			s_seq = ti.name()[0:3]
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
