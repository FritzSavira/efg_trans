# Code Visualizer Guide

The **Code Visualizer** is a tool for generating visual documentation directly from the source code using static analysis. It produces PlantUML diagram files.

## Usage

Run the tool using the following command from the project root:

```bash
python -m visualizer --entrypoint <module_path.function_name> --type <diagram_type> --output <output_file>
```

### Parameters

- `--entrypoint` / `-e`: (Required) The dot-notation path to the function you want to visualize.
  - Example: `app.routes.index`, `app.utils.data_extractor.extract_coordinates`
- `--type` / `-t`: The type of diagram to generate.
  - `flowchart` (Default): Shows the logical flow (if/else, returns) within a single function.
  - `sequence`: Shows interactions (calls) between modules.
- `--output` / `-o`: The output file path. Defaults to `output.puml`.

## Diagram Types

### Flowchart
Visualizes the control flow of a function. Useful for understanding complex conditional logic.

**Example:**
```bash
python visualize.py -e app.utils.data_extractor.extract_coordinates -t flowchart -o coords_flow.puml
```

### Sequence Diagram
Visualizes how the entry point function interacts with other modules or its own helper functions.

**Example:**
```bash
python visualize.py -e app.routes.refresh_data -t sequence -o refresh_seq.puml
```

## Rendering Diagrams
The output is in **PlantUML** format. You can render these files:
1. Online at [PlantText](https://www.planttext.com/) or [PlantUML Online Server](http://www.plantuml.com/plantuml/).
2. Using an IDE plugin (e.g., "PlantUML" in VS Code or PyCharm).
3. Locally using the PlantUML JAR file.
