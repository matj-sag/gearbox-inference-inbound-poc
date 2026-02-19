export function onInput(inputs, context) {
  const temp = inputs[0].value;
  const torque = inputs[1].value;
  const clss = inputs[2].properties["class"];
  const confidence = inputs[2].properties["confidence"];

  const labelMap = {
    0: "normal",
    1: "early_bearing_wear",
    2: "gear_tooth_damage",
    3: "misalignment"
  }

  const label = labelMap[clss] || "unknown";

  const good = (clss === 0);

  if (good) {
    return [temp, torque, good];
  }

  const prompt = `
Wind turbine gearbox anomaly detected.
Model classification: ${label}
Confidence: ${confidence.toFixed(3)}

Temperature: ${temp}
Torque: ${torque}

Provide a likely root cause, probable secondary effects, and clear recommended diagnostic steps for a field engineer.
`.trim();

  return [temp, torque, good, prompt];
}
