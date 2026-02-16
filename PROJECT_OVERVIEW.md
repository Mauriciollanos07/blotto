# Blotto Game Project Overview

## What is Blotto?

A strategic resource allocation game built with Dash where players compete against AI by distributing 100 resources across multiple battlefields. Victory is determined by winning the most battlefields, not by total resources allocated.

## Game Features

- **Rule Selection**: Choose from different game rules (DEFAULT, RULES 2, RULES 3)
- **Battlefield Configuration**: Select 3-6 battlefields to play on
- **Match Modes**: Play in free mode or structured rounds (1-10 rounds)
- **Resource Allocation**: Use sliders to distribute 100 resources across battlefields
- **Visual Results**: View distribution charts and territory maps
- **Victory Tracking**: Monitor wins, losses, and ties in a results table

## Code Structure

### Main Components (`app.py`)

**Data Storage**
- Uses `dcc.Store` components to maintain game state (player/AI allocations, match status, round count)
- Initializes victory tracking dataframe and map coordinates

**Layout Elements**
- Radio buttons for rule selection
- Dropdowns for battlefield and round configuration  
- Dynamic sliders for resource allocation (generated based on battlefield count)
- Results visualization with tabs for charts and maps
- Victory table with conditional styling

**Core Callbacks (8 total)**
1. **Rule Display**: Shows rule descriptions based on selection
2. **Match Control**: Manages match button text and submit button state
3. **Slider Generation**: Creates appropriate number of sliders for battlefields
4. **Resource Validation**: Checks if allocations exceed 100 resources
5. **Match Toggle**: Activates/deactivates round-based matches
6. **Data Processing**: Handles submissions and generates AI responses
7. **Game Logic**: Validates moves, determines winners, updates scores and graphics
8. **Styling**: Highlights selected rules and winning players in table

### Helper Functions (`reglas.py`)

- `get_ai_allocations()`: Generates rule-compliant random AI allocations
- `validate_player_allocs()`: Ensures player moves follow selected rules

## Technical Implementation

Built with Dash framework using:
- Interactive components (sliders, dropdowns, buttons)
- Real-time validation and feedback
- Dynamic chart generation with Plotly
- Conditional styling for enhanced UX
- Memory-based state management for session persistence