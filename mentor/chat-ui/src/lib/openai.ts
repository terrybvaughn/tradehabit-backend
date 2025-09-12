import OpenAI from "openai";

export const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export const ASSISTANT_ID = process.env.ASSISTANT_ID as string;
export const TOOL_RUNNER_BASE_URL = process.env.TOOL_RUNNER_BASE_URL as string;

if (!process.env.OPENAI_API_KEY) throw new Error("Missing OPENAI_API_KEY");
if (!ASSISTANT_ID) throw new Error("Missing ASSISTANT_ID env var");
if (!TOOL_RUNNER_BASE_URL) throw new Error("Missing TOOL_RUNNER_BASE_URL env var");