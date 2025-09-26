// /tradehabit-backend/mentor/chat-ui/src/lib/runAssistant.ts
import { openai, ASSISTANT_ID, TOOL_RUNNER_BASE_URL } from "./openai";

type ToolCall = {
  id: string;
  type: "function";
  function: { name: string; arguments: string };
};

// --- tiny retry/backoff for 429s and blips ---
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

// --- tool runner bridge ---
async function callToolRunner(name: string, args: any, userText?: string) {
  // get_summary_data is always tiny
  if (name === "get_summary_data") {
    const res = await fetch(`${TOOL_RUNNER_BASE_URL}/get_summary_data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      if (!res.ok) throw new Error(`${json.error || "tool_error"}: ${json.detail || "unknown error"}`);
      return json;
    } catch (e) {
      if (!res.ok) throw new Error(`tool_http_${res.status}: ${text.slice(0, 200)}`);
      throw new Error(`tool_response_not_json: ${text.slice(0, 200)}`);
    }
  }

  // get_endpoint_data with safe defaults and fallback to keys_only
  if (name === "get_endpoint_data") {
    const safeArgs: any = { ...(args || {}) };

    // Normalize param: server expects `name` (not topic)
    if (safeArgs.topic && !safeArgs.name) {
      safeArgs.name = safeArgs.topic;
      delete safeArgs.topic;
    }

    if (!("keys_only" in safeArgs) && !safeArgs.top) safeArgs.keys_only = true;

    if (safeArgs.top === "trades" && !Array.isArray(safeArgs.fields)) {
      safeArgs.fields = ["id", "entryTime", "symbol", "pnl", "mistakes"];
    }

    const req = Number(safeArgs.max_results);
    safeArgs.max_results = Number.isFinite(req) && req > 0 ? Math.min(req, 50) : 10;

    let res = await fetch(`${TOOL_RUNNER_BASE_URL}/get_endpoint_data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(safeArgs)
    });
    let text = await res.text();
    try {
      let json = JSON.parse(text);
      if (!res.ok) {
        // Attempt fallback only if not ok
        const fallback = { name: safeArgs.name, keys_only: true };
        const res2 = await fetch(`${TOOL_RUNNER_BASE_URL}/get_endpoint_data`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(fallback)
        });
        const text2 = await res2.text();
        try {
          const json2 = JSON.parse(text2);
          if (!res2.ok) throw new Error(`${json2.error || "tool_error"}: ${json2.detail || "unknown error"}`);
          return json2;
        } catch (e2) {
          if (!res2.ok) throw new Error(`tool_http_${res2.status}: ${text2.slice(0, 200)}`);
          throw new Error(`tool_response_not_json: ${text2.slice(0, 200)}`);
        }
      }
      return json;
    } catch (e) {
      if (!res.ok) throw new Error(`tool_http_${res.status}: ${text.slice(0, 200)}`);
      throw new Error(`tool_response_not_json: ${text.slice(0, 200)}`);
    }
  }

  // filter_trades
  if (name === "filter_trades") {
    const safe: any = { include_total: true, ...(args || {}) };

    if (Array.isArray(safe.mistakes)) {
      safe.mistakes = safe.mistakes.filter(
        (m: string) => (m || "").toLowerCase() !== "any"
      );
      if (safe.mistakes.length === 0) delete safe.mistakes;
    }

    if (!Array.isArray(safe.fields)) {
      safe.fields = ["id", "entryTime", "symbol", "pnl", "mistakes"];
    }

    const req = Number(safe.max_results);
    safe.max_results = Number.isFinite(req) && req > 0 ? Math.min(req, 50) : 10;

    const res = await fetch(`${TOOL_RUNNER_BASE_URL}/filter_trades`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(safe)
    });
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      if (!res.ok) throw new Error(`${json.error || "tool_error"}: ${json.detail || "unknown error"}`);
      return json;
    } catch (e) {
      if (!res.ok) throw new Error(`tool_http_${res.status}: ${text.slice(0, 200)}`);
      throw new Error(`tool_response_not_json: ${text.slice(0, 200)}`);
    }
  }

  // filter_losses
  if (name === "filter_losses") {
    const safe: any = { include_total: true, ...(args || {}) };

    if (!Array.isArray(safe.fields)) {
      safe.fields = [
        "exitOrderId",
        "entryTime",
        "pointsLost",
        "symbol",
        "side",
        "hasMistake"
      ];
    }

    const txt = (typeof userText === "string" ? userText : "").toLowerCase();

    // Gate extrema (single-row) behind singular intent only.
    // Examples that SHOULD trigger extrema: "the worst loss", "largest loss", "max loss", "single worst loss"
    // Examples that SHOULD NOT trigger extrema: "worst losses", "101 worst losses", "top N biggest losses"
    const pluralLosses = /\blosses\b/.test(txt);
    const singularWorstLoss = /\b(?:the\s+)?(?:worst|biggest|largest|max(?:imum)?)\s+loss\b/.test(txt);
    const explicitSingle = /\b(?:single|one|1)\b/.test(txt);
    const requested = Number((safe as any).max_results);
    const wantsSingle = (Number.isFinite(requested) && requested === 1) || (!Number.isFinite(requested) && (explicitSingle || singularWorstLoss));

    if (!safe.extrema && wantsSingle && !pluralLosses) {
      safe.extrema = { field: "pointsLost", mode: "max" };
    } else {
      // For list requests, ensure deterministic ordering when asking for "worst/biggest/largest" plurals
      if (!safe.sort_by) safe.sort_by = "pointsLost";
      if (!safe.sort_dir) safe.sort_dir = "desc";
    }

    const req = Number(safe.max_results);
    safe.max_results = Number.isFinite(req) && req > 0 ? Math.min(req, 50) : 10;

    const res = await fetch(`${TOOL_RUNNER_BASE_URL}/filter_losses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(safe)
    });
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      if (!res.ok) throw new Error(`${json.error || "tool_error"}: ${json.detail || "unknown error"}`);
      return json;
    } catch (e) {
      if (!res.ok) throw new Error(`tool_http_${res.status}: ${text.slice(0, 200)}`);
      throw new Error(`tool_response_not_json: ${text.slice(0, 200)}`);
    }
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
  const thread =
    threadId ? { id: threadId } : await withRetry(() => openai.beta.threads.create());

  await withRetry(() =>
    openai.beta.threads.messages.create(thread.id, {
      role: "user",
      content: userText
    })
  );

  let run = await withRetry(() =>
    openai.beta.threads.runs.create(thread.id, {
      assistant_id: ASSISTANT_ID
    })
  );

  while (true) {
    run = await withRetry(() =>
      openai.beta.threads.runs.retrieve(thread.id, run.id)
    );

    if (run.status === "requires_action") {
      const toolCalls = (run.required_action?.submit_tool_outputs?.tool_calls ||
        []) as ToolCall[];

      const outputs = await Promise.all(
        toolCalls.map(async (tc) => {
          const args = JSON.parse(tc.function.arguments || "{}");
          const result = await callToolRunner(tc.function.name, args, userText);
          return { tool_call_id: tc.id, output: JSON.stringify(result) };
        })
      );

      await withRetry(() =>
        openai.beta.threads.runs.submitToolOutputs(thread.id, run.id, {
          tool_outputs: outputs
        })
      );

      continue;
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
      const errMsg = run.last_error?.message || "Unknown error";
      const errCode = run.last_error?.code || "no_code";
      // Instead of throwing, return a conversational error payload
      return {
        threadId: thread.id,
        text: `⚠️ Assistant run ended with status: ${run.status}\nError code: ${errCode}\nDetails: ${errMsg}`
      };
    }

    await new Promise((r) => setTimeout(r, 600));
  }
}
