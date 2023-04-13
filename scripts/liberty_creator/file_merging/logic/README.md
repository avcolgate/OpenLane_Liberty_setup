# Installation

1. Clone this repository
2. Install pyeda wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/ (optional)

Python 3.7+ is required.

# Features

## Verilog parser

Current parser works with synthesized Verilog. 
Use Circuit class to read or write your circuit:

    from logic import Circuit
    circuit = Circuit.from_verilog("path_to_circuit.v")
    circuit.to_verilog("path_to_output_circuit.v")

`to_verilog` method renames all wires by default to avoid collisions, 
use `rename=False` to keep the original names.

### Circuit structure

There are 4 main types of entities in the Circuit object:
* `inputs` - input terminals
* `outputs` - output terminals
* `gates` - logic gates
* `nets` - wire interconnections

Each entity is stored in their respective `IDDict` container that provides access by name and by ID:

    from logic import Circuit
    circuit = Circuit.from_verilog("path_to_circuit.v")
    gate_0 = circuit.gates[0]
    gate_G0 = circuit.gates.by_name('G0')

Nets connect to gates and terminals via pins. Each net must have one driver pin and any number of output pins.
Each gate must have one output and any number of input pins (multi-output gates are not supported at the moment).

In case of hierarchical design, `submodules` attribute stores a dictionary of modules used inside the main circuit.

## Liberty parser

In order to perform simulations or some form of analysis, library data is needed.
Use Liberty parser to read your .lib file:

    from logic import Liberty
    lib = Liberty.load("path_to_library.lib")

Most of the data contained in .lib file might be redundant for your goal, 
so you might want to customize the parser. 
For that you'll need to set up your desired library structure in separate file
and import it before parsing:

    from logic import Liberty
    import logic.doc.templates.liberty
    lib = Liberty.load("path_to_library.lib")

Use example in _doc/templates/liberty.py_ and read the docstrings in _models/Liberty.py_
for more info on customization.

Converting to JSON:

    from logic import Liberty
    lib1 = Liberty.load("path_to_library1.lib")
    lib2 = Liberty.load("path_to_library2.lib")
    ...
    Liberty.to_json(lib1, lib2, ..., filename="output_path.json")

By default, numeric values are converted to ints and floats, set `convert_numerics=False` to keep strings.

## Logic simulations

_Only combinational simulation is supported at the moment._

Signatures are used to run a number of logic simulations in parallel. Signature is a sequence of logic values
on a circuit node. They are represented as arbitrarily long integers in order to perform bitwise logic operations on them.
Read more about parallel logic simulations in [1].

`datatypes.Signature.Signature` class contains a few useful static methods to work with signatures 
(however, note that it's not used to instantiate objects, signature objects are just `int`).

`Circuit` class provides methods for exhaustive and random simulations:

    from logic import Circuit, Liberty
    lib = Liberty.load("path_to_library.lib")
    circuit = Circuit.from_verilog("path_to_circuit.v", lib)
    exhaustive_sim_ID = circuit.exhaustive_simulation()
    random_sim_ID = circuit.random_simulation(vector_length=1000)

Both methods return simulation IDs used to retrieve the results:

    exh_inputs = circuit.logic_simulation_inputs(exhaustive_sim_ID)
    exh_outputs = circuit.logic_simulation_outputs(exhaustive_sim_ID)

It's also possible to observe internal signals. After simulation there's a signature on each internal pin. 
Pins are objects that connect nets with gates or terminals. For example, if you want to observe outputs of a gate `G2`:

    gate = circuit.gates.by_name('G2')
    for pin in gate.outputs:
        sim_results = pin.simulation_results[exhaustive_sim_ID]
        signature = sim_results[exhaustive_sim_ID]

To be able to pass arbitrary input signatures, you'll need to instantiate a `Process`:

    from logic.tools import Process
    simulate = Process.simulation(name='logic simulation', vector_length=1000)

`simulate` is a callable `Process` object that takes a circuit and a dictionary of input signatures,
returns a dictionary of output signatures:

    random_outputs = simulate(circuit, random_inputs)

Each simulation has new ID meaning that multiple calls might use a lot of memory. 
Call `clear_simulation` method to delete unnecessary data:

    circuit.clear_simulation(simID=-1)      # -1 means last simulation

`Process` module provides more than just logic simulation, check other functions there
if you need an advanced circuit processing. 
`Process.Process` class allows to create your own processing functions from smaller blocks.

## Structure manipulation

`logic.models.virtual.Location.Location` class provides interface for creating 'transparent' subcircuits
which can be used for analysis or manipulation. Location's boundary only exist in the Location itself,
it's not visible from the parent Circuit. However, it can capture or replace its contents:

    from logic import Circuit
    from logic.models.virtual.Location import Location
    circuit = Circuit.from_verilog("path_to_circuit.v")

    location = Location('subc', parent=circuit)
    location.include(circuit.gates.by_name('G0'), circuit.gates.by_name('G1'))

    subc_obj = location.to_circuit()        # Location contents to Circuit object
    location.to_verilog("subcircuit.v")     # Location contents to Verilog file
    location.from_circuit(subc_obj)         # replace location contents with Circuit object
    location.from_verilog("subcircuit.v")   # replace location contents using Verilog file
