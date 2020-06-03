qubits 3
x q0
x q1
h q0
h q2
h q1
toffoli q2, q0, q1
toffoli q1, q2, q0
toffoli q0, q1, q2
h q0
h q2
h q1
toffoli q1, q2, q0
measure q0
measure q1

display
