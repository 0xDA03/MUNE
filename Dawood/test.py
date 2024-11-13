import numpy as np
import plotly.graph_objects as go

# Define the sigmoid function for firing probability
def firing_probability_curve(stimulus_intensity, midpoint, spread):
    slope = 1 / (midpoint * spread)
    return 1 / (1 + np.exp(-slope * (stimulus_intensity - midpoint)))

# Parameters for the curve
mean_intensity = 26.5      # Mean stimulus intensity (µV)
relative_spread = 1.65 / 100  # Relative spread as a percentage

# Generate stimulus intensities (e.g., membrane potentials)
stimulus_intensity = np.linspace(0, 50, 500)

# Compute firing probabilities
firing_probabilities = firing_probability_curve(stimulus_intensity, mean_intensity, relative_spread)

# Create Plotly figure
fig = go.Figure()

# Add the firing probability curve
fig.add_trace(go.Scatter(
    x=stimulus_intensity,
    y=firing_probabilities,
    mode="lines",
    line=dict(color="black", width=2),
    name="Firing Probability"
))

# Add a line for the mean stimulus intensity
fig.add_shape(type="line",
              x0=mean_intensity, y0=0, x1=mean_intensity, y1=1,
              line=dict(color="red", width=2, dash="dash"),
              name="Mean (26.5 mV)")

# Update layout with labels and styling
fig.update_layout(
    xaxis_title="Stimulus Intensity (mV)",
    yaxis_title="Firing Probability",
    plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
    xaxis=dict(
        showgrid=False,            # No gridlines
        zeroline=True,             # Show the zero line
        zerolinecolor="black",     # Color for zero line
        zerolinewidth=1,           # Width for zero line
        color="black",              # Color for axis line and ticks
        range=[22, 31]             # Zoom in on the specified range
    ),
    yaxis=dict(
        showgrid=False,            # No gridlines
        zeroline=True,             # Show the zero line
        zerolinecolor="black",     # Color for zero line
        zerolinewidth=1,           # Width for zero line
        color="black"              # Color for axis line and ticks
    )
)

fig.show()
