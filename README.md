## Gridone Chiller Emulator

Minimal chiller emulator service exposing a small HTTP API for reading and updating a single in-memory chiller instance.

## Linting and type checking

This project uses `ruff` and `ty` for lint and type checks.

## Local development

- **Install dependencies**:

```sh
uv sync --all-groups
```

## Chiller attributes

- **enabled** (`bool`, R/W): whether the chiller is on or off.
- **unit_state** (`bool`, R): whether the compressor currently runs.
- **inlet_temperature** (`float`, R): current inlet water temperature.
- **outlet_temperature** (`float`, R): current outlet water temperature.
- **mode** (`int`, R/W): `1` = heat, `2` = cool.
- **outdoor_temperature** (`float`, R): current outdoor air temperature.
- **setpoint_temperature** (`float`, R/W): target outlet temperature; defaults to `40.0` in heat mode and `10.0` in cool mode.

## HTTP API

- **GET** `/chiller/snapshot`  
  Returns a snapshot of all attributes.

- **PATCH** `/chiller`  
  Accepts a JSON body with any subset of writable fields:
  - `enabled`
  - `mode`
  - `setpoint_temperature`

If `mode` is changed without an explicit `setpoint_temperature`, the setpoint is reset to the default for that mode.


- **Run the API server**:

```bash
uv run uvicorn main:app --reload
```

- **Run tests**:

```bash
uv run pytest
```

