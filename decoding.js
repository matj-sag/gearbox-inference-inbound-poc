export function onInput(inputs, context) {
    // input[0] = base64 string
	 console.log("decoding.js onInput called with inputs:", inputs);
    const bin = Base64.decode(inputs[0]);
	console.log("Decoded binary data:", bin.length);

    if (bin.length < 40) {
        // 10 float32 values expected
        return [];
    }

    const dv = new DataView(bin.buffer);
    const values = [];
    for (let i = 0; i < 10; i++) {
        values.push(dv.getFloat32(i * 4, false));
    }

    // Prepare outputs for ONNX and second JS
    const temp = values[8];
    const torque = values[9];

    return [
        JSON.stringify(values), // out0 → ONNX input
        temp,                   // out1
        torque,                 // out2
    ];
}
