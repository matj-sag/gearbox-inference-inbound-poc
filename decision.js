export function onInput(inputs, context) {
    const raw = String(inputs[0].value || "[]");
    const temp = Number(inputs[1].value || 0);
    const torque = Number(inputs[2].value || 0);
    const cls = Number(inputs[3].value || 0);
    const conf = Number(inputs[4].value || 0);

    const labelMap = {
        0: "normal",
        1: "early_bearing_wear",
        2: "gear_tooth_damage",
        3: "misalignment"
    };

    const label = labelMap[cls] || "unknown";

    const good = (cls === 0);

    if (good) {
        return [temp, torque, good];
    }

    // Construct LLM prompt
    const prompt = `
Wind turbine gearbox anomaly detected.
Model classification: ${label}
Confidence: ${conf.toFixed(3)}
Raw features: ${raw}
Temperature: ${temp}
Torque: ${torque}

Provide a likely root cause, probable secondary effects, and clear recommended diagnostic steps for a field engineer.
    `.trim();

    return [temp, torque, good, prompt];
}
