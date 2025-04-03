
# Logic Gate Simulator 🔧

A visual node-based digital logic circuit simulator built with PyQt5.

🔗 **Repository**: [https://github.com/Suyash878/PyQt5-Logic-Gates.git](https://github.com/Suyash878/PyQt5-Logic-Gates.git)

## Table of Contents
- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Logic Gates](#logic-gates)
- [Keyboard Shortcuts](#keyboard-shortcuts)

## Overview
The Logic Gate Simulator provides an intuitive interface for creating and simulating digital logic circuits. Built using PyQt5, it offers a modern drag-and-drop experience with real-time simulation capabilities.

## Screenshots
### Main Interface
![image-3](https://github.com/user-attachments/assets/1ed31232-5ae9-4b26-a59f-3029e9226ad9)

### Dark Theme
![image-4](https://github.com/user-attachments/assets/4b197baa-870a-4236-9e6c-4fdafdb5a48f)

## Features
### Core Functionality ⚡
- Visual node editor with drag-and-drop interface
- Real-time circuit simulation
- Multiple logic gates (AND, OR, NOT, NAND, NOR, XOR, XNOR)
- Input/Output nodes with state visualization
- Grid-based layout with snapping
    
### Advanced Features 🛠
- File Operations
  - Save/Load circuits
  - Multiple tabs support
  - File output support
- Editor Features
  - Undo/Redo functionality
  - Cut/Copy/Paste operations
  - Dark/Light theme toggle
  - Grid snapping
  - Zoom in/out

## Prerequisites
Before running the simulator, ensure you have:
```bash
- Python 3.8 or higher
- pip (Python package installer)
- PyQt5 compatible system
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Suyash878/PyQt5-Logic-Gates.git
cd logic-gate-simulator
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Usage
### Basic Operations
1. **Creating Circuits**
   - Drag gates from side panel
   - Connect nodes using click-drag
   - Set input values using input nodes

2. **Saving Work**
   - Use Ctrl+S to save
   - Choose File → Save As for new files

3. **Theme Customization**
   - Toggle dark/light mode (Ctrl+T)

## Logic Gates
### Basic Gates
#### AND Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 0      |
| 0       | 1       | 0      |
| 1       | 0       | 0      |
| 1       | 1       | 1      |

#### OR Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 0      |
| 0       | 1       | 1      |
| 1       | 0       | 1      |
| 1       | 1       | 1      |

#### NOT Gate
| Input | Output |
|-------|--------|
| 0     | 1      |
| 1     | 0      |

### Compound Gates
#### NAND Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 1      |
| 0       | 1       | 1      |
| 1       | 0       | 1      |
| 1       | 1       | 0      |

#### NOR Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 1      |
| 0       | 1       | 0      |
| 1       | 0       | 0      |
| 1       | 1       | 0      |

#### XOR Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 0      |
| 0       | 1       | 1      |
| 1       | 0       | 1      |
| 1       | 1       | 0      |

#### XNOR Gate
| Input A | Input B | Output |
|---------|---------|--------|
| 0       | 0       | 1      |
| 0       | 1       | 0      |
| 1       | 0       | 0      |
| 1       | 1       | 1      |

## Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| New Tab | Ctrl+N |
| Open | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Undo | Ctrl+Z |
| Redo | Ctrl+Shift+Z |
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Delete | Delete |
| Toggle Theme | Ctrl+T |

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
>>>>>>> master
