// /tradehabit-backend/mentor/chat-ui/src/lib/runAssistant.ts
import { openai, ASSISTANT_ID, TOOL_RUNNER_BASE_URL } from "./openai";

type ToolCall = {
  id: string;
  type: "function";
  function: { name: string; arguments: string };
};

// ---------- tiny retry/backoff for OpenAI 429s ----------
async function withRetry<T>(fn: () => Promise<T>, tries = 3) {
  let delay = 800;
  let lastErr: any;
  for (let i = 0; i < tries; i++) {
    try {
      return await fn();
    } catch (e: any) {
      lastErr = e;
      const status = e?.status || e?.response?.status;
      const msg = e?.message || e?.response?.data || "";
      const rateLimited = status === 429 || /rate limit|Too Many Requests/i.test(msg);
      if (!rateLimited) break;
      await new Promise((r) => setTimeout(r, delay));
      delay *= 2;
    }
  }
  throw lastErr || new Error("Retry limit reached");
}

// ---------- helper: safe POST JSON to tool_runner ----------
async function postJSON(url: string, payload: any): Promise<{ ok: boolean; data: any }> {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload ?? {})
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, data };
  } catch (e: any) {
    return {
      ok: false,
      data: { status: "ERROR", message: `tool_runner fetch failed: ${e?.message || String(e)}` }
    };
  }
}

// ---------- tool runner bridge ----------
async function callToolRunner(name: string, args: any, userText?: string) {
  // get_summary_data is always tiny
  if (name === "get_summary_data") {
    const { data } = await postJSON(`${TOOL_RUNNER_BASE_URL}/get_summary_data`, {});
    return data;
  }

  // get_endpoint_data with safe defaults and fallback to keys_only
  if (name === "get_endpoint_data") {
    const safeArgs: any = { ...(args || {}) };
  
    // Guard against full-file dumps unless paging a top-level array
    const callerSpecifiedKeysOnly = Object.prototype.hasOwnProperty.call(safeArgs, "keys_only");
    if (!callerSpecifiedKeysOnly && !safeArgs.top) safeArgs.keys_only = true;
  
    // If paging a big array and no projection specified, keep it lean
    if (safeArgs.top === "trades" && !Array.isArray(safeArgs.fields)) {
      safeArgs.fields = ["id", "entryTime", "symbol", "pnl", "mistakes"];
    }
  
    // Clamp page size
    const reqSize = Number(safeArgs.max_results);
    safeArgs.max_results = Number.isFinite(reqSize) && reqSize > 0 ? Math.min(reqSize, 10) : 10;
  
    // First attempt
    let { ok, data } = await postJSON(`${TOOL_RUNNER_BASE_URL}/get_endpoint_data`, safeArgs);
  
    // If the server errored (bad `top`, etc.) → fallback to keys_only
    if (!ok) {
      ({ data } = await postJSON(`${TOOL_RUNNER_BASE_URL}/get_endpoint_data`, {
        name: safeArgs.name,
        keys_only: true
      }));
      return data;
    }
  
    // If we defaulted to keys_only and the payload looks scalar-only (no arrays),
    // auto-fetch the full snapshot so Franklin can read actual values.
    const weDefaultedKeysOnly = !callerSpecifiedKeysOnly && !args?.top;
    const looksScalarOnly =
      data &&
      typeof data === "object" &&
      Array.isArray(data.keys) &&
      data.keys.length > 0 &&
      data.array_lengths &&
      Object.values(data.array_lengths).every((n: any) => typeof n === "number" && n === 0);
  
    if (weDefaultedKeysOnly && looksScalarOnly) {
      const full = await postJSON(`${TOOL_RUNNER_BASE_URL}/get_endpoint_data`, {
        name: safeArgs.name
        // no keys_only → full snapshot
      });
      return full.data;
    }
  
    return data;
  }
  

  // filter_trades
  if (name === "filter_trades") {
    const safe: any = { include_total: true, ...(args || {}) };

    // Strip placeholder 'any'
    if (Array.isArray(safe.mistakes)) {
      safe.mistakes = safe.mistakes.filter(
        (m: string) => (m || "").toLowerCase() !== "any"
      );
      if (safe.mistakes.length === 0) delete safe.mistakes;
    }

    // Default projection
    if (!Array.isArray(safe.fields)) {
      safe.fields = ["id", "entryTime", "symbol", "pnl", "mistakes"];
    }

    // Clamp page size
    const reqSize = Number(safe.max_results);
    safe.max_results = Number.isFinite(reqSize) && reqSize > 0 ? Math.min(reqSize, 10) : 10;

    const { data } = await postJSON(`${TOOL_RUNNER_BASE_URL}/filter_trades`, safe);
    return data;
  }

  // filter_losses
  if (name === "filter_losses") {
    const safe: any = { include_total: true, ...(args || {}) };

    // Default projection
    if (!Array.isArray(safe.fields)) {
      safe.fields = ["exitOrderId", "entryTime", "pointsLost", "symbol", "side", "hasMistake"];
    }

    // Optional nudge for “worst/biggest/largest/max loss”
    const txt = (typeof userText === "string" ? userText : "").toLowerCase();
    if (!safe.extrema && /(?:worst|biggest|largest|max(?:imum)?)[\s-]*(?:loss)?/.test(txt)) {
      safe.extrema = { field: "pointsLost", mode: "max" };
    }

    // Clamp page size
    const reqSize = Number(safe.max_results);
    safe.max_results = Number.isFinite(reqSize) && reqSize > 0 ? Math.min(reqSize, 10) : 10;

    const { data } = await postJSON(`${TOOL_RUNNER_BASE_URL}/filter_losses`, safe);
    return data;
  }

  return { error: `Unknown tool: ${name}` };
}

export async function runAssistantTurn({
  threadId,
  userText
}: {
  threadId?: string;
  userText: string;
}) {
  // 1) Create or reuse thread
  const thread =
    threadId ? { id: threadId } : await withRetry(() => openai.beta.threads.create());

  // 2) Add user message
  await withRetry(() =>
    openai.beta.threads.messages.create(thread.id, {
      role: "user",
      content: userText
    })
  );

  // 3) Create run
  let run = await withRetry(() =>
    openai.beta.threads.runs.create(thread.id, {
      assistant_id: ASSISTANT_ID
    })
  );

  // 4) Poll loop (handles tool calls and completion)
  while (true) {
    run = await withRetry(() =>
      openai.beta.threads.runs.retrieve(thread.id, run.id)
    );

    if (run.status === "requires_action") {
      const toolCalls = (run.required_action?.submit_tool_outputs?.tool_calls || []) as ToolCall[];

      const outputs = await Promise.all(
        toolCalls.map(async (tc) => {
          const args = JSON.parse(tc.function.arguments || "{}");
          // console.log("🔧 tool call ->", tc.function.name, "args:", args);
          const result = await callToolRunner(tc.function.name, args, userText);
          return { tool_call_id: tc.id, output: JSON.stringify(result) };
        })
      );

      await withRetry(() =>
        openai.beta.threads.runs.submitToolOutputs(thread.id, run.id, {
          tool_outputs: outputs
        })
      );

      continue; // keep polling
    }

    if (run.status === "completed") {
      const msgs = await withRetry(() =>
        openai.beta.threads.messages.list(thread.id, { limit: 1, order: "desc" })
      );
      const latest = msgs.data[0];
      const text =
        latest?.content?.[0]?.type === "text"
          ? latest.content[0].text.value
          : "";
      return { threadId: thread.id, text };
    }

    if (["failed", "cancelled", "expired"].includes(run.status as string)) {
      throw new Error(`Run ended with status: ${run.status}`);
    }

    // small wait to avoid rate limits
    await new Promise((r) => setTimeout(r, 600));
  }
}
