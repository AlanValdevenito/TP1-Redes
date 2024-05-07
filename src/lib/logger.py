import matplotlib.pyplot as plt
import time


class Logger:
    def __init__(self, verbose=False, interactive=False):
        self.verbose = verbose
        self.interactive = interactive
        if self.verbose:
            self.x_data = []
            self.y_data = []
            self.fig, self.ax = plt.subplots()
            self.line, = self.ax.plot(self.x_data, self.y_data)
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('RTT (ms)')
            self.ax.set_title('Real-time RTT Visualization')
        if self.interactive:
            plt.ion()  # Turn on interactive mode

    def log(self, message, quiet=False):
        if self.verbose or quiet:
            print(message)

    def log_rtt(self, rtt):
        print("RTT:", rtt)
        if self.verbose:
            self.x_data.append(time.time())  # Add current time to x-axis data
            self.y_data.append(rtt)  # Add RTT value to y-axis data

        if self.interactive:
            self.line.set_xdata(self.x_data)  # Update x-axis data
            self.line.set_ydata(self.y_data)  # Update y-axis data
            self.ax.relim()  # Update limits
            self.ax.autoscale_view()  # Autoscale
            plt.draw()  # Redraw the plot
            plt.pause(0.01)  # Pause for a short time to update the plot

    def log_final_rtt(self):
        print("Showing results")
        if self.verbose:
            self.line.set_xdata(self.x_data)
            self.line.set_ydata(self.y_data)
            self.ax.relim()
            self.ax.autoscale_view()
            plt.draw()
            plt.pause(10)
