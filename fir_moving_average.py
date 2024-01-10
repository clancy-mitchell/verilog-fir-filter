import fxpmath
import numpy as np
import pyverilator
import matplotlib.pyplot as plt
from matplotlib import animation

# Parameters for the sine wave
frequency = 5  
amplitude = 1   
duration = 5    

# PyVerilog Driver for FIR Verilog module
class FIRVerilogDriver:

    # Call Verilator to build the Verilog FIR filter 
    def __init__ (self):
        self.sim = pyverilator.PyVerilator.build('fir_filter.v')

    # Initialize FIR filter
    def setup_sim(self):
        self.sim.io.clk = 0
        self.sim.io.reset = 0
        self.sim.io.enable = 1
        self.sim.io.samples_in = 0
        self.sim.io.fir_coeffs = 0

    # Read coefficients from array and pack into a single integer
    def set_fir_coeffs(self, coeffs):
        packed = 0
        bit_position = 0

        for coeff in coeffs:
            fixed_point = self.float_to_fxp(coeff)
            packed |= (fixed_point << bit_position)
            bit_position += 16
        
        self.sim.io.fir_coeffs = packed

    # Read FIR filter output and interpret fixed point (32 bits, 24 fractional)
    def read_fir_output(self):
        fixed_point_value = self.sim.io.filter_out
        fixed_point_value = np.int32(fixed_point_value)
        return fixed_point_value / (2 ** 24)

    # Helper function to convert to floating point (16 bits, 12 fractional)
    def float_to_fxp(self, x):
        return int(fxpmath.Fxp(x, signed=True, n_word=16, n_frac=12).val)

# Create a scrolling plot with a sine wave, noisy sine wave, and the FIR's moving avg of the noisy sine wave
def scrolling_plot_animation(freq, amplitude, duration, sample_rate=500, window_width=0.5):
    iterations = int(duration * sample_rate)
    t = np.linspace(0, duration, iterations)
    
    # Creating two subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 7))
    line1, = ax1.plot([], [], lw=2)
    line2, = ax2.plot([], [], lw=2)
    line3, = ax3.plot([], [], lw=2, color=(1, 0.341, 0.2))
    xdata, ydata_clean, ydata_noisy, ydata_fir = [], [], [], []  # Arrays to store computed data

    # Title plots
    ax1.text(0.95, 0.9, 'Pure Signal', horizontalalignment='right', verticalalignment='center', transform=ax1.transAxes)
    ax2.text(0.95, 0.9, 'Noisy Signal', horizontalalignment='right', verticalalignment='center', transform=ax2.transAxes)
    ax3.text(0.95, 0.9, 'Verilog FIR Filter', horizontalalignment='right', verticalalignment='center', transform=ax3.transAxes)
    
    # Axis naming, limits, and tick marks
    for ax in [ax1, ax2, ax3]:
        ax.set_ylabel('Amplitude')
        ax.set_ylim(-1.5, 1.5)
        ax.set_yticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5])
        ax.legend(frameon=False)

    # Verilog FIR Filter initialization
    fir = FIRVerilogDriver()
    fir.setup_sim()

    # Set FIR coefficients
    coeffs = [0.1] * 8
    fir.set_fir_coeffs(coeffs)
    fir.sim.io.enable = 1
    fir.sim.clock.tick()

    # Setup plot lines
    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        ax1.set_xlim(0, window_width)  
        ax2.set_xlim(0, window_width)  
        ax3.set_xlim(0, window_width) 
        return line1, line2, line3

    # Animation update function, loops 
    def animate(i):
        if t[i] > window_width:
            for ax in [ax1, ax2, ax3]:
                ax.set_xlim(t[i] - window_width, t[i])

        # Append xdata with new time and calculate ydata sine
        xdata.append(t[i])
        ydata_clean.append(amplitude * np.sin(2 * np.pi * freq * t[i]))

        # Add some noise to the signal
        ydata_noisy.append(amplitude * np.sin(2 * np.pi * freq * t[i]) + np.random.normal(0, 0.1, 1))

        # Send noisy data to the FIR filter
        fir_in = fir.float_to_fxp(ydata_noisy[i])
        fir.sim.io.samples_in = fir_in

        # Step the FIR Verilog modules clock
        fir.sim.clock.tick()

        # Read from FIR filter
        fir_out = fir.read_fir_output()
        ydata_fir.append(fir_out)

        # Update graph
        line1.set_data(xdata, ydata_clean)
        line2.set_data(xdata, ydata_noisy)
        line3.set_data(xdata, ydata_fir)
        return line1, line2, line3

    return animation.FuncAnimation(fig, animate, init_func=init, frames=iterations, interval=1)

# Start simulation and animation
anim = scrolling_plot_animation(frequency, amplitude, duration)
plt.show()