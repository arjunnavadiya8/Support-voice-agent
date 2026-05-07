import { Message } from "../hooks/useVoiceAgent";

const LANG_LABELS: Record<string, string> = { en: "EN", hi: "HI", gu: "GU" };

export function Transcript({ messages }: { messages: Message[] }) {
    if (messages.length === 0) {
        return null;
    }

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                gap: 14,
                padding: "16px 12px",
                maxHeight: "300px",
                overflowY: "auto",
                border: "1px solid #1E293B",
                borderRadius: 12,
                background: "#090D16",
                marginTop: 20,
                width: "100%",
            }}
        >
            {messages.map((m, i) => (
                <div
                    key={i}
                    style={{
                        alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                        maxWidth: "85%",
                        background: m.role === "user" ? "#2563EB" : "#1E293B",
                        borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                        padding: "12px 16px",
                        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                        animation: "fadeIn 0.3s ease",
                    }}
                >
                    <div
                        style={{
                            fontSize: 10,
                            color: m.role === "user" ? "#93C5FD" : "#94A3B8",
                            fontWeight: 600,
                            marginBottom: 4,
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                        }}
                    >
                        {m.role === "user" ? "You" : "Suvit Agent"}
                        {m.language && ` · ${LANG_LABELS[m.language] ?? m.language}`}
                    </div>
                    <div
                        style={{
                            fontSize: 14,
                            color: "#FFFFFF",
                            lineHeight: 1.5,
                            fontWeight: 400,
                        }}
                    >
                        {m.text}
                    </div>
                </div>
            ))}
        </div>
    );
}