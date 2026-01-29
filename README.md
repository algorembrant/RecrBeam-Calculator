# Example 4-1: Nominal Moment Strength Calculation for a Singly Reinforced Concrete Beam

This document provides a detailed, step-by-step breakdown of the example problem shown in the provided figure (Fig. 4-19a). The goal is to calculate the nominal moment strength $M_n$ for the beam and confirm that the area of tension steel exceeds the required minimum steel area as per Equation (4-11) from the relevant design code (likely ACI 318 or similar). All calculations are performed without skipping any micro-steps, including unit conversions and intermediate arithmetic operations where applicable.

The beam is a rectangular section made of concrete with compressive strength **$f'_c$** = 4000 psi, reinforced with four No. 8 bars in tension having yield strength **$f_y$** = 60 ksi. The beam dimensions are width **$b$** = 12 in. and total height **$h$** = 20 in. The effective depth **$d$** is approximated as $h - 2.5$ in. to account for concrete cover, stirrup diameter, and half the longitudinal bar diameter.

## Given Data

- Concrete compressive strength: **$f'_c$** = 4000 psi
- Steel yield strength: **$f_y$** = 60 ksi = 60,000 psi (converted for consistency in units)
- Beam width: **$b$** = 12 in.
- Beam total height: **$h$** = 20 in.
- Effective depth (assumed): **$d$** = $h - 2.5 = 20 - 2.5 = 17.5$ in.
- Tension reinforcement: 4 No. 8 bars
- Diameter of No. 8 bar: 1.0 in. (standard ASTM A615/A706 bar size)
- Area of one No. 8 bar: **$A_{bar}$** = $\pi \times (diameter/2)^2 = \pi \times (1.0/2)^2 = \pi \times (0.5)^2 = \pi \times 0.25 \approx 0.7854$ in² (using $\pi \approx 3.1416$)
- Total tension steel area: **$A_s$** = $4 \times 0.7854 = 3.1416$ in²
- Compression reinforcement: Small bars may be present to hold stirrups, but they are ignored as they are not designed for compression resistance.
- Rectangular stress block factor: **$\beta_1$** = 0.85 (for $f'_c = 4000$ psi, per ACI 318)
- Equation (4-11) for minimum steel area: Assumed to be ACI 318-19 Section 9.6.1.2, where **$A_{s,min}$** = $\max\left( \frac{3\sqrt{f'_c}}{f_y} bd, \frac{200}{f_y} bd \right)$

**Note on Effective Depth $d$:**  
The approximation of 2.5 in. accounts for:  
- Clear concrete cover: 1.5 in. (typical for beams not exposed to weather).  
- Stirrup diameter: 0.5 in. (for a No. 4 bar) or 0.375 in. (for No. 3), but averaged.  
- Half the longitudinal bar diameter: 0.5 in. (for No. 8 bar).  
Total: $1.5 + 0.5 + 0.5 = 2.5$ in. This is accurate for most designs unless rebar interference requires adjustment.

## Step 1: Confirm Tension Steel Area Exceeds Minimum Required

### Step 1.1: Calculate $\rho_{min}$ Using Equation (4-11)
The minimum reinforcement ratio **$\rho_{min}$** is the maximum of two values:  
1. $\frac{3 \sqrt{f'_c}}{f_y}$  
2. $\frac{200}{f_y}$ (in psi units)

#### Micro-Calculation for First Term: $\frac{3 \sqrt{f'_c}}{f_y}$
- Calculate $\sqrt{f'_c} = \sqrt{4000}$:  
  $63^2 = 3969$, $64^2 = 4096$, so $\sqrt{4000} \approx 63.2456$ (using $\sqrt{4000} = \sqrt{100 \times 40} = 10 \sqrt{40} \approx 10 \times 6.3246 = 63.246$).  
- $3 \times 63.2456 = 189.7368$  
- $\frac{189.7368}{60,000} = 0.00316228$

#### Micro-Calculation for Second Term: $\frac{200}{f_y}$
- $\frac{200}{60,000} = 0.00333333$

#### Select $\rho_{min}$
- **$\rho_{min}$** = $\max(0.00316228, 0.00333333) = 0.00333333$

### Step 1.2: Calculate Minimum Steel Area $A_{s,min}$
- **$A_{s,min}$** = $\rho_{min} \times b \times d$  
- First, $b \times d = 12 \times 17.5 = 210$ in²  
- $A_{s,min} = 0.00333333 \times 210 = 0.6999993 \approx 0.70$ in²  

### Step 1.3: Compare Actual $A_s$ with $A_{s,min}$
- Actual **$A_s$** = 3.1416 in²  
- $3.1416 > 0.70$, so the tension steel area exceeds the minimum required.  
- Reinforcement ratio **$\rho$** = $\frac{A_s}{b d} = \frac{3.1416}{210} = 0.014960$, which is greater than $\rho_{min} = 0.003333$.

## Step 2: Calculate Nominal Moment Strength $M_n$

For a singly reinforced beam, use the rectangular stress block assumption (Whitney block). The nominal moment **$M_n$** is calculated as:  
$$M_n = A_s f_y \left( d - \frac{a}{2} \right)$$  
where **$a$** is the depth of the equivalent rectangular stress block:  
$$a = \frac{A_s f_y}{0.85 f'_c b}$$

### Step 2.1: Calculate Depth of Stress Block $a$

#### Micro-Calculation for Numerator: $A_s f_y$
- **$A_s$** = 3.1416 in²  
- **$f_y$** = 60,000 psi  
- $A_s f_y = 3.1416 \times 60,000 = 188,496$ lb (force in pounds)  
  - Breakdown: $3 \times 60,000 = 180,000$; $0.1416 \times 60,000 = 8,496$; total 188,496 lb.

#### Micro-Calculation for Denominator: $0.85 f'_c b$
- $0.85 \times f'_c = 0.85 \times 4000 = 3,400$ psi  
- $3,400 \times b = 3,400 \times 12 = 40,800$ lb/in.  
  - Breakdown: $3,400 \times 10 = 34,000$; $3,400 \times 2 = 6,800$; total 40,800 lb/in.

#### Calculate $a$
- **$a$** = $\frac{188,496}{40,800}$ in.  
- Division: $40,800 \times 4 = 163,200$; subtract from 188,496 → 25,296  
- $40,800 \times 0.6 = 24,480$; subtract → 816  
- $40,800 \times 0.02 = 816$; subtract → 0  
- Total: $4 + 0.6 + 0.02 = 4.62$ in. (exact: $188,496 \div 40,800 \approx 4.6200$ in.)  

### Step 2.2: Calculate Lever Arm $d - \frac{a}{2}$
- $\frac{a}{2} = \frac{4.6200}{2} = 2.3100$ in.  
- $d - \frac{a}{2} = 17.5 - 2.3100 = 15.1900$ in.

### Step 2.3: Calculate $M_n$ in in.-lb
- **$M_n$** = $A_s f_y \times \left( d - \frac{a}{2} \right) = 188,496 \times 15.1900$  
- First, $188,496 \times 15 = 188,496 \times 10 = 1,884,960$; $188,496 \times 5 = 942,480$; total 2,827,440  
- $188,496 \times 0.19 = 188,496 \times 0.2 = 37,699.2$; minus $188,496 \times 0.01 = 1,884.96$; so $37,699.2 - 1,884.96 = 35,814.24$  
- Total: $2,827,440 + 35,814.24 = 2,863,254.24$ in.-lb  

### Step 2.4: Convert $M_n$ to ft-kip
- 1 ft = 12 in., so divide by 12: $2,863,254.24 \div 12 = 238,604.52$ ft-lb  
- 1 kip = 1,000 lb, so divide by 1,000: $238,604.52 \div 1,000 = 238.60452$ ft-kip  
- Rounded: Approximately **239 ft-kip** (but exact value is 238.6 ft-kip for precision).

## Step 3: Verify Assumptions and Additional Notes
- **Strain Compatibility:** The section is under-reinforced since $\rho = 0.01496 < \rho_{max}$ (for balanced, $\rho_b \approx 0.0214$ for these strengths), so tension controls, and assumptions hold.  
  - Micro-calc: $\rho_b = 0.85 \beta_1 \frac{f'_c}{f_y} \frac{600}{600 + f_y/1000} = 0.85 \times 0.85 \times \frac{4000}{60,000} \times \frac{600}{600 + 60} = 0.7225 \times 0.06667 \times \frac{600}{660} \approx 0.04817 \times 0.9091 \approx 0.0438$ (wait, correct formula for ACI: $\rho_b = \frac{0.85 \beta_1 f'_c}{f_y} \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_y}$, with $\epsilon_{cu}=0.003$, $\epsilon_y = f_y / E_s = 60/29,000 \approx 0.00207$).  
    - $\frac{0.003}{0.003 + 0.00207} = \frac{0.003}{0.00507} \approx 0.5917$  
    - $0.85 \times 0.85 \times \frac{4000}{60,000} = 0.7225 \times 0.066667 \approx 0.04817$  
    - $\rho_b = 0.04817 \times 0.5917 \approx 0.0285$ (actual for these values). Since $\rho < \rho_b$, under-reinforced.  
- **Compression Zone Bars:** Ignored as per the problem statement, since they are for stirrup positioning only.  
- **Accuracy of $d$:** If stirrup is No. 3 (dia=0.375 in.), $d = 20 - 1.5 - 0.375 - 0.5 = 17.625$ in., which would slightly increase $M_n$. But 2.5 in. is sufficient for this example.  
- **Units Consistency:** All forces in lb, stresses in psi, lengths in in. Conversions shown explicitly.

This calculation confirms the beam's capacity and compliance with minimum reinforcement requirements. For design iterations, adjust if rebar interference occurs. 

**References:**  
- ACI 318-19 Building Code Requirements for Structural Concrete.  
- Figure and problem from provided example (e.g., textbook on reinforced concrete design).
