# RecrBeam Calculator

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ACI 318](https://img.shields.io/badge/Code-ACI%20318-blue.svg)](https://www.concrete.org/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)

A professional desktop application for calculating the **Nominal Moment Strength (Mn)** of rectangular reinforced concrete beams per ACI 318 provisions.

## Features

- Native Windows desktop application (no browser/localhost required)
- Professional dark theme UI
- Real-time calculations as you type
- **Unit system toggle**: Imperial (psi, in) / SI (MPa, mm)
- **Visual diagrams**: Cross Section, Strain Distribution, Stress Block & Forces
- **Step-by-step equations**: Detailed calculation breakdown with OK/NG indicators
- Minimum steel area check per ACI 318

## Screenshot

![Beam Analysis App](https://github.com/user-attachments/assets/e734b841-a5f7-48fa-b010-3c06c3ef1fb1)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/algorembrant/RecrBeam-Calculator.git
   cd RecrBeam-Calculator
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   
   Windows (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   Windows (Command Prompt):
   ```cmd
   .venv\Scripts\activate.bat
   ```
   
   macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Application

```bash
python app.py
```

The application will launch as a native desktop window.

### Input Parameters

| Parameter | Description | Imperial | SI |
|-----------|-------------|----------|-----|
| fc' | Concrete compressive strength | psi | MPa |
| fy | Steel yield strength | psi | MPa |
| Es | Modulus of elasticity | psi | MPa |
| Beta1 | Stress block factor | - | - |
| ecu | Ultimate concrete strain | - | - |
| b | Beam width | in | mm |
| h | Total beam depth | in | mm |
| d | Effective depth | in | mm |
| n | Number of bars | - | - |
| Ab | Bar area (each) | in2 | mm2 |

### Default Values (Example 4-1)

**Imperial:**
- fc' = 4000 psi, fy = 60,000 psi
- b = 12 in, h = 20 in, d = 17.5 in
- 4 bars at 0.79 in2 each (No. 8 bars)

**SI:**
- fc' = 20 MPa, fy = 420 MPa
- b = 250 mm, h = 565 mm, d = 500 mm
- 3 bars at 510 mm2 each

## Project Structure

```
RecrBeam-Calculator/
├── app.py              # Main desktop application (CustomTkinter)
├── calculator.py       # Beam calculation engine
├── test_calculator.py  # Unit tests
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── LICENSE             # MIT License
├── MATLAB/
│   └── app.m           # Original MATLAB implementation
└── Dump/
    └── example_4_1.tex # LaTeX documentation
```

## Theory

Based on ACI 318 provisions for nominal moment strength:

### Key Equations

**Stress block depth:**
```
a = (As * fy) / (0.85 * fc' * b)
```

**Neutral axis depth:**
```
c = a / Beta1
```

**Nominal moment strength:**
```
Mn = As * fy * (d - a/2)
```

**Minimum steel area (Imperial):**
```
As,min = max(3*sqrt(fc')/fy * b*d, 200/fy * b*d)
```

## Running Tests

```bash
python -m unittest test_calculator -v
```

## Dependencies

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [Matplotlib](https://matplotlib.org/) - Diagram plotting
- [NumPy](https://numpy.org/) - Numerical operations

## License

MIT License - see [LICENSE](LICENSE)

## References

- ACI 318-19: Building Code Requirements for Structural Concrete
- Example 4-1 and 4-1M from ACI 318 Design Handbook

## Citation

If you use this software in your research or project, please cite it as:

```bibtex
@software{recrbeam_calculator,
  author       = {algorembrant},
  title        = {RecrBeam Calculator: Nominal Moment Strength Calculator for Rectangular Beams},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/algorembrant/RecrBeam-Calculator},
  note         = {Based on ACI 318 provisions}
}
```
