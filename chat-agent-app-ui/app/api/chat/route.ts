import { UIMessage } from "ai";

// Backend configuration
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    const { messages }: { messages: UIMessage[] } = await req.json();
    
    // Transform messages to backend format
    const backendMessages = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    // Prepare request for backend
    const backendRequest = {
      messages: backendMessages,
      workflow: "pubmed_research", // Default workflow
      session_id: null // Could be enhanced to include session management
    };

    // Call backend streaming endpoint
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(backendRequest),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status} ${response.statusText}`);
    }

    // Create a ReadableStream to transform backend response to AI SDK format
    const transformStream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter(line => line.trim());

            for (const line of lines) {
              try {
                // Backend sends JSON chunks like: {"type": "text", "content": "word"}
                const parsed = JSON.parse(line);
                if (parsed.type === "text" && parsed.content) {
                  // Transform to AI SDK format
                  const aiSDKChunk = `0:"${parsed.content.replace(/"/g, '\\"')}"\n`;
                  controller.enqueue(new TextEncoder().encode(aiSDKChunk));
                }
              } catch (parseError) {
                // If not JSON, treat as plain text
                const aiSDKChunk = `0:"${line.replace(/"/g, '\\"')}"\n`;
                controller.enqueue(new TextEncoder().encode(aiSDKChunk));
              }
            }
          }
        } catch (error) {
          console.error("Stream processing error:", error);
          controller.error(error);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(transformStream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });

  } catch (error) {
    console.error("API route error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
