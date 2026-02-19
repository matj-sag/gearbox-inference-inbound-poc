export function onInput(inputs, context) {
  return [
    inputs[0].properties.temperature.value,
    inputs[0].properties.torque.value,
    { value: true, properties: { "input": [inputs[0].properties.rawValues.values] } }];
}
