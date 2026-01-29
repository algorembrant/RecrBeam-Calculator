import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from calculator import RectangularBeam
import db_manager

# Page Config
st.set_page_config(page_title="RecrBeam Calculator", page_icon="🏗️", layout="wide")

# Initialize DB
if 'db_initialized' not in st.session_state:
    db_manager.init_db()
    st.session_state['db_initialized'] = True

st.title("🏗️ Rectangular Beam Calculator")
st.markdown("Calculate Nominal Moment Capacity ($M_n$) and visualize beam sections.")

# Sidebar Inputs
st.sidebar.header("Beam Parameters")

col1, col2 = st.columns([1, 2])

with st.sidebar:
    # Dimensions
    st.subheader("Dimensions")
    b = st.number_input("Width (b) [in]", min_value=1.0, value=12.0, step=0.5)
    h = st.number_input("Total Height (h) [in]", min_value=1.0, value=20.0, step=0.5)
    
    # Material Properties
    st.subheader("Materials")
    fc = st.number_input("Concrete Strength (f'c) [psi]", min_value=2000.0, value=4000.0, step=100.0)
    fy = st.number_input("Steel Yield Strength (fy) [psi]", min_value=30000.0, value=60000.0, step=100.0)
    
    # Reinforcement
    st.subheader("Reinforcement")
    # Simple input for now, could be enhanced with bar selection
    bar_size = st.selectbox("Bar Size", ["No. 3", "No. 4", "No. 5", "No. 6", "No. 7", "No. 8", "No. 9", "No. 10", "No. 11", "No. 14", "No. 18"], index=5)
    num_bars = st.number_input("Number of Bars", min_value=1, value=4, step=1)
    
    cover = st.number_input("Concrete Cover [in]", min_value=0.0, value=1.5, step=0.1)
    stirrup_size = st.selectbox("Stirrup Size", ["No. 3", "No. 4"], index=0)

# Helper for bar areas
bar_areas = {
    "No. 3": 0.11, "No. 4": 0.20, "No. 5": 0.31, "No. 6": 0.44, 
    "No. 7": 0.60, "No. 8": 0.79, "No. 9": 1.00, "No. 10": 1.27, 
    "No. 11": 1.56, "No. 14": 2.25, "No. 18": 4.00
}
stirrup_diams = {"No. 3": 0.375, "No. 4": 0.500}
bar_diams = {
    "No. 3": 0.375, "No. 4": 0.500, "No. 5": 0.625, "No. 6": 0.750,
    "No. 7": 0.875, "No. 8": 1.000, "No. 9": 1.128, "No. 10": 1.270,
    "No. 11": 1.410, "No. 14": 1.693, "No. 18": 2.257
}

As_single = bar_areas[bar_size]
As_total = As_single * num_bars
bar_diam = bar_diams[bar_size]
stirrup_diam = stirrup_diams[stirrup_size]

# Calculate d automatically
# d = h - cover - stirrup_diam - bar_diam/2
d_calc = h - cover - stirrup_diam - (bar_diam / 2)

st.sidebar.markdown(f"**Calculated d:** {d_calc:.2f} in")
use_custom_d = st.sidebar.checkbox("Override Effective Depth (d)")
if use_custom_d:
    d = st.sidebar.number_input("Effective Depth (d) [in]", min_value=1.0, value=d_calc, step=0.1)
else:
    d = d_calc

# Main Content
col_res, col_vis = st.columns([1, 1])

with col_res:
    st.subheader("Calculation Results")
    try:
        beam = RectangularBeam(b, d, fc, fy, As_total)
        results = beam.calculate_mn()
        
        # --- NEW: Display Equation with Values ---
        st.markdown("### Calculation Details")
        st.latex(r"M_n = A_s f_y \left(d - \frac{a}{2}\right)")
        
        # Substitute values for display
        st.markdown(f"**Substitution:**")
        st.latex(fr"M_n = {As_total:.2f} \cdot {fy} \left({d:.2f} - \frac{{{results['a']:.3f}}}{{2}}\right)")
        
        st.success(f"**Nominal Moment Capacity ($M_n$):** {results['Mn_kft']:.2f} k-ft")
        
        st.markdown("#### Detailed Results")

        st.write(f"- **Reinforcement Area ($A_s$):** {As_total:.2f} $in^2$")
        st.write(f"- **Depth of Stress Block ($a$):** {results['a']:.3f} in")
        st.write(f"- **Neutral Axis Depth ($c$):** {results['c']:.3f} in")
        st.write(f"- **Net Tensile Strain ($\epsilon_t$):** {results['epsilon_t']:.4f}")
        st.write(f"- **Strength Reduction Factor ($\phi$):** {results['phi']:.2f}")
        st.write(f"- **Design Moment Capacity ($\phi M_n$):** {results['Mu_kft']:.2f} k-ft")
        
        # Save Button
        if st.button("Save Calculation"):
            inputs = {
                'b': b, 'h': h, 'd': d, 'fc': fc, 'fy': fy, 
                'As': As_total, 'bar_size': bar_size, 'num_bars': num_bars
            }
            db_manager.save_calculation(inputs, results)
            st.toast("Calculation saved to history!", icon="💾")
            
    except Exception as e:
        st.error(f"Error in calculation: {e}")

with col_vis:
    st.subheader("Beam Visualization")
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Draw Concrete Section
    # Centered at 0, h/2
    rect = patches.Rectangle((0, 0), b, h, linewidth=2, edgecolor='gray', facecolor='#f0f0f0')
    ax.add_patch(rect)
    
    # Draw Rebar (simplified as dots at bottom)
    # y position = cover + stirrup + bar_diam/2 (which is h - d)
    rebar_y = h - d
    
    # Distribute bars evenly
    # spacing = (b - 2*cover - 2*stirrup - bar_diam) / (num_bars - 1)
    # Simplified visual distribution
    margin = cover + stirrup_diam + bar_diam/2
    if num_bars == 1:
        x_positions = [b/2]
    else:
        spacing = (b - 2*margin) / (num_bars - 1)
        x_positions = [margin + i*spacing for i in range(num_bars)]
        
    for x in x_positions:
        circle = patches.Circle((x, rebar_y), radius=bar_diam/2, edgecolor='black', facecolor='red')
        ax.add_patch(circle)
        
    # Draw Stirrup (approximate)
    stirrup_rect = patches.Rectangle(
        (cover, cover), 
        b - 2*cover, 
        h - 2*cover, 
        linewidth=1, edgecolor='blue', fill=False, linestyle='--'
    )
    ax.add_patch(stirrup_rect)
    
    # Dimensions Annotation
    ax.annotate(f"b = {b}\"", xy=(b/2, -1), ha='center', va='top')
    ax.annotate(f"h = {h}\"", xy=(-1, h/2), ha='right', va='center', rotation=90)
    ax.annotate(f"d = {d:.2f}\"", xy=(b+2, rebar_y + (h-rebar_y)/2), ha='left', va='center')
    # Draw arrow for d
    ax.annotate("", xy=(b+1, h), xytext=(b+1, rebar_y), arrowprops=dict(arrowstyle="<->"))

    ax.set_xlim(-5, b + 5)
    ax.set_ylim(-5, h + 5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    st.pyplot(fig)

# History Section
st.markdown("---")
st.subheader("Recent Calculations")
history = db_manager.get_history()

if history:
    history_data = []
    for item in history:
        inp = item['inputs']
        res = item['results']
        history_data.append({
            "Time": item['timestamp'],
            "b (in)": inp['b'],
            "d (in)": inp['d'],
            "As (in²)": inp['As'],
            "Mn (k-ft)": round(res['Mn_kft'], 2),
            "phi Mn (k-ft)": round(res['Mu_kft'], 2)
        })
    st.dataframe(pd.DataFrame(history_data))
else:
    st.info("No calculations saved yet.")
