import type { WebSocket } from "@fastify/websocket"

const sendMessageToClients = (clients: Set<WebSocket>, msg: string) => {
    for (const client of clients) {
        if (client.readyState === client.OPEN) {
            client.send(JSON.stringify({ type: msg }))
        }
    }
}

export default sendMessageToClients