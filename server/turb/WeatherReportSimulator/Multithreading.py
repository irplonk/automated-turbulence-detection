from . import Simulator
from ..models import *
from ..db_interface import *
import threading
import time
from datetime import timedelta
import pytz

class SimulationThreadManager:
    """Holds multiple threads used for flight simulation.
    Provides methods to start, stop, pause and unpause all threads.
    """

    def __init__(self, flight_time, report_time, update_time, time_per_update, num_threads):
        """
        Creates a new thread manager and initializes the threads it holds.

        :param flight_time: Expected time between flights in seconds
        :param report_time: Expected time between weather reports in seconds
        :param update_time: Minimum real time between iterations of the simulation in seconds
        :param time_per_update: Simulated time per iteration in seconds
        :param num_threads: Total number of threads used
        """
        self.flight_time = flight_time
        self.report_time = report_time
        self.update_time = update_time
        self.time_per_update = time_per_update
        self.num_threads = num_threads
        self._paused = False
        self._stopped = False
        self._running = False
        self._threads = [SimulationThread(flight_time * num_threads, report_time * num_threads, update_time, time_per_update, num_threads > 1) for _ in range(num_threads)]

    def start(self):
        """Starts all of the threads held by this manager."""
        if self._running:
            return
        WeatherReport.objects.all().delete()
        Flight.objects.all().delete()
        Aircraft.objects.all().delete()
        Airport.objects.all().delete()
        for thread in self._threads:
            thread.start()
        self._running = True

    def stop(self):
        """Stops all of the threads held by this manager."""
        if self._stopped:
            return
        for thread in self._threads:
            thread.stop()
        self._stopped = True
        self._running = False

    def pause(self):
        """Pauses all of the threads held by this manager."""
        if self._paused:
            return
        for thread in self._threads:
            thread.pause()
        self._paused = True

    def unpause(self):
        """Unpauses all of the threads held by this manager."""
        if not self._paused:
            return
        for thread in self._threads:
            thread.unpause()
        self._paused = False

    @property
    def paused(self): return self._paused

    @property
    def running(self): return self._running

    @property
    def stopped(self): return self._stopped


class SimulationThread(threading.Thread):
    """Thread implementation for running flight simulation asynchronously."""

    def __init__(self, flight_time, report_time, update_time, time_per_update, parallel: bool=False):
        """
        Creates a new thread to run a flight simulation on

        :param flight_time: Expected time between flights in seconds
        :param report_time: Expected time between weather reports in seconds
        :param update_time: Minimum real time between iterations of the simulation in seconds
        :param time_per_update: Simulated time per iteration in seconds
        :param parallel: Whether files should be loaded to allow for multiple threads to access them
        """
        super(SimulationThread, self).__init__()
        self._flight_time = flight_time
        self._report_time = report_time
        self._update_time = update_time
        self._time_per_update = time_per_update
        self._sim = Simulator.WeatherReportSimulator.get_simulator(flight_time, report_time, parallel=parallel)
        self._stop_event = threading.Event()
        self._unpause_event = threading.Event()
        self._unpause_event.set()
        self._running = False

    def run(self):
        """Starts this thread. Will continually run until stop method is called."""
        keep_time = timedelta(hours=2)
        self._running = True
        while not self.stopped:
            self._unpause_event.wait()
            start = time.time()
            self._sim.progress(timedelta(seconds=self._time_per_update))
            for flight in self._sim.current_flights:
                update_flight(flight)
            for report in self._sim.new_reports:
                add_report(report)
            n = 0
            for report in WeatherReport.objects.filter(time__lte=(self._sim.current_time - keep_time).replace(tzinfo=pytz.UTC)).all():
                n += 1
                report.delete()
            print(str(len(self._sim.new_reports)) + ' new reports')
            print(str(n) + ' removed reports')
            dif = time.time() - start
            if dif < self._update_time:
                time.sleep(self.update_time - dif)
            else:
                print('simulation progressing ' + str(dif - self._update_time) + 's too slow')

    def stop(self):
        """Stops this thread. Cannot be started again once stopped."""
        print('simulation stopped')

        self._stop_event.set()
        self._running = False

    @property
    def stopped(self):
        """Whether this thread is stopped."""
        return self._stop_event.is_set()

    @property
    def running(self):
        """Whether this thread is running."""
        return self._running

    def pause(self):
        """Pauses this thread. Can be un-paused and continue at a later time.
        The thread will wait for unpause to be called rather than continually processing."""
        print('simulation paused')
        self._unpause_event.clear()

    def unpause(self):
        "Unpauses this thread. Continues running on the iteration it paused on."
        print('simulation unpaused')
        self._unpause_event.set()

    @property
    def paused(self):
        """Whether this thread is paused."""
        return self._pause_event.is_set()
