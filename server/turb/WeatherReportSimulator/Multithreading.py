from . import Simulator
from ..models import *
from ..db_interface import *
import threading
import time
from datetime import timedelta
import pytz

class SimulationThreadManager:
    def __init__(self, flight_time, report_time, update_time, time_per_update, num_threads):
        self.flight_time = flight_time
        self.report_time = report_time
        self.update_time = update_time
        self.time_per_update = time_per_update
        self.num_threads = num_threads
        self.paused = False
        self.threads = [SimulationThread(flight_time * num_threads, report_time * num_threads, update_time, time_per_update, num_threads > 1) for _ in range(num_threads)]

    def start(self):
        WeatherReport.objects.all().delete()
        Flight.objects.all().delete()
        Aircraft.objects.all().delete()
        Airport.objects.all().delete()
        for thread in self.threads:
            print('Started thread')
            thread.start()

    def stop(self):
        for thread in self.threads:
            thread.stop()

    def pause(self):
        for thread in self.threads:
            thread.pause()

    def unpause(self):
        for thread in self.threads:
            thread.unpause()


class SimulationThread(threading.Thread):
    def __init__(self, flight_time, report_time, update_time, time_per_update, parallel: bool=False):
        super(SimulationThread, self).__init__()
        self.flight_time = flight_time
        self.report_time = report_time
        self.update_time = update_time
        self.time_per_update = time_per_update
        self.sim = Simulator.WeatherReportSimulator.get_simulator(flight_time, report_time, parallel=parallel)
        self._stop_event = threading.Event()
        self._unpause_event = threading.Event()
        self._unpause_event.set()

    def run(self):
        print('Running thread')
        keep_time = timedelta(hours=2)
        while not self.stopped():
            self._unpause_event.wait()
            start = time.time()
            self.sim.progress(timedelta(seconds=self.time_per_update))
            for report in self.sim.new_reports:
                add_report(report)
            n = 0
            for report in WeatherReport.objects.filter(time__lte=(self.sim.current_time - keep_time).replace(tzinfo=pytz.UTC)).all():
                n += 1
                report.delete()
            print(str(len(self.sim.new_reports)) + ' new reports')
            print(str(n) + ' removed reports')
            dif = time.time() - start
            if dif < self.update_time:
                time.sleep(self.update_time - dif)
            else:
                print('simulation progressing ' + str(dif - self.update_time) + 's too slow')

    def stop(self):
        print('simulation stopped')
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def pause(self):
        print('simulation paused')
        self._unpause_event.clear()

    def unpause(self):
        print('simulation unpaused')
        self._unpause_event.set()

    def paused(self):
        return self._pause_event.is_set()
