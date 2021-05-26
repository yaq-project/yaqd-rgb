__all__ = ["RGBQmini"]

import asyncio
from typing import Dict, Any, List

from yaqd_core import HasMapping, HasMeasureTrigger, IsSensor, IsDaemon

from .rgbdriverkit.qseriesdriver import Qseries  # type: ignore


class RGBQmini(HasMapping, HasMeasureTrigger, IsSensor, IsDaemon):
    _kind = "rgb-qmini"

    def __init__(self, name, config, config_filepath):
        dev = Qseries.search_devices(config["serial"])
        self.spec = Qseries(dev[0])
        super().__init__(name, config, config_filepath)
        self._channel_names = ["intensities"]
        self._channel_units = {"intensities": None}
        self._mappings["wavelengths"] = self.spec.get_wavelengths()
        shape = (len(self._mappings["wavelengths"]),)
        self._channel_shapes = {"intensities": shape}
        self._channel_mappings = {"intensities": "wavelengths"}

        if self._state["exposure_time"]:
            self.spec.exposure_time = self._state["exposure_time"]

    async def _measure(self):
        self.spec.start_exposure(1)
        while not self.spec.available_spectra:
            await asyncio.sleep(0.01)
        out = {}
        spectrum = self.spec.get_spectrum_data()
        out["intensities"] = spectrum.Spectrum
        return out

    def set_exposure_time(self, exposure_time: float):
        self._state["exposure_time"] = exposure_time
        self.spec.exposure_time = exposure_time

    def get_exposure_time(self) -> float:
        return self._state["exposure_time"]
