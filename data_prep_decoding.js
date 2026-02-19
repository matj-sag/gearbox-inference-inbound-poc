export function onMessage(msg, context)
{
  // Read 10 floats (32-bit each = 4 bytes) from the binary payload
  const dataView = new DataView(msg.payload.buffer, msg.payload.byteOffset, msg.payload.byteLength);
  
  const values =  [];
  for (let i = 0; i < 10; i++) {
    // Read each float at position i * 4 bytes
    values.push(dataView.getFloat32(i * 4, false));
  }
  
  // Extract temperature and torque (the last two values)
  const temperature = values[8];
  const torque = values[9];
  
  // Create a Cumulocity event with the data
  return [{
    cumulocityType: "event",
    externalSource: [{
      externalId: msg.clientID,
      type: "c8y_Serial"
    }],
    payload: {
      type: "ai_InferenceInput",
      text: "AI inference input data received",
      time: msg.time,
      temperature: {
        value: temperature
      },
      torque: {
        value: torque
      },
      rawValues: {
        values: values
      }
    }
  }];
}
