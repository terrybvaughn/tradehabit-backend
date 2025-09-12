import { NextResponse } from "next/server";
import { runAssistantTurn } from "@/src/lib/runAssistant";

export async function POST(req: Request) {
  try {
    const { message, threadId } = await req.json();
    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: "Missing 'message'" }, { status: 400 });
    }

    const result = await runAssistantTurn({ threadId, userText: message });
    return NextResponse.json(result);
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || "Unknown error" }, { status: 500 });
  }
}