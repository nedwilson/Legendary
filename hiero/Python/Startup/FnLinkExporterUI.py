import os.path
import PySide.QtCore
import PySide.QtGui

import hiero.ui
import FnLinkExporter


class LinkExporterUI(hiero.ui.TaskUIBase):
  def __init__(self, preset):
    """Initialize"""
    hiero.ui.TaskUIBase.__init__(self, FnLinkExporter.LinkExporter, preset, "Link Exporter")


hiero.ui.taskUIRegistry.registerTaskUI(FnLinkExporter.LinkPreset, LinkExporterUI)
