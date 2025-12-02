import { onInput as fn1 } from "./decoding.js";
import { onInput as fn2 } from "./decision.js";

class Base64 {
	// from uint8array to string
	static encode(str) {
		return Buffer.from(str).toString("base64");
	}
	// from string to uint8array
	static decode(arr) {
		return Uint8Array.from(Buffer.from(arr, "base64"));
	}
}
// put Base64 into global scope for fn1 to access
globalThis.Base64 = Base64;

function b64(str) {
  return Buffer.from(str, "utf8").toString("base64");
}

function decodeB64(str) {
  return Buffer.from(str, "base64").toString("utf8");
}

function runTest() {
  const rawPayload = JSON.stringify([[42, 50, 0.15, 0, 123.4,42, 50, 0.15, 0, 123.4]]);
  const encoded = b64(rawPayload);

  const fn1_out = fn1([encoded], {});
  console.log("fn1 output:", fn1_out);

  const fn2_in = [fn1_out[0], fn1_out[1], fn1_out[2], 2, 0.81];   // pretend wiring to second stage
  const fn2_out = fn2(fn2_in, {});
  console.log("fn2 output:", fn2_out);

  console.log("Decoded fn1 payload:", decodeB64(fn1_out[0] || ""));
}

runTest();
