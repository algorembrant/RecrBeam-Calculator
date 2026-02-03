# Solution Breakdown: RecrBeam Calculator

This document details the **RecrBeam Calculator**, a software solution designed to solve the concrete beam design problem described in **Example 4-1**. It bridges the gap between the theoretical engineering calculations and the Python-based application mechanics.

---

## 1. Theoretical Foundation (Example 4-1)

The core engineering problem is to calculate the **Nominal Moment Strength ($M_n$)** of a singly reinforced concrete beam.

### Problem Statement
Given a rectangular beam with the following properties:
*   **Dimensions**: Width ($b$) = 12 in, Total Height ($h$) = 20 in.
*   **Effective Depth**: $d \approx 17.5$ in (Derived from $h - 2.5$).
*   **Materials**: 
    *   Concrete Strength ($f'_c$) = 4000 psi.
    *   Steel Yield Strength ($f_y$) = 60000 psi.
*   **Reinforcement**: 4 No. 8 bars.
    *   Area of one No. 8 bar = 0.79 in².
    *   Total Area ($A_s$) = $4 \times 0.79 = 3.16$ in².

**Goal**: Calculate $M_n$ and verify $A_s > A_{s,min}$.

### Manual Calculation Steps

#### Step 1: Verify Minimum Steel
The code requires $A_s$ to exceed $A_{s,min}$.
$$ \rho_{min} = \max\left( \frac{3\sqrt{f'_c}}{f_y}, \frac{200}{f_y} \right) $$
*   $\frac{3\sqrt{4000}}{60000} \approx 0.00316$
*   $\frac{200}{60000} \approx 0.00333$ (Governs)

$$ A_{s,min} = \rho_{min} \cdot b \cdot d = 0.00333 \cdot 12 \cdot 17.5 = 0.70 \text{ in}^2 $$
**Result**: $3.16 > 0.70$ (OK).

#### Step 2: Calculate Depth of Stress Block ($a$)
$$ a = \frac{A_s f_y}{0.85 f'_c b} $$
$$ a = \frac{3.16 \cdot 60000}{0.85 \cdot 4000 \cdot 12} = \frac{189,600}{40,800} \approx 4.647 \text{ in} $$

#### Step 3: Calculate Nominal Moment ($M_n$)
$$ M_n = A_s f_y \left( d - \frac{a}{2} \right) $$
*   Lever Arm: $d - a/2 = 17.5 - 2.3235 = 15.1765$ in.
*   $M_n = 189,600 \text{ lb} \cdot 15.1765 \text{ in} = 2,877,464 \text{ lb-in}$
*   Convert to k-ft: $2,877,464 / 12 / 1000 \approx \textbf{239.79 k-ft}$

---

## 2. Application Mechanics

The software implementation automates the above logic using Python.

### Core Logic: `calculator.py`
The `RectangularBeam` class mimics the manual steps.

```python
class RectangularBeam:
    def calculate_mn(self):
        # 1. Compute 'a' (Matches Step 2 above)
        # a = (As * fy) / (0.85 * fc * b)
        a = (self.As * self.fy) / (0.85 * self.fc * self.b)
        
        # 2. Compute Nominal Moment Mn (Matches Step 3 above)
        # Mn = As * fy * (d - a/2)
        Mn_force = self.As * self.fy 
        arm = self.d - (a / 2)
        Mn_kin = Mn_force * arm 
        
        # ... Conversions to k-ft
```

### Validation: `test_calculator.py`
The unit test acts as proof that the software aligns with the theory. It explicitly uses the Example 4-1 values as the "Golden Record".

```python
def test_example_4_19a(self):
    # Inputs from Example 4-1
    beam = RectangularBeam(
        width=12.0, effective_depth=17.5,
        f_c=4000.0, f_y=60000.0, rebar_area=3.16
    )
    results = beam.calculate_mn()
    
    # Assert correctness within tolerance
    self.assertAlmostEqual(results['a'], 4.647, delta=0.01)
    self.assertAlmostEqual(results['Mn_kft'], 239.79, delta=0.5)
```

### User Interface: `app.py`
The Streamlit app provides an interactive layer:
*   **Inputs**: Sidebar allows modifying $b, h, f'_c, f_y$ and bar sizes.
*   **Visualization**: Uses `matplotlib` to draw the cross-section (showing $b, h, d$ and rebar placement).
*   **Math Rendering**: Uses `st.latex` to display the equations dynamically, showing students exactly how inputs flow into the formula.
    ```python
    st.latex(fr"M_n = {As_total:.2f} \cdot {fy} \left({d:.2f} - \frac{{{results['a']:.3f}}}{{2}}\right)")
    ```

### Data Resilience: `db_manager.py`
*   **History**: Every calculation can be saved to a local SQLite database (`beam_calc.db`).
*   **Persistence**: Enables review of past design iterations.

---

## 3. Conclusion

The **RecrBeam Calculator** is a faithful digital twin of the manual engineering process defined in ACI 318.
*   **Input**: Manual engineering parameters.
*   **Process**: Standard Whitney Stress Block methodology (`calculator.py`).
*   **Output**: Verified against text book examples (`test_calculator.py`).
