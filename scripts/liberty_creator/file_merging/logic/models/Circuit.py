from ..exceptions import ParseError
from .elements import *
from .pins import *
from ..datatypes import Signature, IDDict
from ..tools.Traversal import *
from ..tools import Process
from .virtual.Void import Void
from itertools import compress, count
from functools import reduce
from operator import or_
from random import getrandbits
import re
import pickle


class Circuit:
    """Logic circuit class


    """
    __CONSTANTS = {'1\'b0': Constant('1\'b0', lambda: 0),
                   '1\'b1': Constant('1\'b1', lambda: Signature.all_ones)}

    # region properties
    @property
    def gates(self):
        return self.__gates

    @property
    def nets(self):
        return self.__nets

    @property
    def inputs(self):
        return self.__inputs

    @property
    def outputs(self):
        return self.__outputs

    @property
    def constants(self):
        return self.__constants

    @property
    def void(self):
        return self.__void

    # endregion

    # region constructors
    def __init__(self, name=None, library=None):
        self.name = name
        self.library = library
        self.__gates = IDDict()
        self.__nets = IDDict()
        self.__inputs = IDDict()
        self.__outputs = IDDict()
        self.__constants = {}
        self.__void = Void(self)

        self.simulations = []

    def copy(self) -> 'Circuit':
        """Return copy of self structure"""
        copy = self.__class__(name=self.name + '_copy', library=self.library)

        correspondence = ((self.gates, copy.gates, Gate, {}),
                          (self.nets, copy.nets, Net, {}),
                          (self.inputs, copy.inputs, Terminal, {}),
                          (self.outputs, copy.outputs, Terminal, {}))

        for self_dict, copy_dict, _, IDmap in correspondence:
            for instance in self_dict:
                originalID = instance.ID
                copyID = copy_dict.add(instance.copy(parent=copy))
                IDmap[originalID] = copyID

        def source(pin):
            if not pin.from_:
                return copy.void
            for _, copy_dict, class_, IDmap in compress(correspondence, [1, 1, 1, 0]):
                if isinstance(pin.from_, class_):
                    originalID = pin.from_.ID
                    copyID = IDmap[originalID]
                    return copy_dict[copyID]
            return pin.from_

        for self_dict, copy_dict, _, IDmap in compress(correspondence, [1, 1, 0, 0]):
            for instance in self_dict:
                for pin in instance.inputs:
                    from_ = source(pin)
                    pin.copy(from_=from_, to_=copy_dict[IDmap[instance.ID]], parent=copy)
        IDmap = correspondence[3][3]
        for out in self.outputs:
            if isinstance(out.from_, PinBase):
                pin = out.from_
                from_ = source(pin)
                pin.copy(from_=from_, to_=copy.outputs[IDmap[out.ID]], parent=copy)

        return copy

    # endregion

    # region read/write
    @classmethod
    def from_verilog(cls, filename: str, library: 'Library' = None, top: str = None) -> 'Circuit':
        """Parse verilog file, return Circuit instance

        filename - path to source verilog file
        library - Core.models.Library.Library instance
        top - top module name for multilevel circuits
        """
        circuits = {}
        cur_circuit = None
        inputs = {}
        outputs = {}
        gates = {}
        nets = {}
        submodules = {}

        def bus_to_array(s):
            rb = s.find(']')
            range_ = s[1:rb]
            start, end = range_.split(sep=':')
            label = s[rb + 1:]
            return ('{}[{}]'.format(label, i) for i in range(int(end), int(start) + 1))

        def parse_module(s):
            nonlocal cur_circuit, top

            cur_circuit = cls(library=library)
            cur_circuit.name, _ = s.split('(', maxsplit=1)
            circuits[cur_circuit.name] = cur_circuit

            if top is None:
                top = cur_circuit.name

        def parse_inputs(s):
            s = s.replace(' ', '')
            for label in s.split(sep=','):
                if label[0] == '[':
                    for l in bus_to_array(label):
                        nets[l] = Net(l, parent=cur_circuit)
                        inputs[l] = Terminal(l, parent=cur_circuit)
                        PinBase(l, from_=inputs[l], to_=nets[l], parent=cur_circuit)
                else:
                    nets[label] = Net(label, parent=cur_circuit)
                    inputs[label] = Terminal(label, parent=cur_circuit)
                    PinBase(label, from_=inputs[label], to_=nets[label], parent=cur_circuit)

        def parse_outputs(s):
            s = s.replace(' ', '')
            for label in s.split(sep=','):
                if label[0] == '[':
                    for l in bus_to_array(label):
                        nets[l] = Net(l, parent=cur_circuit)
                        outputs[l] = Terminal(l, parent=cur_circuit)
                        PinBase(l, from_=nets[l], to_=outputs[l], parent=cur_circuit)
                else:
                    nets[label] = Net(label, parent=cur_circuit)
                    outputs[label] = Terminal(label, parent=cur_circuit)
                    PinBase(label, from_=nets[label], to_=outputs[label], parent=cur_circuit)

        def parse_wires(s):
            s = s.replace(' ', '')
            for label in s.split(sep=','):
                if label not in nets:
                    nets[label] = Net(label, parent=cur_circuit)

        def parse_assign(s):
            s = s.replace(' ', '')
            left, right = s.split('=')
            left = nets[left]
            if right in Circuit.__CONSTANTS:
                if right not in cur_circuit.__constants:
                    cur_circuit.__constants[right] = Circuit.__CONSTANTS[right].copy()
                right = cur_circuit.__constants[right]
                PinBase(left.label + '_', from_=right, to_=left, parent=cur_circuit)
            else:
                right = nets[right]
                PinBase(left.label + '_', from_=right, to_=left, parent=cur_circuit)

        def endmodule():
            cur_circuit.inputs.add(*inputs.values())
            cur_circuit.outputs.add(*outputs.values())
            cur_circuit.gates.add(*gates.values())
            cur_circuit.nets.add(*nets.values())
            cur_circuit.submodules = copy(submodules)

            cur_circuit._attach_hanging()
            cur_circuit._merge_consecutive_nets()
            cur_circuit.gates._update_name_dict('label')
            cur_circuit.nets._update_name_dict('label')
            cur_circuit.inputs._update_name_dict('label')
            cur_circuit.outputs._update_name_dict('label')

            inputs.clear()
            outputs.clear()
            gates.clear()
            nets.clear()
            submodules.clear()

        def parse_gate(cell, s):
            name, s = s.split(maxsplit=1)
            if cell in circuits:
                gate = Gate(name, model=circuits[cell], parent=cur_circuit)
                submodules[cell] = circuits[cell]
            elif library and cell in library.cell:
                model = library.cell[cell]
                if hasattr(model, 'ff') and model.ff:
                    gate = SequentialGate(name, model=model, parent=cur_circuit)
                    if 'clock_inps' not in cur_circuit.__dict__:
                        cur_circuit.clock_inps = set()
                    ff, = gate.model.ff.values()
                    cur_circuit.clock_inps.add(inputs.get(ff.clocked_on))
                else:
                    gate = CombinationalGate(name, model=model, parent=cur_circuit)
            else:
                gate = Gate(name, model=cell, parent=cur_circuit)

            s = s.replace(' ', '')[1:-1]
            pin_defs = s.split(sep=',')

            if cell in circuits:
                get_direction = lambda label, i: 'input' if label in circuits[cell].inputs.name_dict else 'output'
                get_model = lambda label, direction: circuits[cell].inputs.name_dict[label] if direction == 'input' \
                    else circuits[cell].outputs.name_dict[label]
            elif library:
                get_direction = lambda label, i: library.cell[cell].pin[label].direction
                get_model = lambda label, direction: library.cell[cell].pin[label]
            else:
                get_direction = lambda label, i, last=len(pin_defs) - 1: 'output' if i == last else 'input'
                get_model = lambda label, direction: direction

            for i, pin_def in enumerate(pin_defs):
                lb = pin_def.find('(')
                if pin_def[0] != '.' or pin_def[-1] != ')' or lb == -1:
                    raise ParseError('Error parsing gate {}: cannot read pin definition'.format(name))
                label = pin_def[1:lb]
                connection = pin_def[lb + 1:-1]
                direction = get_direction(label, i)
                if direction == 'input':
                    try:
                        connection = nets[connection] if connection in nets else inputs[connection]
                    except KeyError:
                        if connection not in cur_circuit.__constants:
                            cur_circuit.__constants[connection] = Circuit.__CONSTANTS[connection].copy()
                        connection = cur_circuit.__constants[connection]
                    from_ = connection
                    to_ = gate
                else:
                    connection = nets[connection] if connection in nets else outputs[connection]
                    to_ = connection
                    from_ = gate
                PinBase(label, from_=from_, to_=to_, parent=cur_circuit, model=get_model(label, direction))
            gates[name] = gate

        keywords = {'module': parse_module,
                    'input': parse_inputs,
                    'output': parse_outputs,
                    'wire': parse_wires,
                    'assign': parse_assign}

        with open(filename, 'r') as f:
            string = f.read()
        string = re.sub('\/\*.*?\*\/', '', string)
        string = re.sub('//.*?\n', '', string)
        string = re.sub('\s+', ' ', string)

        for statement in string.split(sep=';'):
            statement = statement.strip()

            if statement.startswith('endmodule'):
                endmodule()
                statement = statement[10:].strip()

            if not statement:
                continue

            kw, s = statement.split(maxsplit=1)
            parse_func = keywords.get(kw)
            if parse_func:
                parse_func(s)
            else:
                parse_gate(kw, s)

        return circuits[top]

    def to_verilog(self, filename: str, rename: bool = True, rewrite=True, recursive=True) -> None:
        """Write circuit structure to file in verilog format

        filename - path to output file
        rename - flag: if True (default), then gates and nets are renamed using their IDs to avoid any collisions
            set False if you need original labels (not collision-safe)
        """
        if rename:
            net_prefix = 'w'
            while any(inp.label.startswith(net_prefix) for inp in self.inputs) or \
                    any(out.label.startswith(net_prefix) for out in self.outputs):
                net_prefix += '_'
            self.rename_safe(net_prefix=net_prefix)
        inputs = [pin.label for pin in self.inputs]
        outputs = [pin.label for pin in self.outputs]
        pins = inputs + outputs
        nets = [net.label for net in self.nets]

        def pins_to_buses(pins: list, terminal: bool):
            pins_bits = [[re.sub('\[.*?\]', '', pin), re.sub('\](.+|)', '', re.sub('.*?\[', '', pin))] for pin in pins]
            buses = []
            lonely_bits = {}
            for pin, bit in pins_bits:
                if pin == bit:
                    buses.append(bit)
                    continue
                elif ':' in bit:
                    buses.append('[{}] '.format(bit) + pin)
                    continue
                try:
                    bit = int(bit)
                    if bit > lonely_bits[pin]['max']:
                        lonely_bits[pin]['max'] = int(bit)
                        continue
                    elif bit < lonely_bits[pin]['min']:
                        lonely_bits[pin]['min'] = bit
                        continue
                except KeyError:
                    lonely_bits[pin] = {}
                    lonely_bits[pin]['min'] = bit
                    lonely_bits[pin]['max'] = 0
            if terminal:
                for pin, bits in lonely_bits.items():
                    buses.append('[{}:{}] {}'.format(str(bits['max']), str(bits['min']), pin))
            else:
                for pin in lonely_bits.keys():
                    buses.append(pin)
            return list(set(buses))  # delete repeats

        with open(filename, 'w' if rewrite else 'a') as fout:
            fout.write('\nmodule {} ( {} );\n'.format(self.name, ', '.join(pins_to_buses(pins.copy(), False))))
            fout.write('  input {};\n'.format(';\n  input '.join(pins_to_buses(inputs.copy(), True))))
            fout.write('  output {};\n'.format(';\n  output '.join(pins_to_buses(outputs.copy(), True))))
            fout.write('  wire {};\n\n'.format(';\n  wire '.join(nets)))

            for s, const in self.__constants.items():
                for pin in const.fanout:
                    fout.write('  assign {} = {};\n'.format(pin.to_, s))

            for inp in self.inputs:
                w = inp.to_.to_
                if isinstance(w, Net) and w.label != inp.label:
                    fout.write('  assign {} = {};\n'.format(w.label, inp.label))
            for out in self.outputs:
                w = out.from_.from_
                if isinstance(w, Net) and w.label != out.label:
                    fout.write('  assign {} = {};\n'.format(out.label, w.label))

            fout.write('\n')

            for gate in self.gates:
                fout.write('  {};\n'.format(gate))
            fout.write('endmodule\n\n')

        for circuit in self.submodules.values():
            circuit.to_verilog(filename, rename=rename, rewrite=False)

    def __str__(self):
        return self.name

    # endregion

    # region processes
    def exhaustive_simulation(self) -> int:
        """Perform exhaustive simulation, return simulation ID"""
        if len(self.inputs) > 20:
            raise ValueError('Too many inputs')
        simulate = Process.simulation(vector_length=(1 << len(self.inputs)))
        input_labels = [inp.label for inp in self.inputs]
        inputs = dict(Signature.exhaustive(sorted(input_labels)))
        simulate(self, inputs)
        return len(self.simulations) - 1

    def random_simulation(self, vector_length: int) -> int:
        """Perform simulation with random signatures, return simulation ID"""
        simulate = Process.simulation(vector_length=vector_length)
        inputs = {inp.label: getrandbits(vector_length) for inp in self.inputs}
        simulate(self, inputs)
        return len(self.simulations) - 1

    def ODC_simulation(self, simID: int) -> int:
        """Compute ODC masks via error simulation, return process ID

        simID - ID of the respective logic simulation
        """
        compute_ODC = Process.observability_simulation(simulation_ID=simID)
        compute_ODC(self)
        return len(self.simulations) - 1

    def copy_process_data(self, procID: int = -1) -> int:
        """Duplicate process results, return new ID

        procID - ID of the respective process (latest process by default)
        """
        for pin in self.pins():
            pin.simulation_results.append(copy(pin.simulation_results[procID]))
        self.simulations.append(self.simulations[procID])
        return len(self.simulations) - 1

    def clear_simulation(self, simID: int = -1) -> None:
        """Delete simulation results

        simID - ID of the respective simulation (latest simulation by default)
        """
        for pin in self.pins():
            pin.simulation_results.pop(simID)
        self.simulations.pop(simID)

    def logic_simulation_outputs(self, simID: int = -1) -> dict:
        """Return dictionary of output signatures assuming simID is ID of logic simulation"""
        return {out.label: out.from_.simulation_results[simID][0] for out in self.outputs}

    def logic_simulation_inputs(self, simID: int = -1) -> dict:
        """Return dictionary of input signatures assuming simID is ID of logic simulation"""
        return {inp.label: inp.to_.simulation_results[simID][0] for inp in self.inputs}

    # endregion

    # region calculations
    def area(self) -> float:
        """Return area of the circuit"""
        return sum(gate.model.area for gate in self.gates)

    def sensitivity_factor(self, procID: int) -> float:
        """Return sensitivity factor of the circuit

        procID - ID of the respective ODC computation process
        """
        signlen = Signature.length

        def obs(gate):
            out, = gate.outputs
            ODC = out.simulation_results[procID][0]
            return Signature.hamming_weight(ODC)

        return sum(map(obs, self.gates)) / signlen

    def sensitive_area(self, procID: int) -> float:
        """Return sensitive area of the circuit

        procID - ID of the respective ODC computation process
        """
        signlen = Signature.length

        def sa(gate):
            out, = gate.outputs
            ODC = out.simulation_results[procID][0]
            return Signature.hamming_weight(ODC) * gate.model.area

        return sum(map(sa, self.gates)) / signlen

    # endregion

    # region analysis
    def all_submodules(self):
        """
        Search for all submodules recursively, return dict
        """
        subs = {}
        if not hasattr(self, 'submodules'):
            return subs

        subs.update(self.submodules)
        for sub in subs.values():
            subs.update(sub.all_submodules())
        return subs

    def distance(self, source: 'Gate | Terminal', target: 'Gate') -> int:
        """Return number of gates between source's output and target's output (including target itself)
        If there's no direct way from source to target, return 0
        If source and target are swapped, return negative number
        """
        for gate, d in fanout_topological(self, [source]):
            if gate is target:
                return d
        if isinstance(source, Terminal):
            return 0
        for gate, d in fanin_reverse_topological(self, [source]):
            if gate is target:
                return -d
        return 0

    def unordered_fanout_cone(self, front: 'Iterable', levels: int = -1) -> set:
        """Return set of gates in transitive fanout cone

        front - gates or input terminals
        levels - max distance from front elements (not restricted by default)

        Tip: this function is faster than Traversal.fanout_topological but does not perform topological sorting
        """
        cone = set()

        def add(gate, level):
            cone.add(gate)
            if level == levels:
                return
            for el in gate.successors(filter=lambda e: isinstance(e, Gate)):
                if el not in cone:
                    add(el, level + 1)

        for el in front:
            add(el, 0)
        cone.difference_update(front)
        return cone

    def unordered_fanin_cone(self, front: 'Iterable', levels: int = -1) -> set:
        """Return set of gates in transitive fanin cone

        front - gates or output terminals
        levels - max distance from front elements (not restricted by default)

        Tip: this function is faster than Traversal.fanin_reverse_topological but does not perform topological sorting
        """
        cone = set()

        def add(gate, level):
            cone.add(gate)
            if level == levels:
                return
            for el in gate.predecessors(filter=lambda e: isinstance(e, Gate)):
                if el not in cone:
                    add(el, level + 1)

        for el in front:
            add(el, 0)
        cone.difference_update(front)
        return cone

    def IO_connectivity(self) -> tuple:
        """Return two dictionaries:
        {<input Terminal>: [<output Terminal>, ...]},
        {<output Terminal>: [<input Terminal>, ...]}

        In the first one each key is circuit input and value is list of outputs reachable from that input,
        In the second one each key is circuit output and value is list of inputs from which that output can be reached
        """
        inps = list(self.inputs)
        dependency = dict(zip(inps, (1 << i for i in count())))
        for el in Traversal.topological_order(self).no_numbers():
            if isinstance(el, Terminal) and el.from_ is None:
                continue
            pred_deps = (dependency[pred] for pred in el.predecessors())
            dependency[el] = reduce(or_, pred_deps, 0)

        out_deps = {out: Signature.decode(dependency[out], inps) for out in self.outputs}
        inp_deps = {inp: [] for inp in self.inputs}
        for out, inps in out_deps.items():
            for inp in inps:
                inp_deps[inp].append(out)
        return inp_deps, out_deps

    def has_no_loops(self) -> bool:
        """Return True if circuit does not contain any cycles"""
        checked = set()

        def noloop(path, gate):
            if gate in checked:
                return True
            if gate.label in path:
                return False
            path.add(gate.label)
            for succ in gate.successors():
                if isinstance(succ, Terminal):
                    continue
                if not noloop(path, succ):
                    return False
            path.remove(gate.label)
            checked.add(gate)
            return True

        return all(noloop(set(), inp) for inp in self.inputs)

    # endregion

    # region auxiliary
    def rename_safe(self, gate_prefix: str = 'G', net_prefix: str = 'w') -> None:
        """Rename gates and nets by their ID:
        new name = <prefix><ID>
        """
        self.gates.rename_items_by_ID(gate_prefix, 'label')
        self.nets.rename_items_by_ID(net_prefix, 'label')

    def initialize_process(self, name: str) -> None:
        """Prepare for new process"""
        self.simulations.append(name)
        for pin in self.pins():
            pin.initialize_simulation()

    def pins(self):
        """Return all internal pins"""
        pins = set()
        for gate in self.gates:
            pins.update(gate.inputs)
            pins.update(gate.outputs)
        for net in self.nets:
            pins.add(net.driver)
            pins.update(net.outputs)
        for out in self.outputs:
            pins.add(out.from_)
        for inp in self.inputs:
            pins.add(inp.to_)
        for const in self.__constants.values():
            pins.update(const.fanout)
        return pins

    def connectivity_correct(self):
        """Search for problems in data structure, return True if none found and False otherwise"""

        def check_pin(pin):
            if isinstance(pin.from_, Terminal):
                if pin.from_.to_ is not pin or pin.from_ not in self.inputs:
                    return True
            elif isinstance(pin.from_, CircuitElementBase):
                if pin not in pin.from_.outputs or (pin.from_ not in self.gates and pin.from_ not in self.nets):
                    print(pin.from_.label, pin.to_.label)
                    return True
            if isinstance(pin.to_, Terminal):
                if pin.to_.from_ is not pin or pin.to_ not in self.outputs:
                    return True
            elif isinstance(pin.to_, CircuitElementBase):
                if pin not in pin.to_.inputs or (pin.to_ not in self.gates and pin.to_ not in self.nets):
                    print(pin.to_.label, pin.from_.label)
                    return True

        pins = [*self.pins()]
        for gate in self.gates:
            pins.extend(gate.outputs)
        for net in self.nets:
            if len(net.inputs) > 1:
                return False
            pins.extend(net.outputs)
        for inp in self.inputs:
            pins.append(inp.to_)

        for inp in self.inputs:
            if inp.to_.to_ not in self.nets:
                return False
        for gate in self.gates:
            out, = gate.outputs
            if out.to_ not in self.nets:
                return False

        return not any(map(check_pin, pins))

    def _attach_hanging(self):
        for net in self.nets:
            if net.driver is None:
                PinBase(label=net.label, from_=self.__void, to_=net, parent=self)

    def _merge_consecutive_nets(self) -> None:
        """Merge directly connected nets into one"""
        deleted = set()
        for net in self.nets:
            if net in deleted:
                continue
            pins = []
            name = net.label
            while isinstance(net.driver.from_, Net):
                driver = net.driver.from_
                pins.extend(net.outputs)
                net.driver.detach()
                net.outputs = []
                deleted.add(net)
                net = driver
            if isinstance(net.driver.from_, Terminal):
                net.label = name
            for pin in pins:
                net.attach_output_pin(pin)
        self.nets.remove(*deleted)

    # endregion

    def destroy(self):
        """Delete all interconnections

        Call this function before you delete all references to circuit instance to allow garbage collection
        """
        self.gates.clear()
        self.nets.clear()
        self.inputs.clear()
        self.outputs.clear()
        for gate in self.__gates:
            [*map(gate.detach_input_pin, list(gate.inputs))]
            [*map(gate.detach_output_pin, list(gate.outputs))]
        for net in self.__nets:
            net.detach_input_pin(net.driver)
            [*map(net.detach_output_pin, list(net.outputs))]
        for inp in self.__inputs:
            inp.to_.from_ = None
            inp.to_ = None
        for out in self.__outputs:
            out.from_.to_ = None
            out.from_ = None
