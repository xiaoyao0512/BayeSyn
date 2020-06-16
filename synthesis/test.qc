qubits 3
x q0
x q1
h q0
toffoli q1, q2, q0
toffoli q1, q0, q2
toffoli q2, q0, q1
toffoli q0, q1, q2
h q2
h q0
toffoli q2, q1, q0
h q2
measure q0
measure q1

display
